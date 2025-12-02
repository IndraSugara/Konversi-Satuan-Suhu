# Dokumentasi Alur Data & Proses Sistem

## 1. Pendahuluan

Sistem terdiri dari beberapa microservice yang berkolaborasi:

- Auth Service (`auth_service`): Registrasi, Login, JWT issuance, Refresh, Logout, Verify.
- Profile Service (`profile_service`): Manajemen profil user (name, bio, contact, social_links, avatar_url) + publish event `profile.updated`.
- Portfolio Service (`portfolio_service`): CRUD proyek (title, description, tags, link, thumbnail_url) + publish event `project.created|updated|deleted`.
- Media Service (`media_service`): Upload file gambar ke MinIO, simpan metadata, publish event `media.uploaded`.
- Worker Thumbnailer (`worker_thumbnailer`): Konsumsi `media.uploaded`, generate thumbnail, update proyek via API.
- Search Service (`search_service`): Index proyek (RabbitMQ consumer untuk project/profile events), endpoint pencarian dan suggestion.
- Infrastruktur: PostgreSQL, RabbitMQ, MinIO, Elasticsearch, Nginx reverse proxy.

Semua komunikasi antar service untuk identitas user menggunakan JWT (Bearer token). Sinkronisasi data ke mesin pencari dan thumbnail berlangsung asinkron melalui RabbitMQ.

## 2. Komponen & Queue

| Komponen           | Peran                      | Queue yang digunakan                        |
| ------------------ | -------------------------- | ------------------------------------------- |
| Auth Service       | Otentikasi & token         | -                                           |
| Profile Service    | Update profil user         | `profile.events` (producer)                 |
| Portfolio Service  | CRUD proyek                | `project.events` (producer)                 |
| Media Service      | Upload gambar              | `media.events` (producer)                   |
| Worker Thumbnailer | Generate thumbnail         | Konsumsi `media.events`                     |
| Search Service     | Index proyek & update nama | Konsumsi `project.events`, `profile.events` |

## 3. Entitas Data & Tabel

### 3.1 users (Auth Service)

Fields: `id (UUID)`, `username`, `email`, `password_hash`, `created_at`.
Digunakan lintas service (JOIN di profile & project).

### 3.2 refresh_tokens (Auth Service)

Fields: `id`, `user_id`, `token`, `expires_at`, `created_at`.
Untuk mekanisme refresh access token.

### 3.3 profiles (Profile Service)

Fields: `user_id (PK)`, `name`, `bio`, `contact`, `social_links (JSONB)`, `avatar_url`, `created_at`, `updated_at`.
Event `profile.updated` diterbitkan saat create/update profil.

### 3.4 projects (Portfolio Service)

Fields: `id (UUID)`, `user_id`, `title`, `description`, `tags (JSONB)`, `link`, `thumbnail_url`, `created_at`, `updated_at`.
Setiap perubahan memicu event untuk indexing.

### 3.5 media_files (Media Service)

Fields: `id`, `user_id`, `project_id (nullable)`, `filename`, `original_filename`, `file_path`, `file_url`, `file_size`, `mime_type`, `created_at`.
Upload memicu event `media.uploaded`.

### 3.6 Index Elasticsearch (Search Service)

Document fields: `project_id`, `user_id`, `username (display name)`, `title`, `description`, `tags[]`, `thumbnail_url`, `created_at`, `updated_at`.

## 4. Autentikasi (Registrasi & Login)

### 4.1 Registrasi

1. Client POST `/auth/register` dengan JSON `{username, email, password}`.
2. Validasi panjang password & unik (username/email).
3. Hash password (bcrypt) lalu simpan ke `users`.
4. Response: `201 { user_id, message }`.

### 4.2 Login

1. Client POST `/auth/login` dengan `{email, password}`.
2. Ambil user by email, verifikasi bcrypt.
3. Generate `access_token (JWT HS256)` + `refresh_token (UUID disimpan di refresh_tokens)`.
4. Response: `200 { access_token, refresh_token, user {id, username, email} }`.

