# Normalisasi Database Sistem Kedai Kopi

## Overview

Database sistem menggunakan **MySQL 8.0** dengan normalisasi hingga **3NF (Third Normal Form)** untuk menghindari redundansi data dan menjaga integritas data.

---

## Tahapan Normalisasi

### Bentuk Tidak Normal (Unnormalized Form - UNF)

**Tabel Transaksi Sebelum Normalisasi:**

| transaction_id | cashier_name | customer_name | products                    | quantities | prices              | total | payment_method | created_at |
| -------------- | ------------ | ------------- | --------------------------- | ---------- | ------------------- | ----- | -------------- | ---------- |
| 1              | Admin        | John          | Espresso, Latte             | 2, 1       | 20000, 22000        | 62000 | cash           | 2025-12-10 |
| 2              | Kasir1       | Jane          | Cappuccino, Mocha, Espresso | 1, 2, 1    | 20000, 25000, 20000 | 90000 | emoney         | 2025-12-10 |

**Masalah:**

- Multi-valued attributes (products, quantities, prices dalam satu kolom)
- Redundansi data produk di setiap transaksi
- Sulit untuk query produk tertentu
- Tidak bisa maintain data produk secara konsisten

---

### Bentuk Normal Pertama (First Normal Form - 1NF)

**Aturan 1NF:**

- Setiap kolom harus atomic (tidak ada multi-valued)
- Setiap baris harus unik (primary key)
- Tidak ada repeating groups

**Hasil 1NF:**

**Tabel: transactions**
| id | transaction_code | cashier_id | cashier_name | customer_name | total_amount | payment_method | created_at |
|---|---|---|---|---|---|---|---|
| 1 | TRX-001 | 1 | Admin | John | 62000 | cash | 2025-12-10 |
| 2 | TRX-002 | 2 | Kasir1 | Jane | 90000 | emoney | 2025-12-10 |

**Tabel: transaction_items**
| id | transaction_id | product_name | quantity | price | subtotal | created_at |
|---|---|---|---|---|---|---|
| 1 | 1 | Espresso | 2 | 20000 | 40000 | 2025-12-10 |
| 2 | 1 | Latte | 1 | 22000 | 22000 | 2025-12-10 |
| 3 | 2 | Cappuccino | 1 | 20000 | 20000 | 2025-12-10 |
| 4 | 2 | Mocha | 2 | 25000 | 50000 | 2025-12-10 |
| 5 | 2 | Espresso | 1 | 20000 | 20000 | 2025-12-10 |

**Perbaikan:**
✅ Setiap kolom atomic
✅ Ada primary key (id)
✅ Tidak ada repeating groups

**Masalah yang Tersisa:**

- Masih ada redundansi `cashier_name` dan `product_name`
- Jika nama produk/kasir berubah, harus update banyak record

---

### Bentuk Normal Kedua (Second Normal Form - 2NF)

**Aturan 2NF:**

- Sudah memenuhi 1NF
- Tidak ada partial dependency (non-key attributes harus fully dependent pada primary key)

**Hasil 2NF:**

**Tabel: users** (untuk kasir)
| id | username | password | full_name | email | role | is_active | created_at | last_login |
|---|---|---|---|---|---|---|---|---|
| 1 | admin | $2b$12... | Administrator | admin@kedaikopi.com | admin | true | 2025-11-19 | 2025-12-10 |
| 2 | kasir1 | $2b$12... | Kasir Satu | kasir1@kedaikopi.com | cashier | true | 2025-11-20 | 2025-12-10 |

**Tabel: products**
| id | name | category | price | description | image_url | is_available | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|
| 1 | Espresso | Kopi | 20000 | Single shot espresso | null | true | 2025-11-29 | 2025-11-29 |
| 2 | Latte | Kopi | 22000 | Espresso dengan susu | null | true | 2025-11-29 | 2025-11-29 |
| 3 | Cappuccino | Kopi | 20000 | Espresso dengan foam | null | true | 2025-11-29 | 2025-11-29 |

**Tabel: transactions** (diperbarui)
| id | transaction_code | cashier_id | customer_name | total_amount | payment_method | payment_amount | change_amount | status | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | TRX-001 | 1 | John | 62000 | cash | 70000 | 8000 | completed | 2025-12-10 | 2025-12-10 |
| 2 | TRX-002 | 2 | Jane | 90000 | emoney | 90000 | 0 | completed | 2025-12-10 | 2025-12-10 |

**Tabel: transaction_items** (diperbarui)
| id | transaction_id | product_id | product_name | quantity | price | subtotal | notes | created_at |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | Espresso | 2 | 20000 | 40000 | null | 2025-12-10 |
| 2 | 1 | 2 | Latte | 1 | 22000 | 22000 | null | 2025-12-10 |
| 3 | 2 | 3 | Cappuccino | 1 | 20000 | 20000 | null | 2025-12-10 |

