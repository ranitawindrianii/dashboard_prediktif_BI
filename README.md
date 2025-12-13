# dashboard_prediktif_BI
Dashboard Prediktif Ketahanan Pangan dengan Lakehouse. Solusi visualisasi data untuk memprediksi kekurangan gizi berdasarkan faktor PESTLE, menggunakan lakehouse untuk menyimpan data historis dan teknologi ML untuk forecasting. Apache Pinot (untuk OLAP real-time) dan Polars (untuk manipulasi data efisien).

# Judul Proyek
Dashboard Prediktif Ketahanan Pangan dengan Lakehouse menggunakan Apache Pinot, Polars, and Streamlit

# Daftar Isi
1. Deskripsi Proyek
2. Tujuan Pengembangan
3. Arsitektur Sistem
4. Komponen Utama
5. Alur Pipeline End-to-End
6. Penjelasan Skrip Utama
7. Orkestrasi Pipeline (Cron & Shell Script)
8. Dashboard Prediktif
9. Tantangan Teknis
10. Perkembangan Mingguan (Week 9–Week 14)
11. Rencana Pengembangan Selanjutnya

# Deskripsi Proyek :
Solusi visualisasi data untuk memprediksi kekurangan gizi berdasarkan faktor PESTLE, menggunakan lakehouse untuk menyimpan data historis dan teknologi ML untuk forecasting.

# Tools/OSS yang Digunakan:
1. Apache Pinot (untuk OLAP real-time)
2. Polars (untuk manipulasi data efisien)
3. Streamlit (tampilan visual dashboard)
4. Virtual Machine : Oracle Virtual Machine
5. OS : Ubuntu 24.04

# Tujuan : 
1. Mengotomatiskan aliran data berita menjadi sinyal risiko keamanan pangan.
2. Membangun risk mart harian berbasis PESTLE.
3. Menyediakan dashboard prediktif bagi analis atau pimpinan.
4. Menguji kemampuan Apache Pinot sebagai OLAP engine untuk pipeline near-real-time.
5. Menyusun prototipe Early Warning System berbasis berita.

# Arsitektur Sistem: 
                +-----------------------+
                |   Republika Website   |
                +-----------+-----------+
                            |
                            | Scraping (Python)
                            v
                     article_metadata.csv
                            |
                            v
 +------------------ Apache Pinot -------------------+
 |  Table: republika_articles_v2 (raw articles)      |
 +----------------------------+----------------------+
                              |
                              | Polars Enrichment Pipeline
                              v
                 articles_enriched_pestle.csv
                              |
                              v
                    build_risk_mart.py (Polars)
                              |
                              v
              food_ingestion_risk_auto.csv (Risk Mart)
                              |
                              v
 +------------------ Apache Pinot -------------------+
 | Table: food_ingestion_risk_auto (daily mart)      |
 +----------------------------+----------------------+
                              |
                              v
                   Streamlit Predictive Dashboard

# Komponen Utama
🔹 Scraper Republika
    Mengambil berita & menghasilkan article_metadata.csv.

🔹 Apache Pinot
    Digunakan sebagai OLAP storage:
        Tabel artikel (republika_articles_v2)
        Tabel risk mart (food_ingestion_risk_auto)

🔹 Polars Pipeline
    Script Python besar yang melakukan:
    Normalisasi tanggal
    Pembersihan teks
    Pengayaan PESTLE
    Penyusunan risk score
    Penyusunan mart harian

🔹 Cron + Shell Script
    Mengorkestrasi pipeline agar berjalan otomatis tiap hari.

🔹 Streamlit Dashboard
    Menampilkan:
        Risk score per PESTLE
        Tren harian
        Forecast 7–30 hari (Prophet)
