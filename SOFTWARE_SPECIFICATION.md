# Spesifikasi Penggunaan Perangkat Lunak

## Sistem Manajemen Kedai Kopi

---

## A. SPESIFIKASI SISTEM

### 1. Persyaratan Hardware

#### Server/Development Machine (Minimum)

| Komponen  | Spesifikasi Minimum         | Spesifikasi Rekomendasi                       |
| --------- | --------------------------- | --------------------------------------------- |
| Processor | Intel Core i3 / AMD Ryzen 3 | Intel Core i5 / AMD Ryzen 5 atau lebih tinggi |
| RAM       | 4 GB                        | 8 GB atau lebih                               |
| Storage   | 20 GB free space (SSD)      | 50 GB free space (SSD)                        |
| Network   | 10 Mbps                     | 100 Mbps atau lebih                           |

#### Client Machine (Kasir/Admin)

| Komponen  | Spesifikasi Minimum    | Spesifikasi Rekomendasi     |
| --------- | ---------------------- | --------------------------- |
| Processor | Intel Celeron / AMD A6 | Intel Core i3 / AMD Ryzen 3 |
| RAM       | 2 GB                   | 4 GB atau lebih             |
| Storage   | 5 GB free space        | 10 GB free space            |
| Display   | 1366x768               | 1920x1080 atau lebih        |
| Network   | 5 Mbps                 | 10 Mbps atau lebih          |

---

### 2. Persyaratan Software

#### Server Requirements

| Software             | Versi                                   | Keterangan                    |
| -------------------- | --------------------------------------- | ----------------------------- |
| **Operating System** | Windows 10/11, Ubuntu 20.04+, macOS 11+ | Development & Production      |
| **Docker Desktop**   | 24.0+                                   | Container runtime             |
| **Docker Compose**   | 2.20+                                   | Multi-container orchestration |
| **Git**              | 2.40+                                   | Version control               |

#### Development Tools (Optional)

| Tool                | Versi   | Fungsi                  |
| ------------------- | ------- | ----------------------- |
| **VS Code**         | Latest  | Code editor             |
| **Python**          | 3.11+   | Backend development     |
| **Node.js**         | 18+ LTS | Frontend tooling        |
| **MySQL Workbench** | 8.0+    | Database management GUI |
| **Postman**         | Latest  | API testing             |

#### Browser Requirements (Client)

| Browser           | Versi Minimum | Status             |
| ----------------- | ------------- | ------------------ |
| Google Chrome     | 100+          | ✅ Recommended     |
| Mozilla Firefox   | 100+          | ✅ Supported       |
| Microsoft Edge    | 100+          | ✅ Supported       |
| Safari            | 15+           | ⚠️ Limited testing |
| Internet Explorer | -             | ❌ Not supported   |

---

## B. INSTALASI & KONFIGURASI

### 1. Instalasi Docker Desktop

#### Windows

```bash
# Download Docker Desktop dari:
https://www.docker.com/products/docker-desktop

# Install dan restart komputer
# Enable WSL 2 jika diminta
```

#### Linux (Ubuntu)

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Setup repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
sudo docker --version
sudo docker compose version
```

#### macOS

```bash
# Install via Homebrew
brew install --cask docker

# Or download from:
https://www.docker.com/products/docker-desktop
```

---

### 2. Clone Repository

```bash
# Clone project
git clone https://github.com/yourusername/kedai-kopi.git

# Masuk ke direktori project
cd kedai-kopi

# Cek struktur folder
ls -la
```

---

### 3. Konfigurasi Environment Variables

```bash
# File .env sudah tersedia, review dan sesuaikan jika perlu
cat .env

# Konfigurasi penting yang perlu diubah untuk production:
```

**.env Configuration:**

```env
# Database - GANTI untuk production
MYSQL_ROOT_PASSWORD=your_secure_password_here
MYSQL_PASSWORD=your_secure_password_here

# JWT - GANTI untuk production
JWT_SECRET_KEY=your_super_secret_jwt_key_minimum_32_characters

# n8n - GANTI untuk production
N8N_BASIC_AUTH_PASSWORD=your_secure_password_here
ADMIN_PASSWORD=your_secure_password_here

# Midtrans - Masukkan credentials asli
MIDTRANS_SERVER_KEY=your_midtrans_server_key
MIDTRANS_CLIENT_KEY=your_midtrans_client_key
MIDTRANS_IS_PRODUCTION=false

# Email - Untuk notifikasi
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram - Untuk notifikasi
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

---

### 4. Build & Run Services