**Perbaikan:**
✅ Tidak ada partial dependency
✅ `cashier_name` diganti dengan `cashier_id` (foreign key ke users)
✅ `product_name` tetap ada untuk historical record (harga & nama saat transaksi)
✅ Ada `product_id` sebagai foreign key ke products

**Catatan Desain:**

- `product_name` dan `price` di `transaction_items` di-denormalisasi untuk keperluan historical record
- Jika produk dihapus/diganti nama, transaksi lama tetap valid

---

### Bentuk Normal Ketiga (Third Normal Form - 3NF)

**Aturan 3NF:**

- Sudah memenuhi 2NF
- Tidak ada transitive dependency (non-key attributes tidak boleh bergantung pada non-key attributes lain)

**Analisis Transitive Dependencies:**

**Pada tabel products:**

- `category` adalah string literal → Buat tabel categories untuk konsistensi

**Hasil 3NF:**

**Tabel: categories**
| id | name | description | created_at |
|---|---|---|---|
| 1 | Kopi | Minuman berbasis kopi | 2025-11-29 |
| 2 | Non-Kopi | Minuman non-kopi | 2025-11-29 |
| 3 | Makanan | Makanan ringan | 2025-11-29 |

**Tabel: products** (final)
| id | name | category | price | description | image_url | is_available | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|
| 1 | Espresso | Kopi | 20000 | Single shot espresso | null | true | 2025-11-29 | 2025-11-29 |

**Catatan:** Category tetap string untuk fleksibilitas, tapi ada tabel categories untuk referensi.

**Tabel: stocks** (stok bahan baku)
| id | ingredient_name | quantity | unit | minimum_stock | price_per_unit | supplier | last_restock | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Kopi Arabica | 5000 | gram | 1000 | 0.15 | Supplier Kopi | 2025-12-10 | 2025-12-10 | 2025-12-10 |
| 2 | Susu | 10000 | ml | 2000 | 0.01 | Supplier Susu | 2025-12-10 | 2025-12-10 | 2025-12-10 |

**Tabel: product_ingredients** (resep produk)
| id | product_id | ingredient_name | quantity | unit | created_at |
|---|---|---|---|---|---|
| 1 | 1 | Kopi Arabica | 18 | gram | 2025-12-10 |
| 2 | 1 | Air | 30 | ml | 2025-12-10 |
| 3 | 2 | Kopi Arabica | 18 | gram | 2025-12-10 |
| 4 | 2 | Susu | 200 | ml | 2025-12-10 |

**Tabel: stock_history** (audit trail stok)
| id | stock_id | change_type | quantity_before | quantity_change | quantity_after | notes | reference_id | created_by | created_at |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | restock | 0 | 5000 | 5000 | Initial stock | null | admin | 2025-12-10 |
| 2 | 1 | usage | 5000 | 36 | 4964 | Transaction usage | TRX-001 | transaction-service | 2025-12-10 |

**Perbaikan:**
✅ Tidak ada transitive dependency
✅ Semua tabel dalam 3NF
✅ Data konsisten dan tidak redundan

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐         ┌──────────────────┐
│     users       │         │   refresh_tokens │
├─────────────────┤         ├──────────────────┤
│ PK id           │────┐    │ PK id            │
│    username     │    │    │ FK user_id       │
│    password     │    │    │    token         │
│    full_name    │    │    │    expires_at    │
│    email        │    │    │    created_at    │
│    role         │    │    └──────────────────┘
│    is_active    │    │
│    created_at   │    │
│    last_login   │    │
└─────────────────┘    │    ┌──────────────────┐
                       └───<│   transactions   │
                            ├──────────────────┤
                            │ PK id            │
                            │    transaction_  │
                            │      code        │
┌─────────────────┐         │ FK cashier_id    │
│   products      │         │    cashier_name  │
├─────────────────┤         │    customer_name │
│ PK id           │────┐    │    total_amount  │
│    name         │    │    │    payment_method│
│    category     │    │    │    payment_amount│
│    price        │    │    │    change_amount │
│    description  │    │    │    status        │
│    image_url    │    │    │    notes         │
│    is_available │    │    │    created_at    │
│    created_at   │    │    │    updated_at    │
│    updated_at   │    │    └──────────────────┘
└─────────────────┘    │              │
       │               │              │
       │               │              ▼
       │               │    ┌──────────────────┐
       │               └───>│ transaction_items│
       │                    ├──────────────────┤
       │                    │ PK id            │
       │                    │ FK transaction_id│
       │                    │ FK product_id    │
       │                    │    product_name  │
       │                    │    quantity      │
       │                    │    price         │
       │                    │    subtotal      │
       │                    │    notes         │
       │                    │    created_at    │
       │                    └──────────────────┘
       │
       │               ┌──────────────────┐
       └──────────────>│product_ingredients│
                       ├──────────────────┤
                       │ PK id            │
                       │ FK product_id    │
                       │    ingredient_   │
                       │      name        │
                       │    quantity      │
                       │    unit          │
                       │    created_at    │
                       └──────────────────┘


