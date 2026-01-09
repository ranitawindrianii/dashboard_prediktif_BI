import streamlit as st
import pandas as pd
import glob
import os
import plotly.express as px

# -------------------------------
# Konfigurasi dasar dashboard
# -------------------------------
st.set_page_config(
    page_title="Dashboard Prediksi Ketahanan Pangan",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Prediksi Ketahanan Pangan")
st.markdown("Data diambil dari file **Parquet** di folder `gold/`.")

# -------------------------------
# Fungsi load data dari folder gold
# -------------------------------
@st.cache_data
def load_parquet_data(folder="gold"):
    files = glob.glob(os.path.join(folder, "*.parquet"))
    if not files:
        st.error("Tidak ada file Parquet ditemukan di folder gold/")
        return pd.DataFrame()
    dfs = [pd.read_parquet(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

# -------------------------------
# Load data
# -------------------------------
df = load_parquet_data("gold")

if not df.empty:
    st.subheader("📑 Data mentah")
    st.dataframe(df.head(20))

    # -------------------------------
    # Ringkasan statistik
    # -------------------------------
    st.subheader("📈 Ringkasan Statistik")
    st.write(df.describe(include="all"))

    # -------------------------------
    # Visualisasi tren prediksi
    # -------------------------------
    if "bulan" in df.columns and "prediksi_ketahanan" in df.columns:
        st.subheader("📉 Tren Prediksi Ketahanan Pangan per Bulan")
        fig = px.line(
            df,
            x="bulan",
            y="prediksi_ketahanan",
            title="Prediksi Ketahanan Pangan",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Visualisasi kategori
    # -------------------------------
    if "kategori" in df.columns and "prediksi_ketahanan" in df.columns:
        st.subheader("🍽️ Distribusi Prediksi per Kategori")
        fig2 = px.bar(
            df.groupby("kategori")["prediksi_ketahanan"].mean().reset_index(),
            x="kategori",
            y="prediksi_ketahanan",
            title="Rata-rata Prediksi Ketahanan per Kategori",
            color="kategori"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # Filter interaktif
    # -------------------------------
    st.sidebar.header("🔍 Filter Data")
    kategori_list = df["kategori"].unique().tolist() if "kategori" in df.columns else []
    selected_kategori = st.sidebar.multiselect("Pilih kategori:", kategori_list, default=kategori_list)

    if "kategori" in df.columns:
        filtered_df = df[df["kategori"].isin(selected_kategori)]
        st.subheader("📑 Data Terfilter")
        st.dataframe(filtered_df.head(20))

else:
    st.warning("Data kosong. Pastikan ada file Parquet di folder gold/.")