Contoh Response Login:

```json
{
  "access_token": "<JWT>",
  "refresh_token": "b5d1c9b4-...",
  "user": { "id": "uuid", "username": "alice", "email": "alice@example.com" }
}
```

### 4.3 Refresh Token

1. Client POST `/auth/refresh` dengan `{refresh_token}`.
2. Validasi token ada & belum expired.
3. Generate access token baru.
4. Response: `{ access_token }`.

### 4.4 Logout

1. Client POST `/auth/logout` dengan header Bearer + body `{refresh_token}`.
2. Hapus row `refresh_tokens` sesuai user + token.
3. Response: `200 { message }`.

### 4.5 Verifikasi Antar Service

Service lain memanggil `/auth/verify` (Bearer) untuk memastikan token valid (opsional jika mereka decode langsung menggunakan shared `JWT_SECRET`).

### 4.6 Flow Ringkas

```
[Client] --register--> [Auth]
[Client] --login--> [Auth] --issue JWT/Refresh--> [Client stores]
[Client] --Bearer--> [Profile/Portfolio/Media/Search] --decode--> allow/deny
[Client] --refresh--> [Auth] --new access--> [Client]
[Client] --logout--> [Auth] --invalidate refresh--> DONE
```

## 5. Manajemen Profil

### 5.1 Ambil Profil Sendiri

GET `/profile/me` (Bearer). JOIN `users` + `profiles`. Jika belum ada profile row, nilai profil bernilai null.

### 5.2 Update Profil

PUT `/profile/me` body misal:

```json
{
  "name": "Alice Tan",
  "bio": "Software Engineer",
  "contact": "alice@corp.com",
  "social_links": { "github": "alice", "linkedin": "alice-t" },
  "avatar_url": "/media/uploads/<path>"
}
```

- Jika belum ada row → INSERT.
- Jika ada → UPDATE kolom yang diberikan.
- Publish event RabbitMQ `profile.events` dengan payload:

```json
{
  "event_type": "profile.updated",
  "data": { "user_id": "uuid", "username": "alice", "name": "Alice Tan" },
  "timestamp": "2025-12-02T...Z"
}
```

### 5.3 Dampak ke Search

Search Service consumer `profile.events` → jalankan `update_user_projects_sync`: ubah field `username` (display name) semua dokumen proyek user agar pencarian menampilkan nama terbaru.

### 5.4 Flow Ringkas

```
Client --PUT profile--> Profile Service --DB upsert--> Publish profile.updated --> RabbitMQ --> Search Service consumer --> Update semua project docs
```

## 6. CRUD Proyek Portofolio

### 6.1 Create

POST `/projects` (Bearer): `{title, description?, tags?[], link?, thumbnail_url?}`.

- Simpan ke `projects` (JSONB tags).
- Ambil `username` dari tabel `users` (bukan dari profile; nama tampilan bisa diperbarui nanti via event).
- Publish event `project.created`:

```json
{
  "event_type": "project.created",
  "data": {
    "project_id": "uuid",
    "user_id": "uuid",
    "username": "alice",
    "title": "My App",
    "description": "Desc",
    "tags": ["python", "flask"],
    "thumbnail_url": ""
  },
  "timestamp": "..."
}
```

### 6.2 Read

GET `/projects/{project_id}` → JOIN `users` untuk `username`.
GET `/projects/user/{user_id}` → List proyek user.

### 6.3 Update

PUT `/projects/{project_id}` (Bearer, owner only). Partial update dengan COALESCE. Publish `project.updated` struktur sama.

### 6.4 Delete

DELETE `/projects/{project_id}` (Bearer, owner). Publish `project.deleted`:

```json
{ "event_type": "project.deleted", "data": { "project_id": "uuid" } }
```

