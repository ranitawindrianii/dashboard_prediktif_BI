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

# Proyek ini berhasil untuk :
1. Merancang data pipeline analitik untuk mendukung risk early warning terhadap topik
2. Mengintegrasikan faktor PESTLE sebagai dasar analisis risiko
3. Menyediakan analisis tren dan indikasi risiko berbasis data historis
4. Menghasilkan dashboard analitik yang mudah diinterpretasikan
5. Mengevaluasi kesiapan data untuk analitik prediktif
6. Menguji kelayakan penggunaan teknologi OLAP dan time-series forecasting 

# Tools/OSS yang Digunakan:
1. Apache Pinot (untuk OLAP real-time)
2. Polars (untuk manipulasi data efisien)
3. Streamlit (tampilan visual dashboard)
4. Virtual Machine : Oracle Virtual Machine
5. OS : Ubuntu 24.04

# Tujuan Proyek : 
1. Mengotomatiskan aliran data berita menjadi sinyal risiko keamanan pangan
2. Membangun risk mart harian berbasis PESTLE
3. Menyediakan dashboard prediktif
4. Menguji kemampuan Apache Pinot sebagai OLAP engine untuk pipeline near-real-time
5. Menyusun prototipe Early Warning System berbasis berita

# Komponen Utama
🔹 Scraper Republika
    Mengambil berita & menghasilkan article_metadata.csv., keyword_search.csv dan search_result.csv

🔹 Apache Pinot
    Digunakan sebagai OLAP storage:
        Tabel artikel

🔹 Polars Pipeline
    Script Python besar yang melakukan:
    Normalisasi tanggal
    Pembersihan teks
    Pengayaan PESTLE
    Penyusunan risk score
    Penyusunan mart harian

🔹 Cron + Shell Script
    Mengorkestrasi pipeline agar berjalan otomatis tiap hari

🔹 Streamlit Dashboard
    Menampilkan:
        Risk score per PESTLE
        Tren harian
        Forecast

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
     streamlit run step_5_dashboard_streamlit.py

# Tantangan saat Implementasi 
  Tantangan Teknis
  1. Format tanggal tidak konsisten dari Republika
     Diselesaikan dengan rules Polars .str.to_date() + fallback.
  2. Pinot tidak menerima schema backward incompatible
     Diselesaikan dengan membuat schema baru
  3. Scraper menghasilkan row sama 
     Tambah incremental scraping
     Gunakan cutoff timestamp dari Pinot
  4. CSV tidak support nested data
     Diselesaikan dengan konten.list.join(" ").
  5. Dashboard forecasting butuh data lebih panjang dan banyak

# Perkembangan Mingguan Project (Week 9–Week 16)
  Terdapat pada folder laporan per minggu dan laporan akhir
  https://drive.google.com/drive/folders/11UAe6r-M54BhjTCCr-qev0bf0N47dKa4?usp=sharing
  
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