┌─────────────────┐         ┌──────────────────┐
│    stocks       │         │  stock_history   │
├─────────────────┤         ├──────────────────┤
│ PK id           │────────<│ PK id            │
│    ingredient_  │         │ FK stock_id      │
│      name       │         │    change_type   │
│    quantity     │         │    quantity_     │
│    unit         │         │      before      │
│    minimum_stock│         │    quantity_     │
│    price_per_   │         │      change      │
│      unit       │         │    quantity_     │
│    supplier     │         │      after       │
│    last_restock │         │    notes         │
│    created_at   │         │    reference_id  │
│    updated_at   │         │    created_by    │
└─────────────────┘         │    created_at    │
                            └──────────────────┘


┌─────────────────┐
│   categories    │
├─────────────────┤
│ PK id           │
│    name         │
│    description  │
│    created_at   │
└─────────────────┘


┌─────────────────┐
│sales_forecasts  │
├─────────────────┤
│ PK id           │
│    forecast_date│
│    predicted_   │
│      revenue    │
│    lower_bound  │
│    upper_bound  │
│    mae          │
│    rmse         │
│    mape         │
│    created_at   │
└─────────────────┘
```

**Relasi:**

- `users` 1:N `transactions` (satu user banyak transaksi)
- `users` 1:N `refresh_tokens` (satu user banyak tokens)
- `transactions` 1:N `transaction_items` (satu transaksi banyak items)
- `products` 1:N `transaction_items` (satu produk di banyak transaksi)
- `products` 1:N `product_ingredients` (satu produk banyak bahan)
- `stocks` 1:N `stock_history` (satu stok banyak history)

---

## Justifikasi Desain Database

### 1. Denormalisasi Terbatas (Controlled Denormalization)

**Kasus: transaction_items**

- Menyimpan `product_name` dan `price` meskipun ada di `products`
- **Alasan:** Historical record harus tetap valid meski produk dihapus/berubah
- **Trade-off:** Sedikit redundansi untuk data integrity

### 2. Soft Delete vs Hard Delete

**Implementasi:**

- User: `is_active` boolean (soft delete)
- Product: `is_available` boolean (soft delete)
- Transaction: Tidak bisa dihapus (audit requirement)

**Alasan:**

- Audit trail requirement
- Referential integrity
- Rollback capability

### 3. Timestamp Tracking

**Semua tabel memiliki:**

- `created_at` - kapan record dibuat
- `updated_at` - kapan record terakhir diupdate (jika applicable)

**Manfaat:**

- Audit trail
- Debugging
- Analytics

### 4. Composite Keys vs Surrogate Keys

**Pilihan: Surrogate Keys (auto-increment id)**

- Lebih simple
- Better performance untuk JOIN
- Lebih flexible untuk perubahan business logic

### 5. Unit Conversion Flexibility

**Kasus: stocks vs product_ingredients**

- Stock: `unit = "kg"`
- Ingredient: `unit = "gram"`
- **Solusi:** Conversion function di application layer
- **Alasan:** Flexibility tanpa constraint di database

---

## Index Strategy

### Primary Indexes (Auto)

```sql
-- Semua tabel memiliki PRIMARY KEY (id)
```

### Secondary Indexes

```sql
-- users
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);

-- products
CREATE INDEX idx_name ON products(name);
CREATE INDEX idx_category ON products(category);

-- transactions
CREATE INDEX idx_transaction_code ON transactions(transaction_code);
CREATE INDEX idx_cashier_id ON transactions(cashier_id);
CREATE INDEX idx_created_at ON transactions(created_at);
CREATE INDEX idx_status ON transactions(status);

-- transaction_items
CREATE INDEX idx_transaction_id ON transaction_items(transaction_id);
CREATE INDEX idx_product_id ON transaction_items(product_id);

-- stocks
CREATE UNIQUE INDEX idx_ingredient_name ON stocks(ingredient_name);

-- stock_history
CREATE INDEX idx_stock_id ON stock_history(stock_id);
CREATE INDEX idx_reference_id ON stock_history(reference_id);