```bash
# Build semua services
docker-compose build

# Start semua services
docker-compose up -d

# Cek status services
docker-compose ps

# Expected output:
# NAME                      STATUS    PORTS
# kedai-kopi-mysql          Up        3306
# kedai-kopi-redis          Up        6379
# kedai-kopi-auth           Up        5001
# kedai-kopi-product        Up        5002
# kedai-kopi-stock          Up        5003
# kedai-kopi-transaction    Up        5004
# kedai-kopi-report         Up        5005
# kedai-kopi-n8n            Up        5678
# kedai-kopi-gateway        Up        80, 443
```

---

### 5. Verifikasi Instalasi

#### Cek Service Health

```bash
# Cek logs semua services
docker-compose logs

# Cek logs service tertentu
docker-compose logs auth-service
docker-compose logs mysql

# Cek health status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

#### Test API Endpoints

```bash
# Test health check
curl http://localhost/health

# Expected response:
# {"status": "ok", "services": [...]}

# Test login
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Expected response:
# {"access_token": "...", "user": {...}}
```

#### Access Web Interface

```
Open browser:
http://localhost

Default credentials:
Username: admin
Password: admin123
```

---

### 6. Generate Data Historis (Untuk Prediksi)

```bash
# Generate 60 hari data transaksi untuk fitur prediksi
docker exec -i kedai-kopi-mysql mysql -uroot -prootpassword123 \
  kedai_kopi < generate_historical_data.sql

# Expected output:
# Historical data generated successfully!
```

---

## C. TOOLS YANG DIGUNAKAN

### 1. Backend Development

| Tool/Library           | Versi  | Fungsi                          | Dokumentasi                               |
| ---------------------- | ------ | ------------------------------- | ----------------------------------------- |
| **Python**             | 3.11   | Programming language            | https://python.org                        |
| **Flask**              | 3.0.0  | Web framework                   | https://flask.palletsprojects.com         |
| **Flask-JWT-Extended** | 4.6.0  | JWT authentication              | https://flask-jwt-extended.readthedocs.io |
| **Flask-CORS**         | 4.0.0  | Cross-origin resource sharing   | https://flask-cors.readthedocs.io         |
| **SQLAlchemy**         | 2.0.23 | ORM (Object-Relational Mapping) | https://www.sqlalchemy.org                |
| **PyMySQL**            | 1.1.0  | MySQL database driver           | https://pymysql.readthedocs.io            |
| **Marshmallow**        | 3.20.1 | Object serialization/validation | https://marshmallow.readthedocs.io        |
| **Bcrypt**             | 4.1.2  | Password hashing                | https://pypi.org/project/bcrypt/          |
| **Redis**              | 5.0.1  | Caching & session storage       | https://redis-py.readthedocs.io           |
| **Prophet**            | 1.1.6  | Time series forecasting (ML)    | https://facebook.github.io/prophet/       |
| **Pandas**             | 2.1.4  | Data manipulation               | https://pandas.pydata.org                 |
| **NumPy**              | 1.26.2 | Numerical computing             | https://numpy.org                         |
| **Scikit-learn**       | 1.3.2  | Machine learning utilities      | https://scikit-learn.org                  |
| **APScheduler**        | 3.10.4 | Task scheduling                 | https://apscheduler.readthedocs.io        |
| **Gunicorn**           | 21.2.0 | WSGI HTTP server                | https://gunicorn.org                      |

#### Requirements Files

```txt
# services/auth-service/requirements.txt
Flask==3.0.0
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
SQLAlchemy==2.0.23
PyMySQL==1.1.0
marshmallow==3.20.1
bcrypt==4.1.2
redis==5.0.1
python-dotenv==1.0.0
gunicorn==21.2.0

# services/report-service/requirements.txt (tambahan untuk ML)
prophet==1.1.6
cmdstanpy==1.2.4
pandas==2.1.4
numpy==1.26.2
scikit-learn==1.3.2
APScheduler==3.10.4
```

---

### 2. Frontend Development

| Tool/Library           | Versi  | Fungsi               | CDN                                                 |
| ---------------------- | ------ | -------------------- | --------------------------------------------------- |
| **Bootstrap**          | 5.3.2  | CSS framework        | https://cdn.jsdelivr.net/npm/bootstrap@5.3.2        |
| **Bootstrap Icons**    | 1.11.1 | Icon library         | https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1 |
| **Chart.js**           | 4.4.0  | Data visualization   | https://cdn.jsdelivr.net/npm/chart.js@4.4.0         |
| **Vanilla JavaScript** | ES6+   | Programming language | Native browser                                      |

#### File Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── style.css      # Custom styles
└── js/
    ├── app.js         # Main application logic
    ├── auth.js        # Authentication
    ├── config.js      # API endpoints configuration
    ├── dashboard.js   # Dashboard functionality
    ├── products.js    # Product management
    ├── stock.js       # Stock management
    ├── transaction.js # Transaction processing
    ├── reports.js     # Reports & forecasting
    └── users.js       # User management
```

