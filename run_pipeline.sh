#!/bin/bash
# ============================================
# 🚀 Pipeline Otomatis Ketahanan Pangan
# Dibuat oleh: Ranita Windriani - 202022510006
# ============================================

# Aktifkan environment Python (opsional)
# source /home/pinot/venv/bin/activate

# Set folder project
PROJECT_ROOT="/home/pinot/project_root/lakehouse"

echo "============================================"
echo "📂 Mulai pipeline otomatis ketahanan pangan"
echo "Waktu: $(date)"
echo "============================================"

# 1. Bronze ingest
echo "🪨 Step 1: Bronze ingest..."
python3 $PROJECT_ROOT/step_1_bronze_ingest.py

# 2. Silver transform
echo "⚙️ Step 2: Silver transform..."
python3 $PROJECT_ROOT/step_2_silver_transform.py

# 3. Gold aggregate
echo "🥇 Step 3: Gold aggregate..."
python3 $PROJECT_ROOT/step_3_gold_aggregate.py

# 4a. Export gold to CSV
echo "📄 Step 4a: Export gold to CSV..."
python3 $PROJECT_ROOT/step_4a_gold_to_csv.py

# 4b. Convert time to epoch millis
echo "⏳ Step 4b: Convert bulan ke epoch millis..."
python3 $PROJECT_ROOT/step_4b_epoch_millis.py

# 4c. Fix bulan epoch consistency
echo "🛠️ Step 4c: Fix bulan epoch..."
python3 $PROJECT_ROOT/step_4c_fix_bulan_epoch.py

# 5. ML pipeline (forecasting + clustering)
echo "🤖 Step 5: ML pipeline..."
python3 /home/pinot/project_root/ml_pipeline.py

# 6. ML forecasting modular
echo "📈 Step 6: ML forecasting modular..."
python3 /home/pinot/project_root/ml_forecasting.py

echo "============================================"
echo "✅ Pipeline selesai dijalankan"
echo "Output tersedia di folder gold/ dan Pinot"
echo "============================================"
