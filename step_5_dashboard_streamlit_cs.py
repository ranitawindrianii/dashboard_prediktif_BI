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
st.markdown("Data diambil dari file **CSV** di folder `gold/`.")

# -------------------------------
# Fungsi load data dari folder gold
# -------------------------------
@st.cache_data
def load_csv_data(folder="/home/pinot/project_root/lakehouse/gold/"):
    files = glob.glob(os.path.join(folder, "*.csv"))
    if not files:
        st.error("Tidak ada file CSV ditemukan di folder gold/")
        return pd.DataFrame()
    dfs = [pd.read_csv(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

# -------------------------------
# Load data
# -------------------------------
df = load_csv_data("/home/pinot/project_root/lakehouse/gold/")
if "bulan" in df.columns:
    try:
        # Konversi dari epoch milidetik ke datetime
        df["bulan"] = pd.to_datetime(df["bulan"], unit="ms")
    except Exception as e:
        st.warning(f"Gagal konversi kolom 'bulan': {e}")

if not df.empty:
    st.subheader("📑 Data mentah")
    st.dataframe(df.head(20))

    # -------------------------------
    # Ringkasan statistik
    # -------------------------------
    st.subheader("📈 Ringkasan Statistik")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Jumlah Kategori", df["kategori"].nunique() if "kategori" in df.columns else 0)
        st.metric("Jumlah Bulan Tercatat", df["bulan"].nunique() if "bulan" in df.columns else 0)

    with col2:
        st.metric("Total Berita", int(df["jumlah_berita"].sum()) if "jumlah_berita" in df.columns else 0)
        st.metric("Rata-rata Panjang Artikel", f"{df['rata_panjang_artikel'].mean():.2f}" if "rata_panjang_artikel" in df.columns else "-")

    with col3:
        st.metric("Bulan Terbaru", df["bulan"].max().strftime("%Y-%m") if "bulan" in df.columns and pd.api.types.is_datetime64_any_dtype(df["bulan"]) else "-")
        st.metric("Bulan Terlama", df["bulan"].min().strftime("%Y-%m") if "bulan" in df.columns and pd.api.types.is_datetime64_any_dtype(df["bulan"]) else "-")


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

    kategori_list = df["kategori"].unique().tolist()
    selected_kategori = st.sidebar.multiselect(
        "Pilih kategori:",
        options=kategori_list,
        default=kategori_list,
        help="Pilih satu atau lebih kategori untuk menampilkan data terkait."
    )

    bulan_list = df["bulan"].dt.strftime("%Y-%m").unique().tolist() if "bulan" in df.columns else []
    selected_bulan = st.sidebar.selectbox(
        "Pilih bulan:",
        options=bulan_list,
        index=0
    )

    # -------------------------------
    # Informasi tambahan di sidebar
    # -------------------------------
    st.sidebar.markdown("---")  # garis pemisah

    st.sidebar.markdown("""
    ### ℹ️ Tentang Dashboard
    - 📊 **Topik:** Prediksi & Analisis Ketahanan Pangan  
    - 📰 **Sumber Data:** Berita dari [Republika](https://www.republika.co.id/) dengan kata kunci beragam terkait ketahanan pangan  
    - 👩‍💻 **Dibuat oleh:** Ranita Windriani — 202022510006  
    """)

    if "prediksi_ketahanan" not in df.columns:
        #st.warning("Kolom 'prediksi_ketahanan' belum tersedia. Menambahkan dummy prediksi untuk simulasi.")
        df["prediksi_ketahanan"] = df["jumlah_berita"] / df["jumlah_berita"].max()  # contoh normalisasi

    # -------------------------------
    # Simulasi sederhana prediksi bulan berikutnya
    # -------------------------------
    st.subheader("🔮 Simulasi Prediksi Sederhana Bulan Berikutnya")

    if "prediksi_ketahanan" in df.columns:
        # Rule sederhana: naik 5% dari nilai sekarang
        df["prediksi_next_month"] = df["prediksi_ketahanan"] * 1.05

        # Tampilkan tabel simulasi
        st.dataframe(df[["kategori", "bulan", "prediksi_ketahanan", "prediksi_next_month"]].head(20))

        # Visualisasi simulasi
        fig_sim = px.bar(
            df,
            x="kategori",
            y=["prediksi_ketahanan", "prediksi_next_month"],
            barmode="group",
            title="Perbandingan Prediksi Saat Ini vs Simulasi Bulan Depan"
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    # -------------------------------
    # Visualisasi kategori (rata-rata prediksi)
    # -------------------------------
    st.subheader("🍽️ Rata-rata Prediksi Ketahanan per Kategori")

    if "kategori" in df.columns and "prediksi_ketahanan" in df.columns:
        avg_df = df.groupby("kategori")["prediksi_ketahanan"].mean().reset_index()
        fig_cat = px.bar(
            avg_df,
            x="kategori",
            y="prediksi_ketahanan",
            color="kategori",
            title="Rata-rata Prediksi Ketahanan per Kategori"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    if "kategori" in df.columns:
        filtered_df = df[df["kategori"].isin(selected_kategori)]
        st.subheader("📑 Data Terfilter")
        st.dataframe(filtered_df.head(20))

else:
    st.warning("Data kosong. Pastikan ada file CSV di folder gold/.")


