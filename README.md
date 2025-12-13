# dashboard_prediktif_BI
Project ini merupakan Dashboard Prediktif Ketahanan Pangan dengan Lakehouse. Solusi visualisasi data untuk memprediksi kekurangan gizi berdasarkan faktor PESTLE, menggunakan lakehouse untuk menyimpan data historis dan teknologi ML untuk forecasting. Tools yang digunakan pada project ini ialah Apache Pinot untuk OLAP real-time, Polars untuk manipulasi data efisien, dan Streamlit untuk visualisasi dashboard.

# Judul Proyek
Dashboard Prediktif Ketahanan Pangan dengan Lakehouse menggunakan Apache Pinot, Polars, and Streamlit

# Daftar Isi
1. Deskripsi Proyek
2. Tools/OSS yang digunakan
3. Tujuan Proyek
4. Arsitektur Sistem
5. Komponen Utama
6. Alur Pipeline End-to-End
7. Penjelasan Skrip Utama
8. Gambaran Arsitektur Sistem
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

# Tujuan Proyek : 
1. Mengotomatiskan aliran data berita menjadi sinyal risiko keamanan pangan.
2. Membangun risk mart harian berbasis PESTLE.
3. Menyediakan dashboard prediktif.
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

# Alur Pipeline End-to-End
1. Scraping Republika
    Output: article_metadata.csv
2. Ingest artikel ke Pinot
    Menggunakan ingestion job YAML (republika_articles_v2_job.yml).
3. Enrichment dengan Polars
    Script: pestle_from_republika.py
    Output: articles_enriched_pestle.csv
4. Build Risk Mart
    Script: build_risk_mart.py
    Output: food_ingestion_risk_auto.csv
5. Ingest Risk Mart ke Pinot
    Table: food_ingestion_risk_auto_OFFLINE
6. Dashboard Predictive Streamlit
    Query langsung dari Pinot menggunakan pinotdb.

# Penjelasan Skrip Utama
  **pestle_from_republika.py**
  1. Load data artikel dari Pinot
  2. Normalisasi tanggal (mengatasi format yang rusak)
  3. Kombinasi teks judul + konten
  4. Pemberian label PESTLE berdasarkan rule-based keywords
  5. Perhitungan panjang konten
  6. Output CSV enriched

  **build_risk_mart.py**
  1. Grouping per published_date × pestle_factor
  2. Menghitung: article_count, sentiment_index, risk_score
  3. Normalisasi & scaling
  4. Output CSV risk mart

  **run_pipeline.sh**
  1. Pipeline otomatis: Aktifkan venv, Jalankan (TODO) scraper,Copy CSV → Pinot,Jalankan ingestion artikel,Jalankan Polars enrichment,Jalankan pembentukan risk mart,Copy risk mart ke Pinot,Jalankan ingestion mart,Berjalan otomatis via cron job.

# Gambaran Arsitektur Sistem
  1. Orkestrasi Pipeline (Cron & Shell Script)
     Fungsi:
      Berjalan otomatis jam 02:00 setiap hari
      Memperbarui seluruh pipeline end-to-end
      Log disimpan di pipeline.log
  3. Dashboard Prediktif
     Dashboard menampilkan:
       Pilihan filter PESTLE
       Grafik risk score
       Grafik article count
       Grafik sentiment index
       High-risk days
       Forecast risk menggunakan Prophet
       Confidence interval
       Insight otomatis dari forecast
     Dashboard diakses dengan script berikut :
     streamlit run app.py

# Tantangan saat Implementasi 
  Tantangan Teknis
  1. Format tanggal tidak konsisten dari Republika
     Diselesaikan dengan rules Polars .str.to_date() + fallback.
  2. Pinot tidak menerima schema backward incompatible
     Diselesaikan dengan membuat schema baru food_ingestion_risk_auto.
  3. Scraper menghasilkan row sama (belum incremental)
     Tambah incremental scraping
     Gunakan cutoff timestamp dari Pinot
     Simpan state last_article_id
  4. CSV tidak support nested data
     Diselesaikan dengan konten.list.join(" ").
  5. Dashboard forecasting butuh data lebih panjang
     Saat ini hanya berjalan untuk faktor dengan > 3 data points. Dikarenakan data yang didapat hanya sedikit.

# Perkembangan Mingguan Project (Week 9–Week 16)
  **Week 9 — Setup & Environment**
  1. Instalasi VM dan Instalasi OS Ubuntu
  2. Instalasi Bootstrap Apache Pinot menggunakan Docker
  3. Setup Polars environment untuk data pipeline

  **Week 10 — Ingestion Raw Data**
  1. Pengujian scraping awal berita Republika
  2. Membuat folder struktur proyek untuk pipeline
  3. Membuat schema & table Pinot (republika_articles_v2)
  4. Menguji ingestion CSV melalui Pinot jobs
  5. Perbaikan schema dan validasi kolom
  6. Mengatasi error time column & schema mismatch

  **Week 11 — PESTLE Enrichment Pipeline**
  1. Membangun script Polars untuk parsing artikel
  2. Normalisasi tanggal, handling invalid date formats
  3. Rule-based PESTLE classifier
  4. Penggabungan konten + judul
  5. Cleaning konten multi-value (list)

  **Week 12 — Risk Mart Construction**
  1. Definisi article_count, sentiment_index, risk_score
  2. Implementasi normalisasi (min-max scaling)
  3. Menyusun tabel mart harian
  4. Menyusun ingestion job untuk food_ingestion_risk_auto
  5. Upload risk mart ke Pinot
  
  **Week 13 — Dashboard Predictive Streamlit**
  1. Membangun UI dasar Streamlit
  2. Query Pinot menggunakan pinotdb
  3. Visualisasi multi-chart: risk score, article count, sentiment index
  4. Menambahkan threshold-based alert
  5. Menambahkan forecasting Prophet + insight otomatis
  6. Menangani error data < 10 titik

  **Week 14 — Pipeline Orchestration**
  1. Menyusun script run_pipeline.sh
  2. Mengautomasi pipeline dari scraping - ingestion - enrichment - mart - ingestion
  3. Setup cron job (daily run at 02:00)
  4. Logging pipeline
  5. Validasi pipeline end-to-end

  **Week 15 — Final Project**
  1. Menyusun laporan akhir
  2. Menyusun roadmap untuk next-phase improvement

# Permasalahan saat Percobaan
Permasalahan yang ditemukan:
1. Struktur HTML halaman tidak konsisten
2. Beberapa halaman gagal diakses
3. Perubahan format tanggal pada data yang diamnbil
   
# Rencana Pengembangan Selanjutnya
1. Incremental Scraper (High Priority)
   Agar row tidak repetitif dan mengambil hanya artikel baru berdasarkan timestamp Pinot
2. Sentiment Analysis
   Mengganti sentiment dummy dan menghasilkan risk score yang lebih akurat
3. PESTLE Classifier berbasis ML
   Mengganti rule-based dengan model supervised dan Mengurangi false label
4. Refinement Risk Score
   Integrasi severity term weighting, Anomaly detection, Early-warning index
5. Model Multivariate Forecasting
   Prophet + exogenous variable,LSTM small model
6. System Hardening
   CI/CD, Error notification, atau Metadata logging (run history)
