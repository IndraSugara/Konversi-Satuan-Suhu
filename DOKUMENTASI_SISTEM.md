# DOKUMENTASI SISTEM PORTFOLIO TERDISTRIBUSI

**Versi**: 1.0  
**Tanggal**: 1 Desember 2025  
**Status**: Production Ready

---

## 📋 DAFTAR ISI

1. [Ringkasan Sistem](#ringkasan-sistem)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Topologi Multi-Laptop](#topologi-multi-laptop)
4. [Komponen Sistem](#komponen-sistem)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Setup & Instalasi](#setup--instalasi)
8. [Konfigurasi](#konfigurasi)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

##  RINGKASAN SISTEM

### Deskripsi
Platform portfolio terdistribusi berbasis microservices yang memungkinkan pengguna untuk membuat, berbagi, dan berkolaborasi pada project portfolio. Sistem ini didesain untuk deployment multi-laptop dengan komunikasi antar-service melalui REST API dan message broker.

### Fitur Utama
-  **Autentikasi & Otorisasi**: JWT-based authentication dengan refresh token
-  **Manajemen Profile**: User profiles dengan avatar upload
-  **Portfolio Projects**: CRUD projects dengan media upload (gambar/video)
-  **Media Processing**: Automatic thumbnail generation untuk gambar
-  **Search Engine**: Full-text search menggunakan Elasticsearch
-  **Likes & Comments**: Engagement system di external service (PHP)
-  **Real-time Analytics**: Project views dan statistics
-  **Responsive UI**: Mobile-friendly frontend

### Teknologi Stack

**Backend:**
- Python 3.11 + Flask
- PostgreSQL 15
- RabbitMQ (Message Broker)
- MinIO (Object Storage)
- Elasticsearch 8.11
- Nginx (Reverse Proxy)

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5 & CSS3
- Responsive Design

**External Services:**
- PHP 8.x (Likes & Comments Service)
- Stream Chat API (Coming Soon)

---

##  ARSITEKTUR SISTEM

### Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│                   (HTML/CSS/JS - Port 8080)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX REVERSE PROXY                          │
│                       (Port 80)                                 │
│  Routes:                                                        │
│    /api/auth/* → Auth Service                                  │
│    /api/profile/* → Profile Service                            │
│    /api/portfolio/* → Portfolio Service                        │
│    /api/media/* → Media Service                                │
│    /api/search/* → Search Service                              │
│    /api/likes/* → External PHP Service (192.168.1.17:8080)    │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Auth Service │ │Profile Service│ │Portfolio Srv │
│  (Port 8001) │ │  (Port 8002)  │ │  (Port 8003) │
└──────┬───────┘ └──────┬────────┘ └──────┬───────┘
       │                │                  │
       ├────────────────┴──────────────────┤
       │                                   │
       ▼                                   ▼
┌──────────────┐                    ┌──────────────┐
│ Media Service│                    │Search Service│
│  (Port 8004) │                    │  (Port 8005) │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       ▼                                   ▼
┌──────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │PostgreSQL│ │ RabbitMQ │ │  MinIO   │        │
│  │  :5432   │ │  :5672   │ │  :9000   │        │
│  └──────────┘ └──────────┘ └──────────┘        │
│  ┌──────────────────────────────────┐          │
│  │      Elasticsearch :9200         │          │
│  └──────────────────────────────────┘          │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│         BACKGROUND WORKERS                       │
│  ┌──────────────────────────────────┐           │
│  │   Thumbnailer Worker             │           │
│  │   (Konsumsi RabbitMQ Queue)      │           │
│  └──────────────────────────────────┘           │
└──────────────────────────────────────────────────┘
```

### Pola Komunikasi

#### 1. **Synchronous (REST API)**
- Frontend ↔ All Services
- Service ↔ Database
- Auth verification antar services

#### 2. **Asynchronous (Message Queue)**
- Portfolio Service → RabbitMQ → Thumbnailer Worker
- Search Service → Elasticsearch indexing
- Event-driven updates

#### 3. **Object Storage**
- Media Service → MinIO (upload/download)
- Thumbnailer Worker → MinIO (thumbnail storage)

---

##  TOPOLOGI MULTI-LAPTOP

### Deployment Configuration

```
┌──────────────────────────────────────────────────────┐
│         LAPTOP A (10.132.78.141)                     │
│  ┌────────────────────────────────────────────┐     │
│  │  Core Infrastructure                       │     │
│  │  - PostgreSQL Database (:5432)             │     │
│  │  - RabbitMQ (:5672)                        │     │
│  │  - Auth Service (:8001)                    │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
                        ▲
                        │ Network Connection
                        │ (Direct IP: 192.168.1.5 or 10.132.78.141)
                        │
┌──────────────────────────────────────────────────────┐
│         LAPTOP B (192.168.1.17)                      │
│  ┌────────────────────────────────────────────┐     │
│  │  External Services (PHP)                   │     │
│  │  - Likes & Comments Service (:8080)        │     │
│  │  - PostgreSQL Client (connects to A)       │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
                        ▲
                        │ Network Connection
                        │ (Proxied via Nginx)
                        │
┌──────────────────────────────────────────────────────┐
│         LAPTOP C (Current - Main Server)             │
│  ┌────────────────────────────────────────────┐     │
│  │  Application Layer                         │     │
│  │  - Frontend (:8080)                        │     │
│  │  - Nginx Proxy (:80)                       │     │
│  │  - Profile Service (:8002)                 │     │
│  │  - Portfolio Service (:8003)               │     │
│  │  - Media Service (:8004)                   │     │
│  │  - Search Service (:8005)                  │     │
│  │  - MinIO Storage (:9000)                   │     │
│  │  - Elasticsearch (:9200)                   │     │
│  │  - Thumbnailer Worker                      │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  Ngrok Tunnel (Optional):                           │
│  https://xxxxx.ngrok-free.dev → localhost:80        │
└──────────────────────────────────────────────────────┘
```

### Network Configuration

#### Laptop A (Infrastructure)
```bash
IP: 10.132.78.141 (Internal Network)
Public: 192.168.1.5 (Local Network)

Open Ports:
- 5432 (PostgreSQL)
- 5672 (RabbitMQ)
- 15672 (RabbitMQ Management)
- 8001 (Auth Service)

Firewall Rules:
- Allow incoming: 5432, 5672, 8001
- Allow from: Laptop B, Laptop C
```

#### Laptop B (External PHP Service)
```bash
IP: 192.168.1.17

Open Ports:
- 8080 (PHP Service)

Requirements:
- PHP 8.x with curl extension
- PostgreSQL client library
- Network access to Laptop A:5432
```

#### Laptop C (Main Application)
```bash
IP: 192.168.x.x (Dynamic)

Open Ports:
- 80 (Nginx)
- 8080 (Frontend)
- 8002-8005 (Services)
- 9000 (MinIO)

External Access:
- Ngrok tunnel on port 80
- Domain: https://xxxxx.ngrok-free.dev
```

---

##  KOMPONEN SISTEM

### 1. Auth Service (Port 8001)

**Tanggung Jawab:**
- User registration & login
- JWT token generation & validation
- Refresh token management
- User data management

**Teknologi:**
- Flask (Python)
- bcrypt (password hashing)
- PyJWT (token generation)
- PostgreSQL

**Endpoints:**
```
POST   /auth/register          - Register user baru
POST   /auth/login             - Login user
POST   /auth/refresh           - Refresh access token
POST   /auth/logout            - Logout user
GET    /auth/verify            - Verify JWT token (untuk middleware)
GET    /api/users              - List all users (untuk chat sync)
GET    /api/user/:id           - Get user by ID
```

**Environment Variables:**
```env
DATABASE_URL=postgresql://admin:admin123@10.132.78.141:5432/distributed_system
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRATION=86400
CHAT_API_KEY=secure-chat-api-key
```

---

### 2. Profile Service (Port 8002)

**Tanggung Jawab:**
- User profile management (name, bio, contact)
- Avatar upload & management
- Social links management
- Profile validation

**Teknologi:**
- Flask (Python)
- PostgreSQL
- File upload handling

**Endpoints:**
```
GET    /profile/me             - Get current user profile
GET    /profile/user/:user_id  - Get profile by user ID
PUT    /profile/update         - Update profile
POST   /profile/avatar         - Upload avatar
GET    /health                 - Health check
```

**Environment Variables:**
```env
DATABASE_URL=postgresql://admin:admin123@postgres:5432/distributed_system
JWT_SECRET=your-super-secret-jwt-key-change-in-production
AUTH_SERVICE_URL=http://auth_service:8000
```

---

### 3. Portfolio Service (Port 8003)

**Tanggung Jawab:**
- Project CRUD operations
- Project ownership management
- Tag management
- Event publishing ke RabbitMQ

**Teknologi:**
- Flask (Python)
- PostgreSQL
- RabbitMQ (pika)

**Endpoints:**
```
POST   /projects               - Create project
GET    /projects               - List all projects (with pagination)
GET    /projects/:id           - Get project by ID
PUT    /projects/:id           - Update project
DELETE /projects/:id           - Delete project
GET    /projects/user/:user_id - Get user's projects
GET    /search                 - Search projects
GET    /health                 - Health check
```

**Environment Variables:**
```env
DATABASE_URL=postgresql://admin:admin123@postgres:5432/distributed_system
JWT_SECRET=your-super-secret-jwt-key-change-in-production
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
```

**RabbitMQ Events:**
- Queue: `thumbnail_queue`
- Event: Project created with images
- Payload: `{project_id, user_id, media_files: [{id, url, type}]}`

---

### 4. Media Service (Port 8004)

**Tanggung Jawab:**
- File upload (images, videos)
- MinIO integration
- Media metadata management
- File deletion

**Teknologi:**
- Flask (Python)
- MinIO client
- PostgreSQL
- Pillow (image validation)

**Endpoints:**
```
POST   /upload                 - Upload single file
POST   /upload/multiple        - Upload multiple files
GET    /file/:file_id          - Get file metadata
DELETE /file/:file_id          - Delete file
GET    /uploads/:path          - Serve file from MinIO
GET    /health                 - Health check
```

**Environment Variables:**
```env
DATABASE_URL=postgresql://admin:admin123@postgres:5432/distributed_system
JWT_SECRET=your-super-secret-jwt-key-change-in-production
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
MINIO_ENDPOINT=minio:9000
MINIO_PUBLIC_URL=http://localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin123
MINIO_BUCKET=media-files
```

**Supported Formats:**
- Images: jpg, jpeg, png, gif, webp
- Videos: mp4, webm, mov
- Max size: 100MB

---

### 5. Search Service (Port 8005)

**Tanggung Jawab:**
- Elasticsearch indexing
- Full-text search
- Auto-complete suggestions
- Search analytics

**Teknologi:**
- Flask (Python)
- Elasticsearch
- RabbitMQ consumer

**Endpoints:**
```
GET    /search                 - Search projects
GET    /search/suggestions     - Auto-complete suggestions
POST   /index/project/:id      - Manual index project
DELETE /index/project/:id      - Remove from index
GET    /health                 - Health check
```

**Environment Variables:**
```env
ELASTICSEARCH_URL=http://elasticsearch:9200
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
```

**Search Features:**
- Full-text search on title, description, tags
- Fuzzy matching
- Pagination
- Relevance scoring

---

### 6. Thumbnailer Worker (Background)

**Tanggung Jawab:**
- Generate thumbnails dari gambar
- Update project dengan thumbnail URLs
- Handle queue dari RabbitMQ

**Teknologi:**
- Python
- Pillow (image processing)
- MinIO client
- RabbitMQ consumer

**Workflow:**
1. Listen to `thumbnail_queue`
2. Download image dari MinIO
3. Generate thumbnail (300x300, 800x800)
4. Upload thumbnail ke MinIO
5. Update project di Portfolio Service

**Environment Variables:**
```env
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin123
MINIO_BUCKET=media-files
PORTFOLIO_SERVICE_URL=http://portfolio_service:8000
```

---

### 7. External Service - Likes & Comments (PHP)

**Lokasi:** Laptop B (192.168.1.17:8080)

**Tanggung Jawab:**
- Like/unlike projects
- Comment CRUD
- Statistics aggregation
- Top liked/commented projects

**Teknologi:**
- PHP 8.x
- PostgreSQL
- cURL (untuk auth verification)

**Endpoints:**
```
# Likes
GET    /likes/project/:id         - Get likes count
POST   /likes/toggle/:id          - Toggle like
GET    /likes/check/:id           - Check if user liked (requires auth)
GET    /likes/user                - Get user's liked projects (requires auth)

# Comments
GET    /comments/project/:id      - Get project comments
POST   /comments                  - Create comment (requires auth)
PUT    /comments/:id              - Update comment (requires auth)
DELETE /comments/:id              - Delete comment (requires auth)

# Statistics
GET    /stats/project/:id         - Project stats (likes + comments)
GET    /stats/all                 - All projects stats
GET    /stats/top/liked           - Top liked projects
GET    /stats/top/commented       - Top commented projects
```

**Auth Middleware:**
```php
// Verify token dengan Auth Service
$authUrl = "http://192.168.1.5:8001/auth/verify";
$method = "GET"; // PENTING: GET bukan POST!

curl_setopt($ch, CURLOPT_URL, $authUrl);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $token
]);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'GET');
```

**Response Format:**
```json
{
  "success": true,
  "message": "Operation successful",
  "timestamp": "2025-12-01T10:30:00Z",
  "data": {
    // actual data here
  }
}
```

**Database Connection:**
```php
$host = '10.132.78.141'; // Laptop A
$port = '5432';
$dbname = 'distributed_system';
$user = 'admin';
$password = 'admin123';
```

---

### 8. Frontend (Port 8080)

**Lokasi:** `frontend/`

**Struktur:**
```
frontend/
├── index.html              # Landing page
├── login.html              # Login page
├── register.html           # Register page
├── explore.html            # Browse projects
├── profile.html            # User profile
├── edit-profile.html       # Edit profile
├── project-detail.html     # Project detail dengan likes/comments
├── create-project.html     # Create project form
├── edit-project.html       # Edit project form
├── styles.css              # Global styles
├── assets/                 # Images, icons
└── js/
    ├── config.js           # API config & helpers
    ├── auth.js             # Authentication logic
    ├── user-service.js     # User API wrapper
    ├── profile.js          # Profile management
    ├── home.js             # Feed & project cards
    ├── explore.js          # Search & filter
    ├── likes-comments.js   # Likes/Comments API wrapper
    └── chat.js             # Chat integration (future)
```

**Key Features:**

1. **Auto-detection Ngrok/Local:**
```javascript
const isNgrok = window.location.hostname.includes("ngrok");
const BASE_URL = isNgrok ? window.location.origin : "http://localhost";
```

2. **API Helper dengan Auth:**
```javascript
const api = {
  async get(url, options) { /* ... */ },
  async post(url, body, options) { /* ... */ },
  async put(url, body, options) { /* ... */ },
  async delete(url, options) { /* ... */ }
};
```

3. **LocalStorage Caching:**
```javascript
// Cache likes & comments untuk prevent reset
localStorage.setItem(`project_${id}_likes`, count);
localStorage.setItem(`project_${id}_comments`, commentsData);
```

4. **HTTPS Avatar URLs:**
```javascript
// Auto-convert http:// to https:// untuk prevent mixed content
if (avatarUrl && avatarUrl.startsWith('http://')) {
  avatarUrl = avatarUrl.replace('http://', 'https://');
}
```

---

##  DATABASE SCHEMA

### Schema: `distributed_system`

```sql
-- Users (Auth Service)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Refresh Tokens (Auth Service)
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profiles (Profile Service)
CREATE TABLE profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    bio TEXT,
    contact VARCHAR(255),
    social_links JSONB DEFAULT '{}',
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects (Portfolio Service)
CREATE TABLE projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    media_files JSONB DEFAULT '[]',
    thumbnail_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Media Files (Media Service)
CREATE TABLE media_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,
    minio_path VARCHAR(500),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Likes (External PHP Service)
CREATE TABLE likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, project_id)
);