---

### 3. Database & Storage

| Tool               | Versi    | Fungsi              |
| ------------------ | -------- | ------------------- |
| **MySQL**          | 8.0      | Relational database |
| **Redis**          | 7-alpine | In-memory cache     |
| **Docker Volumes** | -        | Persistent storage  |

#### Database Schema

```sql
-- Main database: kedai_kopi
-- Tables:
- users (10 columns)
- products (9 columns)
- categories (4 columns)
- product_ingredients (5 columns)
- stocks (10 columns)
- stock_history (9 columns)
- transactions (12 columns)
- transaction_items (8 columns)
- refresh_tokens (5 columns)
- sales_forecasts (9 columns)

-- n8n database: n8n (managed by n8n)
```

---

### 4. Workflow Automation

| Tool    | Versi  | Fungsi              | Access                |
| ------- | ------ | ------------------- | --------------------- |
| **n8n** | latest | Workflow automation | http://localhost:5678 |

#### Workflows

1. **Low Stock Alert** - Notifikasi stok menipis
2. **Transaction Notification** - Notifikasi transaksi besar
3. **Daily Sales Report** - Laporan harian otomatis
4. **Database Backup** - Backup database harian

---

### 5. API Gateway & Reverse Proxy

| Tool      | Versi  | Fungsi                             |
| --------- | ------ | ---------------------------------- |
| **Nginx** | alpine | Reverse proxy & static file server |

#### Configuration

```nginx
# gateway/nginx.conf
- Route /api/* to backend services
- Serve /frontend as static files
- Load balancing (round-robin)
- SSL/TLS termination ready
```

---

### 6. Payment Gateway

| Service      | Provider | Environment        |
| ------------ | -------- | ------------------ |
| **Midtrans** | Snap API | Sandbox/Production |

#### Integration

- **Client Key**: Frontend payment UI
- **Server Key**: Backend payment verification
- **Webhook**: Payment status updates

---

### 7. Containerization & Orchestration

| Tool               | Versi | Fungsi                        |
| ------------------ | ----- | ----------------------------- |
| **Docker**         | 24.0+ | Container runtime             |
| **Docker Compose** | 2.20+ | Multi-container orchestration |

#### Container Architecture

```yaml
Services (10 containers):
1. mysql          - Database
2. redis          - Cache
3. auth-service   - Authentication
4. product-service - Product management
5. stock-service  - Stock management
6. transaction-service - Transaction processing
7. report-service - Reports & forecasting
8. n8n            - Workflow automation
9. mysql-backup   - Automated backups
10. gateway       - Nginx reverse proxy
```

---

### 8. Version Control & CI/CD

| Tool           | Fungsi                        |
| -------------- | ----------------------------- |
| **Git**        | Version control               |
| **GitHub**     | Repository hosting            |
| **Docker Hub** | Container registry (optional) |

---

### 9. Monitoring & Logging

#### Built-in Logging

```bash
# View logs
docker-compose logs -f [service-name]

# Example:
docker-compose logs -f auth-service
docker-compose logs -f transaction-service
```

#### Log Locations

```
Container logs: /var/log/docker/
Application logs: stdout (via docker logs)
n8n logs: /home/node/.n8n/logs/
MySQL logs: /var/log/mysql/
```

---

### 10. Backup & Recovery

| Tool                  | Schedule       | Location       |
| --------------------- | -------------- | -------------- |
| **MySQL Cron Backup** | Daily 02:00 AM | ./backups/     |
| **Docker Volumes**    | Manual         | Docker volumes |

#### Backup Commands

```bash
# Manual database backup
docker exec kedai-kopi-mysql mysqldump \
  -uroot -prootpassword123 \
  --single-transaction \
  kedai_kopi > backup_$(date +%Y%m%d).sql

# Restore database
docker exec -i kedai-kopi-mysql mysql \
  -uroot -prootpassword123 \
  kedai_kopi < backup_20251210.sql

# Backup Docker volumes
docker run --rm -v mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql_data.tar.gz -C /data .
```

---

## D. PENGGUNAAN SISTEM

### 1. Login System

#### Login sebagai Admin

```
URL: http://localhost
Username: admin
Password: admin123
Role: admin

Akses:
✅ Dashboard
✅ Manajemen Produk (CRUD)
✅ Manajemen Stok (CRUD)
✅ Laporan Penjualan
✅ Prediksi Penjualan (Prophet ML)
✅ Manajemen User
✅ Semua Transaksi
```