### 6.5 Reindex Massal (Admin)

POST `/admin/reindex-projects` → iterasi semua proyek lalu publish kembali `project.created` untuk rebuild index Elasticsearch.

### 6.6 Flow Ringkas

```
Create/Update/Delete --> Portfolio Service DB --> Publish event project.* --> RabbitMQ --> Search Service consumer --> Index / Update / Delete document
```

## 7. Upload Gambar & Thumbnail Otomatis

### 7.1 Upload

POST multipart `/media/upload` (Bearer) fields: `file`, optional `project_id`.
Langkah:

1. Validasi ukuran & ekstensi (<=5MB, tipe diperbolehkan).
2. Generate `file_id` + path `uploads/<user_id>/<uuid>.<ext>`.
3. Upload ke MinIO bucket `media-files`.
4. Simpan metadata ke `media_files`.
5. Publish event `media.uploaded`:

```json
{
  "event_type": "media.uploaded",
  "data": {
    "file_id": "uuid",
    "path": "uploads/<user>/<uuid>.png",
    "owner_id": "uuid",
    "project_id": "uuid|null",
    "file_url": "http://host/media/uploads/...",
    "mime_type": "image/png"
  }
}
```

6. Response ke client berisi metadata.

### 7.2 Worker Thumbnailer

- Konsumsi `media.events`.
- Kalau `mime_type` image → download dari MinIO.
- Generate thumbnail (resize dengan PIL ke 300x300, JPEG kualitas 85). Simpan ke path `thumbnails/<user>/<uuid>_thumb.jpg`.
- Upload thumbnail ke MinIO.
- Jika `project_id` ada → PUT ke Portfolio Service `/projects/{id}/thumbnail` body `{thumbnail_url}`.
- Portfolio Service update DB & publish lagi `project.updated` (memicu reindex thumbnail di search).

### 7.3 Flow Ringkas

```
Client upload --> Media Service (DB + MinIO) --> Publish media.uploaded --> Worker consume --> Generate thumbnail --> Upload thumbnail --> Update proyek --> Publish project.updated --> Search reindex project
```

## 8. Fitur Pencarian Proyek

### 8.1 Indexing Sumber Data

- `project.created` / `project.updated` → index/replace doc di Elasticsearch.
- `project.deleted` → hapus doc.
- `profile.updated` → update semua doc user (username field).

### 8.2 Query Pencarian

GET `/search?query=...&tags=tag1,tag2&page=1&size=20`.

- Query builder:
  - `multi_match` pada `title^3`, `description`, `username^2` (boost title & username).
  - Filter tags dengan `terms` jika diberikan.
  - Sort: `_score` desc lalu `updated_at` desc.
- Pagination: `from = (page-1)*size`.
- Response contoh:

```json
{
  "results": [
    {
      "project_id": "uuid",
      "title": "My App",
      "tags": ["python"],
      "username": "Alice Tan",
      "score": 4.23
    }
  ],
  "total": 37,
  "page": 1,
  "size": 20,
  "pages": 2
}
```

### 8.3 Suggestion Endpoint

GET `/search/suggest?query=py` → mengembalikan kandidat judul & tags paling relevan (size 5).

### 8.4 Flow Ringkas

```
Project/Profile event --> Search consumer --> Update index --> User search --> Elasticsearch query --> Response terstruktur
```

## 9. Contoh Payload Ringkas

### 9.1 Create Project Request

```json
{
  "title": "Expense Tracker",
  "description": "A simple finance app",
  "tags": ["react", "flask"],
  "link": "https://example.com"
}
```

### 9.2 Project Created Event (dispatched)

```json
{
  "event_type": "project.created",
  "data": {
    "project_id": "b3f...",
    "user_id": "2c1...",
    "username": "alice",
    "title": "Expense Tracker",
    "description": "A simple finance app",
    "tags": ["react", "flask"],
    "thumbnail_url": null
  },
  "timestamp": "2025-12-02T12:34:56Z"
}
```

