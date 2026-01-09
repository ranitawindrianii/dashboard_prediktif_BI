import requests
import pandas as pd
from prophet import Prophet
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# 1. Query data dari Pinot
query = {
    "sql": "SELECT kategori, pestle_factor, bulan, jumlah_berita, rata_panjang_artikel FROM famine_dashboard"
}
resp = requests.post("http://localhost:8099/query", json=query)
rows = resp.json()["resultTable"]["rows"]

df = pd.DataFrame(rows, columns=["kategori","pestle_factor","bulan","jumlah_berita","rata_panjang_artikel"])
df["bulan"] = pd.to_datetime(df["bulan"], unit="ms")

print("Data sample:")
print(df.head())

# 2. Forecasting jumlah_berita per bulan (Prophet)
df_prophet = df.groupby("bulan")["jumlah_berita"].sum().reset_index()
df_prophet.columns = ["ds","y"]

model = Prophet()
model.fit(df_prophet)
future = model.make_future_dataframe(periods=6, freq="M")
forecast = model.predict(future)

# Plot forecast
fig1 = model.plot(forecast)
plt.title("Forecast jumlah_berita per bulan")
plt.show()

# 3. Clustering kategori berdasarkan metrik
X = df[["jumlah_berita","rata_panjang_artikel"]]
X_scaled = StandardScaler().fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(X_scaled)

print("\nCluster assignment sample:")
print(df[["kategori","pestle_factor","jumlah_berita","rata_panjang_artikel","cluster"]].head())

# 4. Visualisasi cluster
plt.figure(figsize=(8,6))
plt.scatter(df["jumlah_berita"], df["rata_panjang_artikel"], c=df["cluster"], cmap="viridis")
plt.xlabel("Jumlah Berita")
plt.ylabel("Rata Panjang Artikel")
plt.title("Clustering kategori berdasarkan metrik")
plt.show()
