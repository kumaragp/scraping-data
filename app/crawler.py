import requests
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

sources = {
    "detik": "https://www.detik.com/terpopuler/news",
    "cnn": "https://www.cnnindonesia.com/nasional/politik",
    "kompas": "https://indeks.kompas.com/terpopuler",
}

def crawl_news():
    print(f"\n[{datetime.now()}] Memulai proses crawling...")

    headers = {"User-Agent": "Mozilla/5.0"}

    for source_name, url in sources.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            articles_found = 0

            # Detik
            if source_name == "detik":
                for item in soup.find_all("article"):
                    title = None
                    link = None
                    category = None

                    title_tag = item.find("h3") or item.find("h2") or item.find("h1")
                    link_tag = item.find("a", href=True)

                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if link_tag:
                        link = str(link_tag["href"])

                    if not title or not link:
                        continue

                    doc = {
                        "source": source_name,
                        "title": title,
                        "url": link,
                        "category": category,
                        "timestamp": datetime.now().isoformat()
                    }

                    supabase.table("news").upsert(
                        doc,
                        on_conflict="url"
                    ).execute()

                    articles_found += 1
                    print(f"✔ Artikel Detik: {title}")

            # CNN
            elif source_name == "cnn":
                for item in soup.find_all("article"):
                    title = None
                    link = None
                    category = None

                    title_tag = item.find("h2") or item.find("h3") or item.find("h1")
                    link_tag = item.find("a", href=True)
                    category_tag = item.find("span", class_="text-xs text-cnn_red")

                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if link_tag:
                        link = str(link_tag["href"])
                        if not link.startswith("http"):
                            link = "https://www.cnnindonesia.com" + link
                    if category_tag:
                        category = category_tag.get_text(strip=True)

                    if not title or not link:
                        continue

                    doc = {
                        "source": source_name,
                        "title": title,
                        "url": link,
                        "category": category,
                        "timestamp": datetime.now().isoformat()
                    }

                    supabase.table("news").upsert(
                        doc,
                        on_conflict="url"
                    ).execute()

                    articles_found += 1
                    print(f"✔ Artikel CNN: {title}")

            # Kompas
            elif source_name == "kompas":
                for item in soup.find_all("div", class_="articleItem"):
                    title = None
                    link = None
                    category = None

                    title_tag = item.find("h2", class_="articleTitle")
                    link_tag = item.find("a", class_="article-link", href=True)

                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if link_tag:
                        link = str(link_tag["href"])

                    if not title or not link:
                        continue

                    doc = {
                        "source": source_name,
                        "title": title,
                        "url": link,
                        "category": category,
                        "timestamp": datetime.now().isoformat()
                    }

                    supabase.table("news").upsert(
                        doc,
                        on_conflict="url"
                    ).execute()

                    articles_found += 1
                    print(f"✔ Artikel Kompas: {title}")

            print(f"Sumber {source_name}: {articles_found} artikel berhasil disimpan.\n")

        except requests.exceptions.RequestException as e:
            print(f"❌ Gagal mengakses {source_name}: {e}")

    print(f"[{datetime.now()}] Crawling selesai.\n")

schedule.every(10).minutes.do(crawl_news)

crawl_news()

while True:
    schedule.run_pending()
    time.sleep(5)