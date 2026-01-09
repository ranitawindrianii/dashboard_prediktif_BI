# step_2_silver_transform.py
import polars as pl
import os
from datetime import datetime

BRONZE = "lakehouse/bronze/article_metadata.csv"
SILVER_DIR = "lakehouse/silver"
os.makedirs(SILVER_DIR, exist_ok=True)

# Helper: parse tanggal
def parse_waktu(w):
    if w is None or len(w.strip()) == 0:
        return None
    w = w.replace("WIB", "").strip()
    for fmt in ["%d %B %Y %H:%M", "%d %B %Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.strptime(w, fmt)
        except:
            continue
    return None

# Load bronze
df = pl.read_csv(BRONZE, ignore_errors=True)

# Normalisasi tanggal
if "waktu_terbit" in df.columns:
    df = df.with_columns(
        pl.col("waktu_terbit").map_elements(parse_waktu).cast(pl.Datetime).alias("waktu_terbit_parsed")
    )

# Hilangkan duplikasi URL
if "url" in df.columns:
    df = df.unique(subset=["url"])

# Kategori umum (Produksi, Risiko Iklim, Kebijakan, Sosial, Ketahanan Pangan)
def categorize(row):
    text = " ".join([
        str(row.get("judul", "")),
        str(row.get("konten", "")),
        str(row.get("keyword", "")),
    ]).lower()
    if any(k in text for k in ["padi", "panen", "gabah", "pupuk", "produksi"]):
        return "Produksi"
    if any(k in text for k in ["el nino", "la nina", "kekeringan", "banjir", "iklim", "cuaca ekstrem"]):
        return "Risiko Iklim"
    if any(k in text for k in ["subsidi", "program", "bulog", "kementerian"]):
        return "Kebijakan"
    if any(k in text for k in ["stunting", "gizi buruk", "malnutrisi"]):
        return "Sosial"
    return "Ketahanan Pangan"

df = df.with_columns(
    pl.struct(df.columns).map_elements(categorize).alias("kategori")
)

# 🔑 Tambahan: PESTLE keyword matching
PESTLE_KEYWORDS = {
    "Political": ["bulog", "kementerian", "subsidi", "program pangan", "regulasi", "uu pangan"],
    "Economic": ["harga beras", "inflasi", "daya beli", "kemiskinan", "ekonomi", "impor"],
    "Social": ["stunting", "gizi buruk", "malnutrisi", "kesehatan masyarakat"],
    "Technological": ["inovasi pertanian", "pupuk teknologi", "logistik", "distribusi modern"],
    "Legal": ["uu pangan", "peraturan", "hukum", "regulasi impor"],
    "Environmental": ["el nino", "la nina", "banjir", "kekeringan", "perubahan iklim", "cuaca ekstrem"]
}

def categorize_pestle(text: str) -> str:
    text = text.lower()
    for factor, keywords in PESTLE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return factor
    return "Uncategorized"

df = df.with_columns(
    pl.struct(["judul","konten"]).map_elements(
        lambda row: categorize_pestle(row["judul"] + " " + row["konten"])
    ).alias("pestle_factor")
)

# Panjang konten
if "konten" in df.columns:
    df = df.with_columns(
        pl.col("konten").str.len_bytes().alias("panjang_konten")
    )

# Simpan ke Silver
SILVER_PATH = os.path.join(SILVER_DIR, "articles_with_pestle.parquet")
df.write_parquet(SILVER_PATH)
print(f"Silver saved: {SILVER_PATH}")
