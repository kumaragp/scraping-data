
# Scrapping Data

Kode program ini digunakan untuk melakukan web scraping pada website berita Indonesia dengan tujuan mengambil data informasi berita secara otomatis. Data yang diambil umumnya meliputi sumber berita, judul berita, url, kategori berita, dan waktu pengambilan. Adapun website berita yang diambil datanya adalah sebagai berikut:
- CNN
- NEWS
- KOMPAS

## Fitur
- Pengambilan data secara interval
- Terhubung dengan cloud server
- Pre-processing menggunakan spark
- Visualisasi data

## Teknologi
- Python
- Supabase
- Databricks Free Version
- Docker

## Panduan Instalasi
Untuk menjalankan kode program di atas, ikuti langkah-langkah berikut secara berurutan agar proses web scraping dapat berjalan dengan baik:

1. Clone Repository
~~~ bash
git clone https://github.com/kumaragp/scraping-data.git
~~~

2. Pastikan sudah membuat akun supabase dan databricks

3. Masuk ke supabase dan buat project baru

4. Buat tabel database dengan konfigurasi sebagai berikut:

| Columns Name | Type     | Deffault Value  | Primary |
| :----------- | :------- | :-------------- | :------ |
| id           | int8     | NULL            |   II    |
| source       | text     | ''::text        |   IN    |
| title        | text     | NULL            | IN & IU |
| url          | text     | NULL            | IN & IU |
| category     | text     | NULL            |   IN    |
| timestamps   | timstamp | NULL            |   IN    |

- **II = Is Identify**
- **IU = Is Unique**
- **IN = Is Nullable**

5. Buat notebook baru di databricks pada menu Workspace

6. Salin seluruh kode dari visualization.ipynb dan tempelkan ke notebook Databricks

7. Jalankan perintah pada terminal code editor untuk menjalankan proses crawling, lalu pastikan data tersimpan di cloud storage Supabase.
~~~ bash
docker compose up --build
~~~
8. Download kamus berikut ini [NRC_LEXICON](https://drive.google.com/file/d/1P_KTZP7MQJH_4nSM-7u1bPI-n8Tx491I/view?usp=drive_link)

9. Jika sudah berhasil di download pindahkan file ke Data ingestion -> Upload files to a volume -> sesuikan directorinya masing-masing, setelah itu copy_path dan letakkan di **nrc_path** yang ada pada shell databricks

9. Setelah data tersedia, pilih Run All pada Databricks untuk menjalankan seluruh kode program

## Authors

- [@kumaragp](https://github.com/kumaragp)
- [@anthonydewantoro](https://github.com/Anthony091104)