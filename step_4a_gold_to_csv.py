# save as step_4a_gold_to_csv.py
import polars as pl

gold_parquet = "lakehouse/gold/famine_dashboard.parquet"
gold_csv = "lakehouse/gold/famine_dashboard.csv"

pl.read_parquet(gold_parquet).write_csv(gold_csv)
print(f"Converted to CSV: {gold_csv}")

