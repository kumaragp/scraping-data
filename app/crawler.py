import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, errors
import schedule
import time
from datetime import datetime
import os

# Configurasi MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
DB_NAME = "news"
COLLECTION_NAME = "articles"

# Fungsi koneksi MongoDB dengan retry
def connect_mongo(uri, db_name, collection_name, max_retry=10, wait_sec=5):
    retry_count = 0
    while retry_count < max_retry:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client[db_name]
            collection = db[collection_name]
            print(f"✅ Connected to MongoDB at {uri}")
            return collection
        except Exception as e:
            retry_count += 1
            print(f"MongoDB belum siap, coba lagi ({retry_count}/{max_retry})... Error: {e}")
            time.sleep(wait_sec)
    print("❌ Gagal koneksi ke MongoDB setelah beberapa percobaan.")
    exit()

collection = connect_mongo(MONGO_URI, DB_NAME, COLLECTION_NAME)

# Daftar Sumber Berita
sources = {
    "detik": "https://www.detik.com/terpopuler/news",
    "cnn": "https://www.cnnindonesia.com/nasional/politik",
}

# Crawling
def crawl_news():
    print(f"\n[{datetime.now()}] Memulai proses crawling...")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for source_name, url in sources.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            articles_found = 0

            # Parsing khusus Detik
            if source_name == "detik":
                for item in soup.find_all("article"):
                    link_tag = item.find("a")
                    title_tag = item.find("h3") or item.find("h2") or item.find("h1")

                    title = title_tag.get_text(strip=True) if title_tag else None
                    link = link_tag["href"] if link_tag else None
                    category = None  # Detik tidak diambil category di contoh ini

                    if title and link and collection.count_documents({"url": link}) == 0:
                        doc = {
                            "source": source_name,
                            "title": title,
                            "url": link,
                            "category": category,
                            "timestamp": datetime.now()
                        }
                        collection.insert_one(doc)
                        articles_found += 1
                        print(f"✔ Artikel Detik disimpan: {title} ({link})")

            # Parsing khusus CNN
            elif source_name == "cnn":
                articles = soup.find_all("article")
                for item in articles:
                    link_tag = item.find("a", href=True)
                    title_tag = item.find("h2") or item.find("h3") or item.find("h1")
                    category_tag = item.find("span", class_="text-xs text-cnn_red")

                    if not link_tag or not title_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    link = link_tag["href"]
                    if not link.startswith("http"):
                        link = "https://www.cnnindonesia.com" + link
                    category = category_tag.get_text(strip=True) if category_tag else None

                    if collection.count_documents({"url": link}) == 0:
                        doc = {
                            "source": source_name,
                            "title": title,
                            "url": link,
                            "category": category,
                            "timestamp": datetime.now()
                        }
                        collection.insert_one(doc)
                        print(f"✔ Artikel CNN disimpan: {title} ({link})")

                print(f"Sumber {source_name}: {len(articles)} artikel ditemukan.\n")


        except requests.exceptions.RequestException as e:
            print(f"❌ Gagal mengakses {source_name}: {e}")
        except errors.PyMongoError as e:
            print(f"❌ Error MongoDB: {e}")

    print(f"[{datetime.now()}] Crawling selesai.\n")

# Penjadwawalan crawling setiap 30 detik
schedule.every(30).seconds.do(crawl_news)

# Jalankan pertama kali saat container start
crawl_news()  

# Loop scheduler
while True:
    schedule.run_pending()
    time.sleep(60)