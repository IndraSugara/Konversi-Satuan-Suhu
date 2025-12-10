# 📋 Panduan Serah Terima Sistem ke Pemilik Toko

## 🎯 Informasi Sistem

**Nama Sistem:** Kedai Kopi Batman Batu 9 - Sistem Informasi Manajemen  
**Versi:** 1.1.0  
**Tanggal Serah Terima:** 11 Desember 2025  
**Developer:** [Nama Developer]  
**Pemilik:** Kedai Kopi Batman Batu 9

---

## 🔐 Kredensial Akses

### 1. Akses Sistem Utama (Frontend)
```
URL: http://localhost (atau IP server)
Username: owner
Password: Batman@2025
Role: Admin (Full Access)
```

### 2. Akses Database
```
Host: localhost
Port: 3306
Database: kedai_kopi
Username: kopi_user
Password: kopi_password123
Root Password: rootpassword123
```

### 3. Akses MinIO (Image Storage)
```
Console: http://localhost:9001
Username: minioadmin
Password: minioadmin123
```

### 4. Akses n8n (Automation)
```
URL: http://localhost:5678
Email: batman.kedaikopi@gmail.com
Password: Batman@2025
```

---

## 📱 Cara Menggunakan Sistem

### Login Pertama Kali

1. **Buka browser** (Chrome/Firefox/Edge)
2. **Ketik alamat:** `http://localhost` atau IP server
3. **Login dengan:**
   - Username: `owner`
   - Password: `Batman@2025`
4. **Anda akan masuk ke Dashboard**

### Menu yang Tersedia

#### 1. 📊 Dashboard
- Lihat ringkasan penjualan hari ini
- Total transaksi
- Grafik penjualan 7 hari terakhir
- Produk terlaris
- Stok menipis (jika ada)

#### 2. 🛒 Transaksi (Kasir)
- Pilih produk dengan klik card
- Masukkan jumlah pembelian
- Pilih metode pembayaran:
  - **Tunai:** Input jumlah bayar → sistem hitung kembalian
  - **E-Money:** Scan QR Code via Midtrans
- Klik "Proses Transaksi"
- Cetak/Download struk

#### 3. 📦 Produk
- **Tambah Produk Baru:**
  - Klik "Tambah Produk"
  - Isi nama, kategori, harga, deskripsi
  - Upload gambar (klik "Choose File")
  - Tambah bahan-bahan (resep)
  - Klik "Simpan"

- **Edit Produk:**
  - Klik icon pensil (✏️)
  - Ubah data yang perlu
  - Upload gambar baru (jika perlu)
  - Klik "Simpan"

- **Lihat Detail:**
  - Klik icon mata (👁️)
  - Lihat info lengkap + bahan-bahan

- **Hapus Produk:**
  - Klik icon tempat sampah (🗑️)
  - Konfirmasi hapus

#### 4. 📊 Stok Bahan
- **Lihat Stok:**
  - Tabel menampilkan semua bahan
  - Warna merah = stok menipis
  
- **Restock (Tambah Stok):**
  - Klik "Restock" pada bahan
  - Input jumlah tambahan
  - Sistem otomatis update

- **Adjustment (Koreksi Stok):**
  - Klik "Adjustment"
  - Input jumlah stok yang benar
  - Untuk stock opname fisik

- **Lihat History:**
  - Klik "History"
  - Lihat riwayat perubahan stok

#### 5. 📈 Laporan

**Laporan Penjualan:**
- Pilih tanggal mulai dan akhir
- Klik "Generate Laporan"
- Lihat grafik dan tabel
- Download PDF/Excel

**Prediksi Penjualan (AI):**
- Klik tab "Prediksi Penjualan"
- Sistem akan prediksi 30 hari ke depan
- Gunakan untuk planning restock
- Akurasi: ~80% (MAPE 19.97%)

#### 6. 👥 User Management
- Tambah kasir baru
- Edit data user
- Nonaktifkan user (jangan hapus!)

---

## ⚠️ Hal Penting yang Harus Diketahui

### 1. Backup Otomatis
- **Jadwal:** Setiap hari jam 02:00 dini hari
- **Lokasi:** Folder `backups/`
- **Format:** `kedai_kopi_YYYYMMDD_HHMMSS.sql`
- **Simpan ke Google Drive/Flash Disk seminggu sekali!**

### 2. Notifikasi Otomatis
Sistem akan otomatis kirim notifikasi:
- ⚠️ **Stok Menipis:** Via email & Telegram
- 💰 **Transaksi Besar:** (>100K) via Telegram
- 📊 **Laporan Harian:** Email jam 20:00

### 3. Stok Otomatis Berkurang
- Saat transaksi selesai, stok bahan otomatis berkurang
- Sesuai resep yang sudah diset di produk
- **PENTING:** Pastikan resep produk sudah benar!

