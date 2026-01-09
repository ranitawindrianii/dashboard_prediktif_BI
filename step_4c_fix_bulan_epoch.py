# step_4c_fix_bulan_epoch.py
import pandas as pd
from datetime import datetime
import os

# Path file CSV
csv_path = "lakehouse/gold/famine_dashboard.csv"

# Load data
df = pd.read_csv(csv_path)

# Jika kolom 'bulan' kosong, isi dengan default (misalnya Desember 2025)
default_date = datetime(2025, 12, 1)
default_epoch = int(default_date.timestamp() * 1000)

# Isi nilai kosong dengan default epoch millis
df["bulan"] = df["bulan"].fillna(default_epoch).astype(int)

# Simpan ulang
df.to_csv(csv_path, index=False)
print(f"Kolom 'bulan' sudah diisi dengan epoch millis: {default_epoch}")
