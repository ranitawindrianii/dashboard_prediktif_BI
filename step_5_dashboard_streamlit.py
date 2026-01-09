# step_5_dashboard_streamlit_forecast.py
import os
import json
import requests
import pandas as pd
import streamlit as st

BROKER_URL = os.getenv("PINOT_BROKER_URL", "http://localhost:9000/query/sql")
GOLD_DIR = os.getenv("GOLD_DIR", "gold")

PESTLE_OPTIONS = ["Political", "Economic", "Social", "Technological", "Legal", "Environmental"]

st.set_page_config(page_title="Dashboard Ketahanan Pangan", page_icon="🌾", layout="wide")
st.title("🌾 Dashboard Prediktif Ketahanan Pangan (Berita)")

mode = st.radio("Pilih mode", ["Historis (Kategori)", "Historis (PESTLE)", "Forecasting (PESTLE)"])
limit = st.slider("Limit rows", 10, 5000, 200)

def query_pinot(sql):
    try:
        payload = {"sql": sql}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(BROKER_URL, data=json.dumps(payload), headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        cols = data.get("resultTable", {}).get("dataSchema", {}).get("columnNames", [])
        rows = data.get("resultTable", {}).get("rows", [])
        return pd.DataFrame(rows, columns=cols)
    except Exception as e:
        st.error(f"Gagal konek ke Broker: {e}")
        return pd.DataFrame()

if mode == "Historis (Kategori)":
    selected = st.selectbox("Kategori", ["Ketahanan Pangan", "Produksi", "Risiko", "Distribusi", "Harga"])
    sql = f"""
    SELECT kategori,
           millisToTimestamp(bulan) AS bulan,
           jumlah_berita,
           rata_panjang_kalimat
    FROM famine_dashboard
    WHERE kategori = '{selected}'
    ORDER BY bulan
    LIMIT {limit}
    """
    df = query_pinot(sql)
    if not df.empty:
        df["bulan"] = pd.to_datetime(df["bulan"], errors="coerce")
        st.subheader(f"Historis jumlah berita - {selected}")
        st.line_chart(df.set_index("bulan")[["jumlah_berita"]], use_container_width=True)
        st.dataframe(df, use_container_width=True)

elif mode == "Historis (PESTLE)":
    selected = st.selectbox("PESTLE Factor", PESTLE_OPTIONS)
    sql = f"""
    SELECT pestle,
           millisToTimestamp(bulan) AS bulan,
           SUM(jumlah_berita) AS jumlah_berita,
           AVG(rata_panjang_kalimat) AS rata_panjang_kalimat
    FROM famine_dashboard
    WHERE pestle = '{selected}'
    GROUP BY pestle, bulan
    ORDER BY bulan
    LIMIT {limit}
    """
    df = query_pinot(sql)
    if not df.empty:
        df["bulan"] = pd.to_datetime(df["bulan"], errors="coerce")
        st.subheader(f"Historis jumlah berita - {selected}")
        st.line_chart(df.set_index("bulan")[["jumlah_berita"]], use_container_width=True)
        st.dataframe(df, use_container_width=True)

else:  # Forecasting (PESTLE)
    selected = st.selectbox("PESTLE Factor (Forecast)", PESTLE_OPTIONS)
    forecast_path = os.path.join(GOLD_DIR, f"forecast_{selected.lower()}.csv")
    if not os.path.exists(forecast_path):
        st.warning(f"File forecast belum ditemukan: {forecast_path}. Jalankan ml_forecasting.py terlebih dulu.")
    else:
        df = pd.read_csv(forecast_path)
        # Expect columns: ds, yhat, yhat_lower, yhat_upper, pestle
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
        df = df.dropna(subset=["ds", "yhat"])
        st.subheader(f"Forecast jumlah berita - {selected}")
        st.line_chart(df.set_index("ds")[["yhat"]], use_container_width=True)
        st.area_chart(df.set_index("ds")[["yhat_lower", "yhat_upper"]], use_container_width=True)
        st.dataframe(df.tail(24), use_container_width=True)

st.caption("Jika koneksi Broker gagal, gunakan mode Forecasting (PESTLE) yang membaca prediksi dari Gold CSV.")