-- sales_forecasts
CREATE INDEX idx_forecast_date ON sales_forecasts(forecast_date);
CREATE INDEX idx_created_at ON sales_forecasts(created_at);
```

**Justifikasi:**

- `idx_username`, `idx_email`: Login queries
- `idx_transaction_code`: Lookup transaksi spesifik
- `idx_created_at`: Range queries untuk reports
- `idx_ingredient_name`: Unique constraint + lookup
- `idx_reference_id`: Audit trail lookup

---

## Constraints & Referential Integrity

### Foreign Key Constraints

```sql
-- transactions
ALTER TABLE transactions
ADD CONSTRAINT fk_transactions_cashier
FOREIGN KEY (cashier_id) REFERENCES users(id)
ON DELETE RESTRICT  -- Tidak bisa hapus user yang punya transaksi
ON UPDATE CASCADE;  -- Update cascade jika id berubah

-- transaction_items
ALTER TABLE transaction_items
ADD CONSTRAINT fk_transaction_items_transaction
FOREIGN KEY (transaction_id) REFERENCES transactions(id)
ON DELETE CASCADE  -- Hapus items jika transaksi dihapus
ON UPDATE CASCADE;

ALTER TABLE transaction_items
ADD CONSTRAINT fk_transaction_items_product
FOREIGN KEY (product_id) REFERENCES products(id)
ON DELETE RESTRICT  -- Tidak bisa hapus produk yang ada di transaksi
ON UPDATE CASCADE;

-- product_ingredients
ALTER TABLE product_ingredients
ADD CONSTRAINT fk_product_ingredients_product
FOREIGN KEY (product_id) REFERENCES products(id)
ON DELETE CASCADE  -- Hapus ingredients jika produk dihapus
ON UPDATE CASCADE;

-- stock_history
ALTER TABLE stock_history
ADD CONSTRAINT fk_stock_history_stock
FOREIGN KEY (stock_id) REFERENCES stocks(id)
ON DELETE CASCADE  -- Hapus history jika stock dihapus
ON UPDATE CASCADE;

-- refresh_tokens
ALTER TABLE refresh_tokens
ADD CONSTRAINT fk_refresh_tokens_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE  -- Hapus tokens jika user dihapus
ON UPDATE CASCADE;
```

### Check Constraints

```sql
-- Pastikan quantity > 0
ALTER TABLE stocks
ADD CONSTRAINT chk_stocks_quantity
CHECK (quantity >= 0);

ALTER TABLE stocks
ADD CONSTRAINT chk_stocks_minimum_stock
CHECK (minimum_stock >= 0);

-- Pastikan price > 0
ALTER TABLE products
ADD CONSTRAINT chk_products_price
CHECK (price > 0);

-- Pastikan payment_amount >= total_amount
ALTER TABLE transactions
ADD CONSTRAINT chk_transactions_payment
CHECK (payment_amount >= total_amount);

-- Pastikan change_amount >= 0
ALTER TABLE transactions
ADD CONSTRAINT chk_transactions_change
CHECK (change_amount >= 0);
```

---

## Data Integrity Rules

### 1. Transaction Atomicity

- Semua operasi transaction menggunakan `BEGIN/COMMIT/ROLLBACK`
- Stock reduction adalah bagian dari transaction

### 2. Consistency

- Foreign key constraints menjaga referential integrity
- Check constraints menjaga business rules

### 3. Isolation

- Transaction isolation level: `READ COMMITTED`
- Mencegah dirty reads tapi allow non-repeatable reads

### 4. Durability

- MySQL InnoDB storage engine
- Auto-commit disabled untuk explicit transaction control

---

## Normalisasi Final Summary

| Tabel               | 1NF | 2NF | 3NF | Keterangan                               |
| ------------------- | --- | --- | --- | ---------------------------------------- |
| users               | ✅  | ✅  | ✅  | Fully normalized                         |
| products            | ✅  | ✅  | ✅  | Fully normalized                         |
| categories          | ✅  | ✅  | ✅  | Fully normalized                         |
| stocks              | ✅  | ✅  | ✅  | Fully normalized                         |
| stock_history       | ✅  | ✅  | ✅  | Fully normalized                         |
| transactions        | ✅  | ✅  | ✅  | Denormalized `cashier_name` for display  |
| transaction_items   | ✅  | ✅  | ⚠️  | Intentional denormalization (historical) |
| product_ingredients | ✅  | ✅  | ✅  | Fully normalized                         |
| refresh_tokens      | ✅  | ✅  | ✅  | Fully normalized                         |
| sales_forecasts     | ✅  | ✅  | ✅  | Fully normalized                         |

**Legend:**

- ✅ Memenuhi normal form
- ⚠️ Intentional denormalization untuk keperluan khusus

---

## Kesimpulan

Database sistem Kedai Kopi telah dinormalisasi hingga **3NF** dengan beberapa **intentional denormalization** untuk:

1. **Historical Data Integrity** - Transaksi tetap valid meski produk berubah
2. **Performance Optimization** - Mengurangi JOIN yang kompleks
3. **User Experience** - Display name langsung tanpa JOIN

Desain ini menyeimbangkan antara **data integrity**, **performance**, dan **maintainability**.
