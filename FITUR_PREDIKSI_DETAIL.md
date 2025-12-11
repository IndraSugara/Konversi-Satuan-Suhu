# 🔮 Cara Kerja Fitur Prediksi Penjualan - Penjelasan Detail

## 📋 Daftar Isi
1. [Overview Sistem Prediksi](#overview-sistem-prediksi)
2. [Alur Kerja Lengkap](#alur-kerja-lengkap)
3. [Komponen Teknis](#komponen-teknis)
4. [Algoritma Facebook Prophet](#algoritma-facebook-prophet)
5. [Proses Training Model](#proses-training-model)
6. [Proses Prediksi](#proses-prediksi)
7. [Evaluasi Akurasi](#evaluasi-akurasi)
8. [Penyimpanan Hasil](#penyimpanan-hasil)
9. [Scheduler Otomatis](#scheduler-otomatis)
10. [Contoh Kasus Nyata](#contoh-kasus-nyata)

---

## 🎯 Overview Sistem Prediksi

### Apa yang Diprediksi?
**Target**: Total pendapatan penjualan (revenue) per hari untuk 30 hari ke depan

### Teknologi yang Digunakan:
- **Prophet**: Time series forecasting dari Facebook
- **Pandas**: Manipulasi data
- **NumPy**: Komputasi numerik
- **Scikit-learn**: Evaluasi model (MAE, RMSE, MAPE)

### Input Data:
```
Data historis transaksi 90 hari terakhir:
- Tanggal transaksi
- Total penjualan per hari
- Status transaksi (hanya yang 'completed')
```

### Output Prediksi:
```
Untuk setiap hari (30 hari ke depan):
- Prediksi revenue (predicted_revenue)
- Batas bawah (lower_bound) - skenario pesimis
- Batas atas (upper_bound) - skenario optimis
- Akurasi model (MAE, RMSE, MAPE)
```

---

## 🔄 Alur Kerja Lengkap

### Diagram Alur:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│  (Frontend - reports.js)                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 1. User klik "Prediksi Penjualan"
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              API REQUEST                                    │
│  GET /api/reports/sales-forecast                            │
│  Query params:                                              │
│  - historical_days=90  (data training)                      │
│  - forecast_days=30    (periode prediksi)                   │
│  - save=true           (simpan ke DB)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 2. Request masuk Report Service
                        ↓
┌─────────────────────────────────────────────────────────────┐
│            REPORT SERVICE (Flask)                           │
│  routes.py → get_sales_forecast()                           │
│                                                             │
│  Langkah:                                                   │
│  ✓ Validasi JWT token (admin only)                         │
│  ✓ Validasi parameter (min 7 hari)                         │
│  ✓ Panggil fungsi train_and_predict_sales()                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 3. Ambil data historis
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         DATABASE QUERY (MySQL)                              │
│  get_historical_sales_data(90 days)                         │
│                                                             │
│  SQL Query:                                                 │
│  SELECT DATE(created_at), SUM(total_amount)                 │
│  FROM transactions                                          │
│  WHERE created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)      │
│  AND status = 'completed'                                   │
│  GROUP BY DATE(created_at)                                  │
│  ORDER BY DATE(created_at)                                  │
│                                                             │
│  Result: Contoh 61 hari data                                │
│  2025-10-11: Rp 503.000                                     │
│  2025-10-12: Rp 471.000                                     │
│  ...                                                        │
│  2025-12-10: Rp 367.004                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 4. Convert ke DataFrame
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         PANDAS DATAFRAME                                    │
│  Format Prophet: {ds, y}                                    │
│                                                             │
│     ds          |    y                                      │
│  ──────────────────────────────                             │
│  2025-10-11    | 503000.00                                  │
│  2025-10-12    | 471000.00                                  │
│  2025-10-13    | 653000.00                                  │
│  ...           | ...                                        │
│  2025-12-10    | 367004.00                                  │
│                                                             │
│  Total: 61 rows                                             │
│  Mean: Rp 587.000                                           │
│  Std: Rp 183.000                                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 5. Train Prophet Model
                        ↓
┌─────────────────────────────────────────────────────────────┐
│      FACEBOOK PROPHET MODEL                                 │
│  train_and_predict_sales()                                  │
│                                                             │
│  Inisialisasi Model:                                        │
│  Prophet(                                                   │
│    daily_seasonality=False,      # Tidak ada pola harian   │
│    weekly_seasonality=True,      # Ada pola mingguan       │
│    yearly_seasonality=False,     # Data < 1 tahun          │
│    changepoint_prior_scale=0.5,  # Fleksibilitas tinggi    │
│    seasonality_prior_scale=10.0, # Kekuatan seasonality    │
│    interval_width=0.95,          # Confidence 95%          │
│    seasonality_mode='multiplicative' # Mode retail         │
│  )                                                          │
│                                                             │
│  Model belajar dari data:                                   │
│  ✓ Trend umum (naik/turun/stabil)                          │
│  ✓ Pola mingguan (weekend vs weekday)                      │
│  ✓ Changepoints (titik perubahan trend)                    │
│  ✓ Outliers & anomali                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 6. Fit model dengan data
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         MODEL TRAINING PROCESS                              │
│  model.fit(df)                                              │
│                                                             │
│  Proses Internal Prophet:                                   │
│  1. Dekomposisi data:                                       │
│     y(t) = trend(t) + seasonality(t) + holidays(t) + ε     │
│                                                             │
│  2. Identifikasi trend:                                     │
│     - Linear/logistic growth                                │
│     - Changepoints otomatis                                 │
│                                                             │
│  3. Deteksi seasonality:                                    │
│     - Fourier series untuk pola mingguan                    │
│     - Senin-Jumat vs Sabtu-Minggu                           │
│                                                             │
│  4. Fitting dengan Stan (MCMC):                             │
│     - Bayesian inference                                    │
│     - Uncertainty quantification                            │
│                                                             │
│  Log output:                                                │
│  [PROPHET] Training with 61 days of data                    │
│  [PROPHET] Revenue range: 334000 - 1037005                  │
│  [PROPHET] Revenue mean: 587430, std: 183290                │
│  Chain [1] start processing                                 │
│  Chain [1] done processing                                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 7. Generate future dates
                        ↓
┌─────────────────────────────────────────────────────────────┐
│      FUTURE DATAFRAME                                       │
│  model.make_future_dataframe(periods=30)                    │
│                                                             │
│  Membuat dataframe dengan:                                  │
│  - 61 hari historis (untuk evaluasi)                        │
│  - 30 hari masa depan (untuk prediksi)                      │
│  Total: 91 rows                                             │
│                                                             │
│     ds                                                      │
│  ──────────────                                             │
│  2025-10-11 (historis)                                      │
│  ...                                                        │
│  2025-12-10 (hari ini)                                      │
│  2025-12-11 (prediksi)                                      │
│  2025-12-12 (prediksi)                                      │
│  ...                                                        │
│  2026-01-09 (prediksi)                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 8. Predict
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         PREDICTION RESULT                                   │
│  forecast = model.predict(future)                           │
│                                                             │
│  Output columns (91 rows):                                  │
│  ds         | yhat      | yhat_lower | yhat_upper | trend  │
│  ─────────────────────────────────────────────────────────  │
│  2025-12-11 | 612.450   | 428.320    | 798.120    | 610.2  │
│  2025-12-12 | 634.780   | 449.560    | 821.340    | 612.5  │
│  2025-12-13 | 598.230   | 411.890    | 782.670    | 614.8  │
│  2025-12-14 | 711.450   | 524.320    | 895.230    | 617.1  │
│  2025-12-15 | 689.120   | 501.890    | 872.560    | 619.4  │
│  ... (30 hari)                                              │
│                                                             │
│  Komponen prediksi:                                         │
│  - yhat: Prediksi utama                                     │
│  - yhat_lower: Bound bawah (95% CI)                         │
│  - yhat_upper: Bound atas (95% CI)                          │
│  - trend: Komponen trend                                    │
│  - weekly: Komponen mingguan                                │
│  - multiplicative_terms: Efek multiplikatif                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 9. Extract prediksi 30 hari
                        ↓
┌─────────────────────────────────────────────────────────────┐
│      FILTER FUTURE PREDICTIONS                              │
│  predictions = forecast[...].tail(30)                       │
│                                                             │
│  Ambil hanya 30 hari ke depan:                              │
│  {                                                          │
│    'ds': '2025-12-11',                                      │
│    'yhat': 612450.00,                                       │
│    'yhat_lower': 428320.00,                                 │
│    'yhat_upper': 798120.00                                  │
│  }                                                          │
│  ... (29 hari lagi)                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 10. Evaluate accuracy
                        ↓
┌─────────────────────────────────────────────────────────────┐
│      ACCURACY EVALUATION                                    │
│  calculate_forecast_errors()                                │
│                                                             │
│  Bandingkan prediksi vs data aktual (61 hari historis):    │
│                                                             │
│  Actual values: [503000, 471000, 653000, ...]               │
│  Predicted values: [515340, 489230, 641780, ...]            │
│                                                             │
│  Hitung 3 metrik:                                           │
│                                                             │
│  1. MAE (Mean Absolute Error):                              │
│     = (1/n) × Σ|actual - predicted|                         │
│     = (1/61) × (12340 + 18230 + 11220 + ...)                │
│     = Rp 45.680                                             │
│     → Rata-rata selisih absolut                             │
│                                                             │
│  2. RMSE (Root Mean Squared Error):                         │
│     = √[(1/n) × Σ(actual - predicted)²]                     │
│     = √[(1/61) × (12340² + 18230² + ...)]                   │
│     = Rp 58.920                                             │
│     → Penalti lebih besar untuk error besar                 │
│                                                             │
│  3. MAPE (Mean Absolute Percentage Error):                  │
│     = (100/n) × Σ|(actual - predicted)/actual|             │
│     = (100/61) × (12340/503000 + 18230/471000 + ...)        │
│     = 8.24%                                                 │
│     → Akurasi dalam persentase                              │
│                                                             │
│  Interpretasi MAPE:                                         │
│  < 10%: Excellent ✅                                        │
│  10-20%: Good                                               │
│  20-50%: Reasonable                                         │
│  > 50%: Inaccurate ❌                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 11. Format response
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         JSON RESPONSE                                       │
│                                                             │
│  {                                                          │
│    "status": "success",                                     │
│    "forecast": [                                            │
│      {                                                      │
│        "date": "2025-12-11",                                │
│        "predicted_revenue": 612450.00,                      │
│        "lower_bound": 428320.00,                            │
│        "upper_bound": 798120.00                             │
│      },                                                     │
│      ... (29 hari lagi)                                     │
│    ],                                                       │
│    "accuracy_metrics": {                                    │
│      "mae": 45680.50,                                       │
│      "rmse": 58920.30,                                      │
│      "mape": 8.24                                           │
│    },                                                       │
│    "model_info": {                                          │
│      "training_days": 61,                                   │
│      "forecast_days": 30,                                   │
│      "training_start": "2025-10-11",                        │
│      "training_end": "2025-12-10"                           │
│    },                                                       │
│    "generated_at": "2025-12-10T23:45:12.000Z",              │
│    "saved_to_db": true                                      │
│  }                                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 12. Save to database (if save=true)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│       SAVE TO DATABASE                                      │
│  save_forecast_to_db()                                      │
│                                                             │
│  Table: sales_forecasts                                     │
│                                                             │
│  INSERT INTO sales_forecasts:                               │
│  - forecast_date: 2025-12-11                                │
│  - predicted_revenue: 612450.00                             │
│  - lower_bound: 428320.00                                   │
│  - upper_bound: 798120.00                                   │
│  - mae: 45680.50                                            │
│  - rmse: 58920.30                                           │
│  - mape: 8.24                                               │
│  - created_at: NOW()                                        │
│                                                             │
│  × 30 rows (untuk 30 hari prediksi)                         │
│                                                             │
│  Purpose: Riwayat prediksi untuk evaluasi nanti            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 13. Return ke frontend
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         FRONTEND VISUALIZATION                              │
│  displayForecast() - reports.js                             │
│                                                             │
│  1. Display Metrics:                                        │
│     MAE: Rp 45.680                                          │
│     RMSE: Rp 58.920                                         │
│     MAPE: 8.24% (Excellent)                                 │
│                                                             │
│  2. Chart.js Line Chart:                                    │
│     - Garis biru: Prediksi revenue                          │
│     - Garis hijau putus: Batas atas (optimis)               │
│     - Garis merah putus: Batas bawah (pesimis)              │
│     - Area shaded: Confidence interval                      │
│                                                             │
│  3. Table:                                                  │
│     Tanggal | Prediksi | MAPE | Created                     │
│     ─────────────────────────────────                       │
│     11 Des  | Rp 612K  | 8.2% | 10 Des 23:45               │
│     12 Des  | Rp 635K  | 8.2% | 10 Des 23:45               │
│     ...                                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Komponen Teknis

### 1. **Backend Service (Python Flask)**

**File**: `services/report-service/routes.py`

```python
# Endpoint utama
@report_bp.route('/sales-forecast', methods=['GET'])
@jwt_required()
def get_sales_forecast():
    # 1. Autentikasi admin
    # 2. Ambil parameter
    # 3. Panggil training function
    # 4. Format hasil
    # 5. Save ke database
    # 6. Return JSON
```

### 2. **Database (MySQL)**

**Tabel Input**: `transactions`
```sql
SELECT 
    DATE(created_at) as date,
    SUM(total_amount) as revenue
FROM transactions
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)
AND status = 'completed'
GROUP BY DATE(created_at)
```

**Tabel Output**: `sales_forecasts`
```sql
CREATE TABLE sales_forecasts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    forecast_date DATE NOT NULL,
    predicted_revenue DECIMAL(10,2),
    lower_bound DECIMAL(10,2),
    upper_bound DECIMAL(10,2),
    mae DECIMAL(10,2),
    rmse DECIMAL(10,2),
    mape DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. **Frontend (JavaScript)**

**File**: `frontend/js/reports.js`

```javascript
async function loadSalesForecast() {
    // 1. Get parameter dari form
    const historicalDays = 90;
    const forecastDays = 30;
    
    // 2. Call API
    const response = await apiRequest(
        `/api/reports/sales-forecast?historical_days=${historicalDays}&forecast_days=${forecastDays}`
    );
    
    // 3. Display hasil
    displayForecast(response);
}
```

---

## 🧠 Algoritma Facebook Prophet

### Konsep Dasar

Prophet adalah algoritma time series forecasting yang dikembangkan Facebook untuk:
- Data dengan pola musiman (seasonality)
- Data dengan trend
- Data dengan anomali/outliers
- Data dengan missing values

### Formula Prophet:

```
y(t) = g(t) + s(t) + h(t) + εt

Dimana:
- y(t) = nilai prediksi pada waktu t
- g(t) = trend (growth) - pola jangka panjang
- s(t) = seasonality - pola berulang (harian, mingguan, tahunan)
- h(t) = holidays - efek hari libur
- εt = error term (noise)
```

### Komponen yang Dipelajari:

#### 1. **Trend (g(t))**
```
Menangkap perubahan jangka panjang:
- Apakah penjualan naik?
- Apakah penjualan turun?
- Apakah stabil?

Contoh kedai kopi:
- Bulan pertama: Rp 15jt/bulan (masih baru)
- Bulan kedua: Rp 18jt/bulan (mulai ramai)
- Bulan ketiga: Rp 22jt/bulan (pelanggan tetap)
→ Trend: Naik 30% dalam 3 bulan
```

#### 2. **Seasonality (s(t))**
```
Pola berulang yang dipelajari:

Weekly Seasonality (pola mingguan):
- Senin-Jumat: Rp 500-600K/hari (hari kerja)
- Sabtu-Minggu: Rp 800-900K/hari (weekend ramai)

Jika ada data 1 tahun:
- Yearly Seasonality:
  - Januari-Februari: Turun (habis lebaran)
  - Maret-April: Naik (mulai normal)
  - Juli-Agustus: Puncak (liburan)
  - September-Oktober: Normal
  - November-Desember: Naik (akhir tahun)
```

#### 3. **Changepoints**
```
Titik perubahan signifikan dalam trend:

Contoh:
- 1 Nov 2025: Penjualan tiba-tiba naik 50%
  → Mungkin: Buka cabang baru, viral di sosmed
  
- 15 Nov 2025: Penjualan turun 30%
  → Mungkin: Kompetitor buka, masalah kualitas

Prophet otomatis deteksi changepoints ini!
```

### Parameter yang Digunakan:

```python
Prophet(
    # 1. Seasonality Settings
    daily_seasonality=False,     # OFF - tidak ada data per jam
    weekly_seasonality=True,     # ON - ada pola weekend vs weekday
    yearly_seasonality=False,    # OFF - data cuma 61 hari
    
    # 2. Flexibility Settings
    changepoint_prior_scale=0.5, # Tinggi = lebih fleksibel menangkap perubahan
                                 # Rendah = lebih smooth, kurang sensitif
                                 # Default: 0.05 (terlalu kaku)
                                 # Kami: 0.5 (10x lebih fleksibel)
    
    seasonality_prior_scale=10.0, # Kekuatan pola musiman
                                  # Default: 10 (cukup)
                                  # Kami: 10 (pakai default)
    
    # 3. Uncertainty Settings
    interval_width=0.95,         # 95% confidence interval
                                 # Artinya: 95% kemungkinan nilai asli
                                 # akan berada di antara lower_bound dan upper_bound
    
    # 4. Mode Settings
    seasonality_mode='multiplicative' # Untuk retail growth
                                      # Alternatif: 'additive'
)
```

**Kenapa Multiplicative?**
```
Additive: seasonality + trend
→ Efek musiman konstan (naik Rp 100K setiap weekend)

Multiplicative: seasonality × trend  
→ Efek musiman proporsional (naik 20% setiap weekend)

Retail biasanya multiplicative karena:
- Semakin ramai kedai, semakin besar efek weekend
- Pertumbuhan eksponensial, bukan linear
```

---

## 📚 Proses Training Model

### Step-by-Step Training:

```python
# 1. Inisialisasi model
model = Prophet(
    daily_seasonality=False,
    weekly_seasonality=True,
    yearly_seasonality=False,
    changepoint_prior_scale=0.5,
    seasonality_prior_scale=10.0,
    interval_width=0.95,
    seasonality_mode='multiplicative'
)

# 2. Fit model dengan data historis
model.fit(df)

# Proses internal:
# - Stan (MCMC) inference
# - Identifikasi trend
# - Deteksi seasonality
# - Estimasi uncertainty
```

### Apa yang Terjadi di Balik Layar:

```
STEP 1: Data Preparation
────────────────────────
Input: 61 hari data revenue
│
├─ Check missing dates → Fill dengan median
├─ Detect outliers → Cap extreme values
└─ Normalize data → Scale untuk training

STEP 2: Trend Estimation
────────────────────────
Prophet mencoba berbagai piecewise linear functions:
│
├─ Cari best fit untuk trend garis
├─ Identifikasi changepoints (max 25 otomatis)
│   Contoh: 2025-11-15 (tiba-tiba naik)
│           2025-12-01 (tiba-tiba turun)
└─ Estimasi growth rate per segment

STEP 3: Seasonality Detection
─────────────────────────────
Untuk weekly seasonality:
│
├─ Fourier series: sin dan cos functions
├─ Fit pola 7 hari (Senin-Minggu)
├─ Identifikasi hari ramai vs sepi
│   Senin: -15% dari mean
│   Selasa: -10%
│   Rabu: -5%
│   Kamis: 0%
│   Jumat: +5%
│   Sabtu: +20%
│   Minggu: +15%
└─ Smooth seasonality curve

STEP 4: Uncertainty Quantification
──────────────────────────────────
Bayesian inference:
│
├─ Hitung posterior distribution
├─ Simulate 1000+ future scenarios
├─ Calculate percentiles:
│   - 2.5 percentile → lower_bound
│   - 50 percentile → yhat (prediction)
│   - 97.5 percentile → upper_bound
└─ Wide interval = high uncertainty

STEP 5: Model Validation
────────────────────────
Cross-validation internal:
│
├─ Split data: 80% train, 20% test
├─ Train model pada 80%
├─ Test pada 20%
├─ Calculate errors
└─ Tune hyperparameters if needed
```

### Output Training:

```
Log yang terlihat:

[PROPHET] Training with 61 days of data
[PROPHET] Revenue range: 334000.00 - 1037005.00
[PROPHET] Revenue mean: 587430.00, std: 183290.00

Chain [1] start processing
Chain [1] done processing

INFO: Fit model completed (2.3 seconds)
```

---

## 🔮 Proses Prediksi

### Generate Future Dates:

```python
# Create dataframe untuk 30 hari ke depan
future = model.make_future_dataframe(periods=30)

# Result:
#     ds
# 0   2025-10-11  (historis)
# 1   2025-10-12  (historis)
# ...
# 60  2025-12-10  (hari ini)
# 61  2025-12-11  (prediksi)
# 62  2025-12-12  (prediksi)
# ...
# 90  2026-01-09  (prediksi)
```

### Predict:

```python
forecast = model.predict(future)

# forecast berisi banyak kolom:
# - ds: tanggal
# - yhat: prediksi utama
# - yhat_lower: batas bawah
# - yhat_upper: batas atas
# - trend: komponen trend
# - weekly: komponen mingguan
# - weekly_lower: uncertainty weekly
# - weekly_upper: uncertainty weekly
# - multiplicative_terms: gabungan efek multiplikatif
# - yhat_residual: sisa error
```

### Cara Prophet Memprediksi:

```
Untuk tanggal 2025-12-15 (Minggu):

1. BASE PREDICTION dari trend:
   trend(2025-12-15) = 600.000
   
2. TAMBAH SEASONALITY EFFECT:
   weekly_effect(Minggu) = +15% = 600.000 × 1.15 = 690.000
   
3. FINAL PREDICTION:
   yhat = 690.000
   
4. UNCERTAINTY BOUNDS:
   - Historical volatility: ±20%
   - Lower bound (95% CI): 690.000 × 0.8 = 552.000
   - Upper bound (95% CI): 690.000 × 1.2 = 828.000

Artinya:
→ Prediksi: Rp 690.000
→ 95% yakin nilai asli antara Rp 552K - 828K
```

---

## 📊 Evaluasi Akurasi

### 3 Metrik Utama:

#### 1. MAE (Mean Absolute Error)

```python
MAE = (1/n) × Σ|actual - predicted|

Contoh:
Hari 1: |503000 - 515340| = 12340
Hari 2: |471000 - 489230| = 18230
Hari 3: |653000 - 641780| = 11220
...
Hari 61: |367004 - 354672| = 12332

MAE = (12340 + 18230 + ... + 12332) / 61 = 45680

Interpretasi:
→ Rata-rata selisih prediksi vs aktual: Rp 45.680
→ Dalam skala Rp 587K (mean), error 7.7%
→ Semakin kecil MAE, semakin baik
```

#### 2. RMSE (Root Mean Squared Error)

```python
RMSE = √[(1/n) × Σ(actual - predicted)²]

Contoh:
Hari 1: (503000 - 515340)² = 152,274,560
Hari 2: (471000 - 489230)² = 332,329,000
Hari 3: (653000 - 641780)² = 125,928,400
...

RMSE = √[(152274560 + 332329000 + ...) / 61] = 58920

Interpretasi:
→ Penalti lebih besar untuk error besar
→ RMSE > MAE karena squaring
→ Sensitivitas terhadap outlier
→ Gunakan untuk deteksi anomali
```

#### 3. MAPE (Mean Absolute Percentage Error)

```python
MAPE = (100/n) × Σ|(actual - predicted) / actual|

Contoh:
Hari 1: |503000 - 515340| / 503000 = 0.0245 = 2.45%
Hari 2: |471000 - 489230| / 471000 = 0.0387 = 3.87%
Hari 3: |653000 - 641780| / 653000 = 0.0172 = 1.72%
...

MAPE = (2.45 + 3.87 + 1.72 + ...) / 61 = 8.24%

Interpretasi:
→ Akurasi model: 100% - 8.24% = 91.76%
→ Kategori: Excellent (< 10%)
→ Paling mudah dipahami user
```

### Interpretasi Gabungan:

```
Model Forecast Kedai Kopi:
├─ MAE: Rp 45.680  → Selisih rata-rata ±45K
├─ RMSE: Rp 58.920 → Ada beberapa hari dengan error besar
└─ MAPE: 8.24%     → Akurasi 91.76% (Excellent!)

Kesimpulan:
✅ Model sangat akurat (MAPE < 10%)
✅ Error cukup konsisten (RMSE tidak jauh dari MAE)
✅ Bisa dipercaya untuk planning

Rekomendasi:
- Gunakan predicted_revenue untuk estimasi
- Siapkan buffer 10% untuk safety
- Monitor actual vs predicted untuk improvement
```

---

## 💾 Penyimpanan Hasil

### Database Schema:

```sql
CREATE TABLE sales_forecasts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    forecast_date DATE NOT NULL,           -- Tanggal prediksi
    predicted_revenue DECIMAL(10,2),       -- Prediksi utama
    lower_bound DECIMAL(10,2),             -- Batas bawah (pesimis)
    upper_bound DECIMAL(10,2),             -- Batas atas (optimis)
    mae DECIMAL(10,2),                     -- Mean Absolute Error
    rmse DECIMAL(10,2),                    -- Root Mean Squared Error
    mape DECIMAL(10,2),                    -- Mean Absolute Percentage Error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Kapan prediksi dibuat
    INDEX idx_forecast_date (forecast_date),
    INDEX idx_created_at (created_at)
);
```

### Contoh Data:

```sql
INSERT INTO sales_forecasts VALUES
(1, '2025-12-11', 612450.00, 428320.00, 798120.00, 45680.50, 58920.30, 8.24, '2025-12-10 23:45:12'),
(2, '2025-12-12', 634780.00, 449560.00, 821340.00, 45680.50, 58920.30, 8.24, '2025-12-10 23:45:12'),
(3, '2025-12-13', 598230.00, 411890.00, 782670.00, 45680.50, 58920.30, 8.24, '2025-12-10 23:45:12'),
...
(30, '2026-01-09', 687920.00, 502140.00, 875230.00, 45680.50, 58920.30, 8.24, '2025-12-10 23:45:12');
```

### Kegunaan Penyimpanan:

1. **Historical Tracking**
   ```sql
   -- Lihat prediksi vs aktual
   SELECT 
       f.forecast_date,
       f.predicted_revenue,
       t.actual_revenue,
       ABS(f.predicted_revenue - t.actual_revenue) as error
   FROM sales_forecasts f
   LEFT JOIN (
       SELECT DATE(created_at) as date, SUM(total_amount) as actual_revenue
       FROM transactions
       GROUP BY DATE(created_at)
   ) t ON f.forecast_date = t.date
   WHERE f.forecast_date <= CURDATE();
   ```

2. **Model Improvement**
   ```sql
   -- Calculate actual MAPE
   SELECT 
       AVG(ABS((actual - predicted) / actual) * 100) as actual_mape
   FROM forecast_vs_actual;
   ```

3. **Riwayat Prediksi**
   ```
   User bisa lihat:
   - Prediksi yang pernah dibuat
   - Apakah prediksi akurat?
   - Trend akurasi model
   ```

---

## ⏰ Scheduler Otomatis

### Auto-Forecast Schedule:

```python
# File: services/report-service/app.py

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def check_and_run_forecast():
    """
    Run otomatis setiap akhir bulan
    """
    with app.app_context():
        today = datetime.utcnow()
        
        # Check if end of month
        tomorrow = today + timedelta(days=1)
        if tomorrow.day == 1:  # Besok tanggal 1 = hari ini akhir bulan
            print("[AUTO-FORECAST] Running auto forecast...")
            
            # Train model dengan 90 hari terakhir
            result, error = train_and_predict_sales(
                historical_days=90, 
                forecast_days=30
            )
            
            if result:
                # Save ke database
                save_forecast_to_db(result['predictions'], result['errors'])
                print("[AUTO-FORECAST] Success!")
            else:
                print(f"[AUTO-FORECAST] Failed: {error}")
        else:
            print("[AUTO-FORECAST] Not end of month, skipping")

# Schedule: Setiap hari jam 23:00
scheduler.add_job(
    func=check_and_run_forecast,
    trigger='cron',
    hour=23,
    minute=0,
    id='auto_forecast'
)

scheduler.start()
```

### Kapan Auto-Forecast Jalan?

```
Contoh:
- 30 Januari 2026, 23:00 → RUN ✅ (besok tanggal 1)
- 28 Februari 2026, 23:00 → RUN ✅ (besok tanggal 1)
- 31 Maret 2026, 23:00 → RUN ✅ (besok tanggal 1)
- 15 April 2026, 23:00 → SKIP (besok bukan tanggal 1)

Hasil:
→ Prediksi selalu ready di awal bulan
→ Pemilik bisa planning untuk bulan depan
```

---

## 🎯 Contoh Kasus Nyata

### Skenario: Prediksi Penjualan Januari 2026

#### Data Historis (Oktober - Desember 2025):

```
OKTOBER 2025: (31 hari)
├─ Weekend: Rp 800-900K/hari
├─ Weekday: Rp 500-600K/hari
└─ Total bulan: Rp 20.500.000

NOVEMBER 2025: (30 hari)
├─ Weekend: Rp 850-950K/hari (naik sedikit)
├─ Weekday: Rp 550-650K/hari
├─ Tanggal 15: VIRAL di TikTok → Rp 1.500.000 (anomali)
└─ Total bulan: Rp 22.300.000

DESEMBER 2025: (10 hari sampai sekarang)
├─ Weekend: Rp 900K-1.000K/hari (trend naik)
├─ Weekday: Rp 600-700K/hari
└─ Total 10 hari: Rp 7.000.000 (estimasi bulan: Rp 21.000.000)
```

#### Analisis Model:

```
TREND DETECTION:
────────────────
Oktober → November: +9% (Rp 20.5jt → 22.3jt)
November → Desember: -6% (penurunan karena akhir tahun sibuk)

Linear trend: +1.5% per bulan
Growth rate: Stabil dengan fluktuasi kecil

SEASONALITY DETECTION:
─────────────────────
Weekly Pattern:
- Senin-Kamis: 85-95% dari mean (sepi)
- Jumat: 100-105% dari mean (mulai ramai)
- Sabtu-Minggu: 130-150% dari mean (ramai)

Monthly Pattern (belum cukup data untuk yearly):
- Awal bulan: Normal (tanggal gajian habis)
- Pertengahan: Puncak (tanggal 15-20, sebelum gajian)
- Akhir bulan: Turun (tunggu gajian)

CHANGEPOINTS:
────────────
- 15 November: Viral TikTok (+150% anomali)
  → Model treat sebagai outlier, tidak mempengaruhi trend
  
- 1 Desember: Akhir tahun effect (-10%)
  → Banyak orang liburan ke luar kota
```

#### Prediksi Januari 2026:

```
HASIL PREDIKSI:

Week 1 (1-7 Jan):
├─ 1 Jan (Kamis): Rp 650.000 (weekday normal)
├─ 2 Jan (Jumat): Rp 700.000 (Jumat)
├─ 3 Jan (Sabtu): Rp 920.000 (Weekend)
├─ 4 Jan (Minggu): Rp 950.000 (Weekend)
├─ 5 Jan (Senin): Rp 600.000 (Weekday)
├─ 6 Jan (Selasa): Rp 620.000 (Weekday)
└─ 7 Jan (Rabu): Rp 630.000 (Weekday)
Total Week 1: Rp 5.070.000

Week 2 (8-14 Jan):
├─ Similar pattern
└─ Total Week 2: Rp 5.200.000 (sedikit naik, trend +1.5%)

Week 3 (15-21 Jan):
├─ Tanggal 15 (Kamis): Rp 720.000 (tanggal gajian, ramai)
├─ Weekend: Rp 950-1.000K
└─ Total Week 3: Rp 5.500.000 (puncak)

Week 4 (22-28 Jan):
├─ Mulai turun lagi (tunggu gajian)
└─ Total Week 4: Rp 5.100.000

Week 5 (29-31 Jan):
├─ Akhir bulan (low)
└─ Total Week 5: Rp 1.900.000

─────────────────────────────────────────
TOTAL PREDIKSI JANUARI 2026: Rp 22.770.000

Confidence Interval (95%):
- Lower Bound (Pesimis): Rp 18.500.000
- Predicted (Most Likely): Rp 22.770.000
- Upper Bound (Optimis): Rp 27.300.000
```

#### Rekomendasi Bisnis:

```
BERDASARKAN PREDIKSI DI ATAS:

1. PEMBELIAN BAHAN:
   ────────────────
   Prediksi revenue: Rp 22.770.000
   COGS (40%): Rp 9.100.000
   
   Bahan yang perlu dibeli:
   ├─ Kopi: 45 kg × Rp 120K = Rp 5.400.000
   ├─ Susu: 150 L × Rp 15K = Rp 2.250.000
   └─ Lain-lain: Rp 1.450.000
   
   ⚠️ JANGAN BELI SEKALIGUS!
   → Beli bertahap:
     - Awal bulan: 40%
     - Tanggal 10: 30%
     - Tanggal 20: 30%

2. STAFFING:
   ─────────
   Prediksi ramai: Weekend & tanggal 15-20
   
   Jadwal kasir:
   ├─ Weekday: 1 kasir
   └─ Weekend + tanggal 15-20: 2 kasir

3. PROMO:
   ──────
   Target slow days (Senin-Rabu):
   → Buat promo "Weekday Special"
   → Diskon 10% untuk 2 cup
   
   Goal: Naikkan weekday dari Rp 600K → 700K
   Potential gain: +Rp 3.000.000/bulan

4. CASH FLOW:
   ──────────
   Prediksi income: Rp 22.770.000
   Expenses:
   ├─ COGS: Rp 9.100.000
   ├─ Gaji: Rp 6.000.000
   ├─ Sewa: Rp 3.000.000
   └─ Operasional: Rp 2.000.000
   
   Net profit: Rp 2.670.000
   Margin: 11.7% (healthy untuk F&B)
```

---

## 🎓 Kesimpulan

### Keunggulan Sistem Prediksi:

✅ **Akurat**: MAPE < 10% (kategori Excellent)
✅ **Otomatis**: Auto-run setiap akhir bulan
✅ **Real-time**: Update sesuai data terbaru
✅ **Actionable**: Ada rekomendasi bisnis konkret
✅ **Trackable**: Simpan riwayat untuk evaluasi

### Keterbatasan:

⚠️ **Butuh minimal 7 hari data** (idealnya 60+ hari)
⚠️ **Tidak bisa prediksi event ekstrim** (pandemi, bencana)
⚠️ **Akurasi turun jika ada perubahan drastis** (ganti menu, kompetitor)
⚠️ **Confidence interval lebar di awal** (data masih sedikit)

### Best Practices:

1. **Update data rutin** - Transaksi harus tercatat lengkap
2. **Review prediksi bulanan** - Bandingkan vs aktual
3. **Adjust planning** - Gunakan sebagai guideline, bukan hukum mutlak
4. **Combine dengan intuisi** - AI + human judgment = terbaik

---

**Sistem prediksi ini membantu kedai kopi membuat keputusan bisnis yang data-driven, bukan asal tebak! 📊🚀**