### 9.3 media.uploaded Event

```json
{
  "event_type": "media.uploaded",
  "data": {
    "file_id": "9af...",
    "path": "uploads/2c1/9af.png",
    "owner_id": "2c1...",
    "project_id": "b3f...",
    "file_url": "http://localhost/media/uploads/2c1/9af.png",
    "mime_type": "image/png"
  }
}
```

### 9.4 profile.updated Event

```json
{
  "event_type": "profile.updated",
  "data": { "user_id": "2c1...", "username": "alice", "name": "Alice Tan" },
  "timestamp": "..."
}
```

## 10. Keamanan & Validasi

- **JWT**: Semua endpoint yang mengubah data dilindungi oleh Bearer token. Dekode dengan `JWT_SECRET`, cek expiry.
- **Ownership Checks**: Update/Delete proyek memverifikasi `user_id` sama dengan pemilik proyek; delete media memverifikasi pemilik file.
- **Password Storage**: Hash dengan bcrypt (salt random).
- **Refresh Token**: Disimpan di DB; dapat dicabut (delete row) saat logout.
- **File Upload Validation**: Ukuran maksimum, ekstensi whitelisted, secure filename.
- **Event Reliability**: RabbitMQ durable queue + pesan persistent (`delivery_mode=2`). Consumer melakukan `basic_ack` hanya jika sukses; kegagalan memicu `basic_nack` dengan requeue (search service) atau drop setelah retry (worker thumbnailer).
- **Idempotency (Search)**: Indexing menggunakan `project_id` sebagai `_id` sehingga update menimpa state lama secara deterministik.

## 11. Error Handling Umum

| Layer             | Strategi                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| Auth              | 400 untuk field hilang, 401 kredensial salah, 409 duplikat, 500 umum.                                 |
| Profile/Portfolio | 401 token invalid, 403 bukan pemilik, 404 tidak ditemukan, rollback transaksi pada exception.         |
| Media             | Validasi ukuran/tipe, 500 saat gagal MinIO, skip non-image di worker.                                 |
| Worker            | Retry dengan exponential backoff (2^n detik) sampai MAX_RETRIES; gagal final di-nack (tanpa requeue). |
| Search            | Jika ES down → 503; event tetap diterima tapi indexing gagal → pesan direqueue.                       |

## 12. Ringkasan End-to-End Alur Utama

### 12.1 Registrasi → Buat Proyek → Upload Gambar → Thumbnail → Pencarian

```
Client register/login --> JWT
Client create project --> DB save + project.created --> RabbitMQ --> Search index
Client upload image (with project_id) --> MinIO + media.uploaded --> RabbitMQ --> Worker --> Generate thumbnail + update project --> project.updated --> RabbitMQ --> Search reindex
Client search --> /search --> Elasticsearch hasil
```

### 12.2 Update Profil → Propagasi Nama di Pencarian

```
Client update profile --> profile.updated --> RabbitMQ --> Search consumer --> update_by_query semua doc user --> Pencarian menampilkan nama baru
```

## 13. Catatan Pengembangan & Perluasan

- Dapat menambah event untuk notifikasi (misal `project.starred`).
- Bisa menambahkan indexing incremental untuk likes/comments di masa depan.
- Avatar user saat ini tidak otomatis mengupdate semua project (kecuali nama); dapat ditambahkan jika diperlukan.

## 14. Checklist Fitur Diminta

- Registrasi & Login (JWT) → Bagian 4 ✅
- Manajemen Profil → Bagian 5 ✅
- CRUD Proyek → Bagian 6 ✅
- Upload Gambar + Thumbnail async → Bagian 7 ✅
- Pencarian Proyek (nama/tag) → Bagian 8 ✅
- Alur data integrasi event → Bagian 12 ✅

---

Terakhir diperbarui: 2025-12-02