### 4. Upload Gambar Produk
- Format: JPG, PNG, WEBP
- Ukuran max: 5MB
- Gambar otomatis dioptimasi sistem
- Disimpan di MinIO (object storage)

---

## 🚨 Troubleshooting (Pemecahan Masalah)

### Sistem Tidak Bisa Dibuka

**Masalah:** Browser tidak bisa buka `http://localhost`

**Solusi:**
```bash
# 1. Cek apakah Docker running
docker ps

# 2. Jika tidak ada container, start semua
docker-compose up -d

# 3. Tunggu 1-2 menit, coba lagi
```

### Lupa Password

**Untuk reset password owner:**
```bash
# Buka terminal/command prompt
cd C:\Users\ASUS\PiplProgres

# Reset password owner
docker exec -i kedai-kopi-mysql mysql -uroot -prootpassword123 kedai_kopi -e "UPDATE users SET password='$2b$12$YourNewHashedPassword' WHERE username='owner'"

# Atau buat user baru
docker exec -i kedai-kopi-mysql mysql -uroot -prootpassword123 kedai_kopi -e "INSERT INTO users (username, password, full_name, email, role, is_active) VALUES ('backup_admin', '$2b$12$...', 'Backup Admin', 'backup@kedaikopi.com', 'admin', 1)"
```

**Hubungi developer untuk reset password!**

### Gambar Produk Tidak Muncul

**Solusi:**
```bash
# 1. Cek MinIO running
docker ps | grep minio

# 2. Restart MinIO
docker-compose restart minio

# 3. Tunggu 30 detik, refresh browser
```

### Transaksi Midtrans Gagal

**Penyebab:** Belum setup Midtrans atau mode Sandbox

**Solusi:**
- Pastikan sudah daftar di https://midtrans.com
- Dapatkan Server Key & Client Key
- Update di file `.env`
- Restart system

---

## 📞 Kontak Support

### Developer
- **Nama:** [Nama Developer]
- **WhatsApp:** [Nomor WA]
- **Email:** [Email Developer]

### Support Hours
- **Senin - Jumat:** 09:00 - 17:00
- **Sabtu:** 09:00 - 12:00
- **Minggu/Libur:** Emergency only

### Response Time
- **Critical (sistem mati):** < 2 jam
- **High (fitur error):** < 24 jam
- **Medium (pertanyaan):** < 48 jam
- **Low (request fitur):** 1-2 minggu

---

## 🔧 Maintenance Rutin

### Harian
- ✅ Cek dashboard pagi hari
- ✅ Review transaksi kemarin
- ✅ Cek stok menipis

### Mingguan
- ✅ Backup manual ke flash disk
- ✅ Review laporan penjualan
- ✅ Update stok bahan

### Bulanan
- ✅ Review prediksi vs actual
- ✅ Generate laporan bulanan
- ✅ Update harga produk (jika perlu)
- ✅ Cleanup data lama (>1 tahun)

---

## 📚 Dokumentasi Lengkap

File dokumentasi yang tersedia:
- `README.md` - Overview sistem
- `QUICKSTART.md` - Panduan cepat mulai
- `SOFTWARE_SPECIFICATION.md` - Spesifikasi teknis
- `MINIO_SETUP.md` - Setup storage gambar
- `MIDTRANS_SETUP.md` - Setup payment gateway
- `TROUBLESHOOTING.md` - Pemecahan masalah
- `API_DOCS.md` - Dokumentasi API (untuk developer)

---

## ⚖️ Hak dan Kewajiban

### Hak Pemilik Toko
- ✅ Menggunakan sistem tanpa batas waktu
- ✅ Mendapat update gratis selama 1 tahun
- ✅ Support teknis via WA/Email
- ✅ Source code lengkap

### Kewajiban Pemilik Toko
- ⚠️ JANGAN ubah konfigurasi tanpa konsultasi developer
- ⚠️ JANGAN share kredensial ke pihak lain
- ⚠️ WAJIB backup data rutin
- ⚠️ Bayar biaya maintenance (jika ada perjanjian)

### Garansi
- **Periode:** 3 bulan dari serah terima
- **Coverage:** Bug fixing & minor adjustment
- **Tidak termasuk:** 
  - Kerusakan hardware
  - Human error (salah input data)
  - Request fitur baru
  - Training ulang user

---

## ✍️ Tanda Tangan Serah Terima

### Yang Menyerahkan (Developer)
```
Nama    : _________________________
Tanggal : _________________________
TTD     : _________________________
```

### Yang Menerima (Pemilik Toko)
```
Nama    : _________________________
Tanggal : _________________________
TTD     : _________________________
```

---

**Terima kasih telah mempercayakan sistem ini kepada kami!**  
**Semoga Kedai Kopi Batman Batu 9 semakin maju dan berkembang! ☕**

---

**Dokumen ini adalah bagian resmi dari serah terima sistem.**  
**Simpan baik-baik untuk referensi di masa mendatang.**
