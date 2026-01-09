# save as step_4b_epoch_millis.py
import polars as pl

p = "lakehouse/gold/famine_dashboard.csv"
df = pl.read_csv(p).with_columns(
    (pl.col("bulan").str.strptime(pl.Datetime, fmt="%Y-%m-%d %H:%M:%S", strict=False).dt.timestamp().cast(pl.Int64) * 1000).alias("bulan_epoch")
).drop("bulan").rename({"bulan_epoch": "bulan"})
df.write_csv(p)
print("Updated CSV with epoch millis for 'bulan'")

#contoh bulan : 1764522000000 perlu diubah