-- Comments (External PHP Service)
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics (Future)
CREATE TABLE project_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_projects_tags ON projects USING GIN(tags);
CREATE INDEX idx_likes_project_id ON likes(project_id);
CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_comments_project_id ON comments(project_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_media_files_user_id ON media_files(user_id);
```

---

## 🔌 API ENDPOINTS

### Base URLs

**Local Development:**
```
Auth Service:       http://localhost:8001
Profile Service:    http://localhost:8002
Portfolio Service:  http://localhost:8003
Media Service:      http://localhost:8004
Search Service:     http://localhost:8005
Likes Service:      http://localhost/api/likes
```

**Production (Ngrok):**
```
All Services:       https://xxxxx.ngrok-free.dev/api/{service}/
```

### Authentication Flow

**1. Register:**
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

**2. Login:**
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securePassword123"
}

Response: (same as register)
```

**3. Verify Token (Middleware):**
```bash
GET /auth/verify
Authorization: Bearer {access_token}

Response:
{
  "valid": true,
  "user_id": "uuid",
  "username": "john_doe"
}
```

### Profile Management

**Get Current Profile:**
```bash
GET /profile/me
Authorization: Bearer {access_token}

Response:
{
  "user_id": "uuid",
  "username": "john_doe",
  "name": "John Doe",
  "bio": "Software Developer",
  "contact": "john@example.com",
  "social_links": {
    "github": "github.com/johndoe",
    "linkedin": "linkedin.com/in/johndoe"
  },
  "avatar_url": "https://xxxxx.ngrok-free.dev/media/avatars/xxx.jpg"
}
```

**Update Profile:**
```bash
PUT /profile/update
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "John Doe",
  "bio": "Full Stack Developer",
  "contact": "john@example.com",
  "social_links": {
    "github": "github.com/johndoe"
  }
}
```

### Project Management

**Create Project:**
```bash
POST /projects
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "My Awesome Project",
  "description": "This is a description",
  "tags": ["python", "flask", "react"],
  "media_files": [
    {
      "id": "media-uuid-1",
      "url": "https://.../image1.jpg",
      "type": "image"
    }
  ]
}

Response:
{
  "project_id": "uuid",
  "user_id": "uuid",
  "title": "My Awesome Project",
  "description": "...",
  "tags": ["python", "flask", "react"],
  "media_files": [...],
  "thumbnail_url": null,  // Generated asynchronously
  "created_at": "2025-12-01T10:00:00Z"
}
```

**List Projects:**
```bash
GET /projects?page=1&per_page=10&sort=created_at&order=desc

Response:
{
  "projects": [...],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "pages": 10
}
```

### Media Upload

**Upload Single File:**
```bash
POST /upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: (binary)

Response:
{
  "id": "uuid",
  "filename": "xxx.jpg",
  "original_filename": "photo.jpg",
  "file_type": "image/jpeg",
  "file_size": 1024000,
  "url": "https://.../media/uploads/user-id/xxx.jpg"
}
```

### Likes & Comments

**Get Project Stats:**
```bash
GET /api/likes/stats/project/{project_id}

Response:
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "total_likes": 42,
    "total_comments": 15
  }
}
```

**Toggle Like:**
```bash
POST /api/likes/likes/toggle/{project_id}
Authorization: Bearer {access_token}

Response:
{
  "success": true,
  "message": "Project liked",
  "data": {
    "action": "liked",  // or "unliked"
    "is_liked": true,
    "total_likes": 43
  }
}
```

**Create Comment:**
```bash
POST /api/likes/comments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "project_id": "uuid",
  "comment_text": "Great project!"
}

Response:
{
  "success": true,
  "message": "Comment created",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "project_id": "uuid",
    "username": "john_doe",
    "comment_text": "Great project!",
    "created_at": "2025-12-01T10:00:00Z"
  }
}
```

**Get Project Comments:**
```bash
GET /api/likes/comments/project/{project_id}?limit=100&offset=0

Response:
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "total_comments": 15,
    "limit": 100,
    "offset": 0,
    "comments": [
      {
        "id": "uuid",
        "user_id": "uuid",
        "username": "john_doe",
        "comment_text": "Great project!",
        "created_at": "2025-12-01T10:00:00Z",
        "updated_at": "2025-12-01T10:00:00Z"
      }
    ]
  }
}
```

---

## ⚙️ SETUP & INSTALASI

### Prerequisites

**Laptop A & C:**
- Docker & Docker Compose
- Python 3.11+
- Git
- Ngrok (optional)

**Laptop B:**
- PHP 8.x dengan extensions: pdo_pgsql, curl, json
- PostgreSQL client library
- Web server (Apache/Nginx) atau PHP built-in server

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd v1.0
```

### Step 2: Setup Environment Variables

**Create `.env` file** (optional, atau gunakan default di `docker-compose.yml`):

```env
# Database
POSTGRES_DB=distributed_system
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123

# RabbitMQ
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin123

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=admin123

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRATION=86400

# Chat API (Future)
CHAT_API_KEY=secure-chat-api-key
```

### Step 3: Run Database Migrations

**Laptop A:**

```bash
# Copy migration files
cd migrations

# Connect ke PostgreSQL
psql -h localhost -U admin -d distributed_system

# Run migrations
\i init.sql
\i comments_likes.sql
\i analytics.sql
```

Atau gunakan script:

```bash
cd migrations
bash run-migrations.sh
```

### Step 4: Start Docker Services

**Laptop C:**

```bash
# Build dan start semua services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Setup Frontend

```bash
# Navigate to frontend
cd frontend

# Start simple HTTP server
python -m http.server 8080

# Atau gunakan script
bash ../start-frontend.sh
```

### Step 6: Setup External PHP Service

**Laptop B:**

```bash
# Install dependencies
composer install  # jika ada composer.json

# Configure database connection
# Edit config/database.php atau .env
DB_HOST=10.132.78.141
DB_PORT=5432
DB_NAME=distributed_system
DB_USER=admin
DB_PASSWORD=admin123

# Configure auth service
AUTH_SERVICE_URL=http://192.168.1.5:8001/auth/verify

# Start PHP server
php -S 0.0.0.0:8080

# Atau gunakan Apache/Nginx
sudo systemctl start apache2
```

**Verify connection:**

```bash
# Test dari Laptop B ke Laptop A
curl http://10.132.78.141:5432  # PostgreSQL
curl http://192.168.1.5:8001/health  # Auth Service

# Test dari Laptop C ke Laptop B
curl http://192.168.1.17:8080/stats/all
```

### Step 7: Setup Ngrok (Optional)

**Laptop C:**

```bash
# Install ngrok
# Download from https://ngrok.com/download

# Authenticate
ngrok authtoken YOUR_AUTH_TOKEN

# Start tunnel on port 80 (nginx)
ngrok http 80

# Copy ngrok URL (e.g., https://xxxxx.ngrok-free.dev)
```

**Update frontend config:**
Frontend akan auto-detect ngrok URL, tidak perlu konfigurasi manual!

### Step 8: Verify Installation

**Test all services:**

```bash
# Auth Service
curl http://localhost:8001/health

# Profile Service
curl http://localhost:8002/health

# Portfolio Service
curl http://localhost:8003/health

# Media Service
curl http://localhost:8004/health

# Search Service
curl http://localhost:8005/health

# Likes Service (via nginx)
curl http://localhost/api/likes/stats/all

# Frontend
curl http://localhost:8080
```

**Access application:**

- Local: http://localhost:8080
- Ngrok: https://xxxxx.ngrok-free.dev

---

## 🔧 KONFIGURASI

### Nginx Configuration

**File:** `nginx.conf`

```nginx
# Key configurations:
location /api/likes/ {
    rewrite ^/api/likes/(.*) /$1 break;
    proxy_pass http://192.168.1.17:8080;
    
    # CORS headers
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
}

location /media/ {
    proxy_pass http://minio:9000/media-files/;
    client_max_body_size 100M;
}
```

### Frontend Configuration

**File:** `frontend/js/config.js`

**Auto-detection Logic:**
```javascript
const isNgrok = window.location.hostname.includes("ngrok");
const BASE_URL = isNgrok ? window.location.origin : "http://localhost";

const API_CONFIG = {
  AUTH_SERVICE: isNgrok 
    ? `${BASE_URL}/api/auth` 
    : "http://localhost:8001/auth",
  // ... other services
};
```

**Manual Override:**
```javascript
// Jika perlu override manual
const API_CONFIG = {
  AUTH_SERVICE: "http://192.168.1.5:8001/auth",
  PROFILE_SERVICE: "http://localhost:8002",
  // ...
};
```

### PHP Service Configuration

**Auth Middleware Example:**

```php
<?php
class AuthMiddleware {
    private $authServiceUrl = "http://192.168.1.5:8001/auth/verify";
    
    public function verifyToken($token) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $this->authServiceUrl);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Authorization: Bearer ' . $token,
            'Content-Type: application/json'
        ]);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'GET');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200) {
            $data = json_decode($response, true);
            if ($data['valid'] === true) {
                return [
                    'success' => true,
                    'user_id' => $data['user_id'],
                    'username' => $data['username']
                ];
            }
        }
        
        return ['success' => false, 'error' => 'Invalid token'];
    }
}
?>
```

---

## 🚀 DEPLOYMENT

### Development Mode

```bash
# Start all services
docker-compose up -d

# Start frontend
cd frontend && python -m http.server 8080

# Start ngrok (optional)
ngrok http 80
```

### Production Mode

**1. Update Environment Variables:**

```env
# Use strong passwords
POSTGRES_PASSWORD=strong_random_password_here
RABBITMQ_DEFAULT_PASS=strong_random_password_here
MINIO_ROOT_PASSWORD=strong_random_password_here
JWT_SECRET=very_long_random_secret_at_least_32_chars

# Update service URLs to production IPs
DATABASE_URL=postgresql://admin:PASSWORD@PRODUCTION_IP:5432/distributed_system
```

**2. SSL/TLS Configuration:**

```bash
# Use certbot untuk SSL certificate
sudo certbot --nginx -d yourdomain.com

# Atau gunakan ngrok dengan custom domain
ngrok http --domain=your-custom-domain.app 80
```

**3. Firewall Configuration:**

```bash
# Laptop A (Infrastructure)
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 5672/tcp  # RabbitMQ
sudo ufw allow 8001/tcp  # Auth Service

# Laptop B (PHP Service)
sudo ufw allow 8080/tcp

# Laptop C (Main)
sudo ufw allow 80/tcp    # Nginx
sudo ufw allow 443/tcp   # HTTPS (if using SSL)
```

**4. Monitoring & Logging:**

```bash
# View service logs
docker-compose logs -f [service_name]

# View RabbitMQ management
http://localhost:15672
Username: admin
Password: admin123

# View MinIO console
http://localhost:9001
Username: admin
Password: admin123

# View Elasticsearch
http://localhost:9200/_cluster/health
```

**5. Backup Strategy:**

```bash
# Backup PostgreSQL
docker exec postgres_db pg_dump -U admin distributed_system > backup.sql

# Backup MinIO data
docker exec minio mc mirror /data /backup

# Restore
docker exec -i postgres_db psql -U admin distributed_system < backup.sql
```

---

## 🐛 TROUBLESHOOTING

### Common Issues

#### 1. **401 Unauthorized di External Service**

**Problem:** PHP service return 401 untuk authenticated requests

**Solution:**
```bash
# Verify auth endpoint
curl -X GET "http://192.168.1.5:8001/auth/verify" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: {"valid": true, "user_id": "...", "username": "..."}

# Update PHP middleware
$authUrl = "http://192.168.1.5:8001/auth/verify";  // Correct endpoint
$method = "GET";  // NOT POST!
```

Lihat: `TROUBLESHOOTING_LIKES_SERVICE.md` dan `AUTH_MIDDLEWARE_EXAMPLE.php`

---

#### 2. **Mixed Content Warning (HTTP in HTTPS)**

**Problem:** Avatar/images menggunakan http:// di halaman https://

**Solution:** Auto-convert URLs ke HTTPS:

```javascript
let avatarUrl = profile.avatar_url || null;
if (avatarUrl && avatarUrl.startsWith('http://')) {
  avatarUrl = avatarUrl.replace('http://', 'https://');
}
```

---

#### 3. **CORS Errors**

**Problem:** Browser blocking cross-origin requests

**Solution:**

**Backend (Flask):**
```python
from flask_cors import CORS

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost", "https://*.ngrok-free.app"],
        "supports_credentials": True
    }
})
```

**Nginx:**
```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
```

---

#### 4. **Cannot Connect to Database**

**Problem:** Service tidak bisa connect ke PostgreSQL

**Diagnostic:**
```bash
# Test connection from service container
docker exec -it auth_service bash
psql -h postgres -U admin -d distributed_system

# Test from host
psql -h localhost -U admin -d distributed_system

# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

**Solution:**
- Verify `DATABASE_URL` environment variable
- Ensure PostgreSQL container is running
- Check network connectivity
- Verify credentials

---

#### 5. **Likes/Comments Not Loading**

**Problem:** Stats tetap 0, comments tidak muncul

**Diagnostic:**
```bash
# Test PHP service directly
curl http://192.168.1.17:8080/stats/all

# Test via nginx proxy
curl http://localhost/api/likes/stats/all

# Check browser console
# Look for: Response keys, typeof response, etc.
```

**Common Causes:**
1. PHP service tidak running
2. Firewall blocking port 8080
3. Wrong nginx proxy configuration
4. Response format mismatch

**Solution:**
```bash
# Start PHP service
php -S 0.0.0.0:8080  # Bind to 0.0.0.0 NOT 127.0.0.1

# Check firewall
sudo ufw allow 8080/tcp

# Test connectivity
ping 192.168.1.17
telnet 192.168.1.17 8080
```

---

#### 6. **Thumbnail Not Generated**

**Problem:** Project thumbnail tetap null setelah upload

**Diagnostic:**
```bash
# Check worker logs
docker-compose logs worker_thumbnailer

# Check RabbitMQ queue
docker exec -it rabbitmq rabbitmqctl list_queues

# Check if worker is running
docker-compose ps worker_thumbnailer
```

**Solution:**
```bash
# Restart worker
docker-compose restart worker_thumbnailer

# Clear queue and restart
docker exec -it rabbitmq rabbitmqctl purge_queue thumbnail_queue
docker-compose restart worker_thumbnailer

# Manual trigger (if needed)
curl -X POST http://localhost:8005/index/project/{project_id}
```

---

#### 7. **Frontend Not Loading**

**Problem:** Blank page atau API errors

**Diagnostic:**
```bash
# Check browser console (F12)
# Look for: Network errors, CORS errors, 404s

# Verify frontend server
curl http://localhost:8080

# Check config.js
curl http://localhost:8080/js/config.js
```

**Common Issues:**
- Wrong API URLs in config.js
- Missing js files
- CORS policy blocking
- Services not running

**Solution:**
```bash
# Ensure all services running
docker-compose ps

# Restart nginx
docker-compose restart nginx

# Clear browser cache
# Hard refresh: Ctrl+Shift+R
```

---

#### 8. **Ngrok Not Working**

**Problem:** Ngrok URL tidak bisa akses backend

**Solution:**
```bash
# IMPORTANT: Use port 80 (nginx) NOT 8080!
ngrok http 80  # ✅ Correct
# NOT: ngrok http 8080  # ❌ Wrong! Only serves frontend

# Update config if needed
# Frontend auto-detects ngrok, no manual config!

# Check ngrok dashboard
http://127.0.0.1:4040
```

---

### Debug Commands

```bash
# Check all containers
docker-compose ps

# View logs for specific service
docker-compose logs -f auth_service

# Restart service
docker-compose restart auth_service

# Rebuild service
docker-compose up -d --build auth_service

# Enter container shell
docker exec -it auth_service bash

# Check network connectivity
docker exec -it auth_service ping postgres
docker exec -it auth_service curl http://rabbitmq:15672

# Database queries
docker exec -it postgres_db psql -U admin -d distributed_system

# RabbitMQ management
docker exec -it rabbitmq rabbitmqctl list_queues

# MinIO client
docker exec -it minio mc ls local/media-files

# Elasticsearch
curl http://localhost:9200/_cat/indices
curl http://localhost:9200/projects/_search
```

---

## 📚 DOKUMENTASI TAMBAHAN

### File Referensi:
- `TROUBLESHOOTING_LIKES_SERVICE.md` - Detail troubleshooting PHP service
- `AUTH_MIDDLEWARE_EXAMPLE.php` - Example middleware PHP
- `EXTERNAL-SERVICE-CONFIG.md` - Konfigurasi external service
- `migrations/init.sql` - Database schema
- `docker-compose.yml` - Service orchestration
- `nginx.conf` - Reverse proxy config

### Architecture Diagrams:
```
docs/
├── architecture-diagram.png
├── database-schema.png
├── deployment-topology.png
└── api-flow-diagram.png
```

---

## 📞 SUPPORT & CONTACT

### Maintenance Team:
- **Backend Services**: [Your Name]
- **Frontend**: [Your Name]
- **PHP External Service**: [PHP Developer Name]
- **Infrastructure**: [DevOps Name]

### Common URLs:
- **Production**: https://xxxxx.ngrok-free.dev
- **Local**: http://localhost:8080
- **RabbitMQ Management**: http://localhost:15672
- **MinIO Console**: http://localhost:9001
- **Elasticsearch**: http://localhost:9200

---

## 📝 CHANGELOG

### Version 1.0 (December 2025)
- ✅ Initial release
- ✅ All core services implemented
- ✅ Multi-laptop deployment
- ✅ External PHP service integration
- ✅ Ngrok support
- ✅ Complete documentation

### Planned Features (v1.1):
- 🔄 Real-time chat integration (Stream Chat API)
- 🔄 Analytics dashboard
- 🔄 Email notifications
- 🔄 Advanced search filters
- 🔄 Project collaboration features

---

## 📄 LICENSE

[Include your license information here]

---

**Last Updated:** December 1, 2025  
**Document Version:** 1.0  
**System Version:** 1.0

