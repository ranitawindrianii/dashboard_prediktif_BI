import os
import json
import argparse
import warnings
import requests
import pandas as pd
from prophet import Prophet

warnings.filterwarnings("ignore", category=FutureWarning)

BROKER_URL = os.getenv("PINOT_BROKER_URL", "http://localhost:8099/query")
GOLD_DIR = os.getenv("GOLD_DIR", "gold")
INPUT_CSV_FALLBACK = os.getenv("GOLD_INPUT_CSV", "gold_layer_famine_dashboard.csv")

PESTLE_ORDER = ["Political", "Economic", "Social", "Technological", "Legal", "Environmental"]

def fetch_from_pinot(limit=10000):
    query = f"""
    SELECT pestle_factor,
           millisToTimestamp(bulan) AS ds,
           SUM(jumlah_berita) AS y
    FROM famine_dashboard
    GROUP BY pestle_factor, millisToTimestamp(bulan)
    ORDER BY ds
    LIMIT {limit}
    """
    payload = {"sql": query}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(BROKER_URL, data=json.dumps(payload), headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    cols = data.get("resultTable", {}).get("dataSchema", {}).get("columnNames", [])
    rows = data.get("resultTable", {}).get("rows", [])
    df = pd.DataFrame(rows, columns=cols)

    # Pastikan kolom sesuai
    if "ds" not in df.columns or "y" not in df.columns or "pestle" not in df.columns:
        raise RuntimeError(f"Hasil query tidak sesuai, kolom: {cols}")

    # Normalisasi tipe data
    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["ds", "y", "pestle"])
    return df

def load_data(limit=10000):
    try:
        print(f"[INFO] Fetching from Pinot Broker: {BROKER_URL}")
        return fetch_from_pinot(limit=limit)
    except Exception as e:
        print(f"[WARN] Pinot fetch failed: {e}")
        if os.path.exists(INPUT_CSV_FALLBACK):
            print(f"[INFO] Using fallback CSV: {INPUT_CSV_FALLBACK}")
            df = pd.read_csv(INPUT_CSV_FALLBACK)
            if {"pestle", "bulan", "jumlah_berita"}.issubset(df.columns):
                df["ds"] = pd.to_datetime(df["bulan"], errors="coerce")
                df["y"] = pd.to_numeric(df["jumlah_berita"], errors="coerce")
            elif {"pestle", "ds", "y"}.issubset(df.columns):
                df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
                df["y"] = pd.to_numeric(df["y"], errors="coerce")
            else:
                raise ValueError("Fallback CSV harus punya kolom (pestle, bulan, jumlah_berita) atau (pestle, ds, y)")
            df = df.dropna(subset=["ds", "y", "pestle"])
            return df
        raise RuntimeError("Tidak ada data dari Pinot dan fallback CSV.")

def fit_prophet_for_factor(df_factor, factor, periods=6, freq="M"):
    df_factor = df_factor[["ds", "y"]].sort_values("ds")
    if len(df_factor) < 6 or df_factor["y"].fillna(0).sum() == 0:
        print(f"[WARN] Skip {factor}: data terlalu sedikit atau kosong.")
        return None
    model = Prophet(seasonality_mode="additive", yearly_seasonality=True)
    model.fit(df_factor)
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    preds = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    preds["pestle"] = factor
    return preds

def save_forecasts(all_preds):
    os.makedirs(GOLD_DIR, exist_ok=True)
    if not all_preds:
        print("[WARN] Tidak ada forecast yang dihasilkan.")
        return
    combined = pd.concat(all_preds, ignore_index=True)
    combined_out = os.path.join(GOLD_DIR, "forecast_all_pestle.csv")
    combined.to_csv(combined_out, index=False)
    print(f"[INFO] Saved {combined_out} ({len(combined)} rows)")
    for factor in combined["pestle"].unique():
        sub = combined[combined["pestle"] == factor]
        out_path = os.path.join(GOLD_DIR, f"forecast_{factor.lower()}.csv")
        sub.to_csv(out_path, index=False)
        print(f"[INFO] Saved {out_path} ({len(sub)} rows)")

def main():
    parser = argparse.ArgumentParser(description="PESTLE forecasting pipeline (Prophet)")
    parser.add_argument("--periods", type=int, default=6, help="Prediction horizon (months)")
    parser.add_argument("--freq", type=str, default="M", help="Frequency alias (e.g., M)")
    parser.add_argument("--limit", type=int, default=10000, help="Max rows to fetch")
    args = parser.parse_args()

    df = load_data(limit=args.limit)
    all_preds = []
    for factor in [f for f in PESTLE_ORDER if f in df["pestle"].unique()]:
        fdf = df[df["pestle"] == factor].copy()
        preds = fit_prophet_for_factor(fdf, factor, periods=args.periods, freq=args.freq)
        if preds is not None:
            all_preds.append(preds)
    save_forecasts(all_preds)

if __name__ == "__main__":
    main()
