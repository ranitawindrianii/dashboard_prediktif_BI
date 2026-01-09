# step_3_gold_aggregate.py
import polars as pl
import os

SILVER_PATH = "lakehouse/silver/articles_with_pestle.parquet"
GOLD_DIR = "lakehouse/gold"
os.makedirs(GOLD_DIR, exist_ok=True)

df = pl.read_parquet(SILVER_PATH)

# Bulan trunc
df = df.with_columns(
    pl.col("waktu_terbit_parsed").dt.truncate("1mo").alias("bulan")
)

# Agregasi per kategori dan PESTLE
gold = df.group_by(["kategori","pestle_factor","bulan"]).agg([
    pl.len().alias("jumlah_berita"),
    pl.mean("panjang_konten").alias("rata_panjang_artikel")
])

GOLD_PATH = os.path.join(GOLD_DIR, "famine_dashboard.parquet")
gold.write_parquet(GOLD_PATH)
print(f"Gold saved: {GOLD_PATH}")