#### Login sebagai Kasir

```
URL: http://localhost
Username: kasir1
Password: kasir123
Role: cashier

Akses:
✅ Dashboard (limited)
✅ Transaksi Baru
✅ Riwayat Transaksi (milik sendiri)
❌ Manajemen Produk
❌ Manajemen Stok
❌ Laporan
❌ Manajemen User
```

---

### 2. Fitur Utama

#### A. Transaksi (Kasir)

```
1. Klik menu "Transaksi"
2. Pilih produk dari list
3. Input quantity
4. Klik "Tambah ke Keranjang"
5. Review keranjang
6. Pilih metode pembayaran:
   - Cash: Input jumlah bayar
   - E-Money: Redirect ke Midtrans
7. Proses transaksi
8. Sistem otomatis:
   - Kurangi stok bahan
   - Generate struk
   - Kirim notifikasi (jika > 100K)
9. Cetak/Download struk
```

#### B. Manajemen Produk (Admin)

```
1. Klik menu "Produk"
2. Operasi:

   Tambah Produk:
   - Klik "Tambah Produk"
   - Isi form (nama, kategori, harga, deskripsi)
   - Tambah bahan-bahan (ingredients):
     * Nama Bahan
     * Quantity
     * Unit (gram/ml/kg/liter)
   - Klik "Simpan"

   Edit Produk:
   - Klik icon pensil
   - Modal terbuka dengan data produk + ingredients
   - Edit data
   - Klik "Simpan"

   View Detail:
   - Klik icon mata
   - Modal menampilkan:
     * Info produk
     * List ingredients
     * Badge status

   Hapus Produk:
   - Klik icon trash
   - Konfirmasi hapus
   - Produk + ingredients terhapus (CASCADE)
```

#### C. Manajemen Stok (Admin)

```
1. Klik menu "Stok"
2. Operasi:

   Tambah Bahan:
   - Klik "Tambah Stok"
   - Isi form (nama, quantity, unit, minimum, harga, supplier)
   - Klik "Simpan"

   Restock:
   - Klik "Restock" pada bahan
   - Input quantity tambahan
   - Sistem update:
     * quantity_after = quantity_before + quantity_change
     * Create history record
     * Check low stock alert

   Adjustment:
   - Klik "Adjustment"
   - Input quantity baru
   - Sistem set ulang quantity

   View History:
   - Klik "History" pada bahan
   - Tampilkan stock_history:
     * Change type
     * Quantity before/after
     * Reference (transaction code)
     * Created by
     * Timestamp

   Low Stock Alert:
   - Filter "Low Stock Only"
   - Tampilkan bahan < minimum_stock
   - Badge merah untuk alert
```

#### D. Laporan Penjualan (Admin)

```
1. Klik menu "Laporan"
2. Tab "Laporan Penjualan"
3. Input filter:
   - Start Date
   - End Date
4. Klik "Generate Laporan"
5. Sistem menampilkan:
   - Total Revenue (Rp)
   - Total Transaksi (count)
   - Grafik penjualan per hari (Chart.js)
   - Top 5 produk terlaris
   - Tabel detail transaksi
6. Klik "Export PDF" untuk download
```

#### E. Prediksi Penjualan (Admin) - Prophet ML

```
1. Klik menu "Laporan"
2. Tab "Prediksi Penjualan"
3. Input parameter:
   - Historical Days: 60 (default)
   - Forecast Days: 30 (default)
4. Klik "Generate Prediksi"
5. Sistem:
   - Validasi data (min 7 hari)
   - Load historical data
   - Train Prophet model
   - Generate forecast 30 hari ke depan
   - Calculate accuracy metrics:
     * MAE (Mean Absolute Error)
     * RMSE (Root Mean Squared Error)
     * MAPE (Mean Absolute Percentage Error)
6. Tampilan:
   - Grafik prediksi (Chart.js)
     * Actual revenue (line chart)
     * Predicted revenue (line chart)
     * Confidence interval (area chart)
   - Tabel forecast:
     * Date
     * Predicted Revenue
     * Lower Bound
     * Upper Bound
   - Accuracy Metrics (cards):
     * MAE: Rp 107K
     * RMSE: Rp 145K
     * MAPE: 19.97%
7. Auto-save:
   - Jika tanggal 28-31 bulan, auto-save ke database
   - History forecast tersimpan untuk audit
```

---

### 3. Akses n8n Workflow

```
URL: http://localhost:5678

Login:
Email: sughara78@gmail.com
Password: [gunakan command reset password]

Reset Password:
docker exec -it kedai-kopi-n8n n8n user-management:reset \
  --email=sughara78@gmail.com \
  --password=admin123

Workflows:
1. Low Stock Alert
2. Transaction Notification
3. Daily Sales Report
4. Database Backup
```

---

### 4. Troubleshooting

#### Service tidak start

```bash
# Cek logs error
docker-compose logs [service-name]

# Restart service
docker-compose restart [service-name]

# Rebuild service
docker-compose build [service-name]
docker-compose up -d [service-name]
```

#### Database connection error

```bash
# Cek MySQL status
docker-compose ps mysql

# Cek MySQL logs
docker-compose logs mysql

# Test connection
docker exec -it kedai-kopi-mysql mysql \
  -ukopi_user -pkopi_password123 \
  -e "SELECT 1"

# Reset database (DANGER: data loss)
docker-compose down -v
docker-compose up -d
```

#### Port already in use

```bash
# Cek port usage
netstat -ano | findstr :80
netstat -ano | findstr :3306

# Stop conflicting service atau ganti port di docker-compose.yml
```

#### Prophet prediction error

```bash
# Cek data availability
docker exec -i kedai-kopi-mysql mysql \
  -uroot -prootpassword123 kedai_kopi \
  -e "SELECT COUNT(*) FROM transactions"

# Generate historical data
docker exec -i kedai-kopi-mysql mysql \
  -uroot -prootpassword123 kedai_kopi \
  < generate_historical_data.sql
```

---

## E. MAINTENANCE

### 1. Update System

```bash
# Pull latest changes
git pull origin main

# Rebuild services
docker-compose build

# Restart services
docker-compose down
docker-compose up -d

# Verify
docker-compose ps
```

### 2. Database Maintenance

```bash
# Optimize tables
docker exec -i kedai-kopi-mysql mysql \
  -uroot -prootpassword123 \
  -e "OPTIMIZE TABLE kedai_kopi.transactions"

# Check table integrity
docker exec -i kedai-kopi-mysql mysql \
  -uroot -prootpassword123 \
  -e "CHECK TABLE kedai_kopi.transactions"

# Repair table (if needed)
docker exec -i kedai-kopi-mysql mysql \
  -uroot -prootpassword123 \
  -e "REPAIR TABLE kedai_kopi.transactions"
```

### 3. Log Cleanup

```bash
# Clear Docker logs
docker system prune -a --volumes

# Backup then truncate logs
docker-compose logs > backup_logs.txt
truncate -s 0 $(docker inspect --format='{{.LogPath}}' kedai-kopi-mysql)
```

### 4. Security Updates

```bash
# Update Docker images
docker-compose pull

# Rebuild with latest base images
docker-compose build --pull

# Restart
docker-compose up -d
```

---

## F. DEPLOYMENT PRODUCTION

### 1. Persiapan

```bash
# Update .env untuk production
MYSQL_ROOT_PASSWORD=strong_random_password_32_chars
JWT_SECRET_KEY=production_jwt_secret_64_chars
N8N_BASIC_AUTH_PASSWORD=strong_password
MIDTRANS_IS_PRODUCTION=true
FLASK_ENV=production
FLASK_DEBUG=0

# Setup SSL certificate
# Copy certificate files ke gateway/ssl/
```

### 2. Optimisasi

```bash
# Build optimized images
docker-compose -f docker-compose.prod.yml build --no-cache

# Start with production config
docker-compose -f docker-compose.prod.yml up -d

# Enable auto-restart
docker update --restart=always $(docker ps -q)
```

### 3. Monitoring

```bash
# Setup monitoring tools
# - Prometheus + Grafana
# - ELK Stack (Elasticsearch, Logstash, Kibana)
# - Uptime monitoring (UptimeRobot, Pingdom)
```

---

## G. SUPPORT & DOKUMENTASI

### Dokumentasi Lengkap

```
README.md                    - Overview & quickstart
API_DOCS.md                  - API documentation
FLOWCHART.md                 - System flowcharts
DATABASE_NORMALIZATION.md    - Database design
MIDTRANS_SETUP.md           - Payment gateway setup
TESTING_PAYMENT.md          - Payment testing guide
TROUBLESHOOTING.md          - Common issues
n8n/SETUP.md                - n8n workflow setup
```

### Contact Support

```
GitHub Issues: [repository-url]/issues
Email: support@kedaikopi.com
Documentation: http://localhost/docs (if enabled)
```

---

**Versi Dokumen:** 1.0  
**Tanggal:** 10 Desember 2025  
**Penulis:** Tim Development Kedai Kopi
