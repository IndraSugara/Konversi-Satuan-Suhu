# System Architecture Documentation

## Overview

Distributed microservices system untuk platform portfolio dengan FastAPI, PostgreSQL, Redis, RabbitMQ, Elasticsearch, dan MinIO.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX (Port 80)                          │
│                    Reverse Proxy & Load Balancer                 │
└────────────┬────────────────────────────────────────────────────┘
             │
   ┌─────────┴─────────────────────────────────────┐
   │                                                 │
   ▼                                                 ▼
┌──────────────────────┐                  ┌──────────────────────┐
│   Frontend (8080)    │                  │   API Gateway        │
│   Static Files       │                  │   /api/* routes      │
└──────────────────────┘                  └──────────┬───────────┘
                                                     │
                        ┌────────────────────────────┼────────────────────────┐
                        │                            │                        │
                        ▼                            ▼                        ▼
              ┌──────────────────┐        ┌──────────────────┐     ┌──────────────────┐
              │  Auth Service    │        │ Profile Service  │     │Portfolio Service │
              │  Port: 8001      │        │  Port: 8002      │     │  Port: 8003      │
              │  FastAPI         │        │  FastAPI         │     │  FastAPI         │
              └────────┬─────────┘        └────────┬─────────┘     └────────┬─────────┘
                       │                           │                        │
                       └───────────────┬───────────┴────────────────────────┘
                                       │
                        ┌──────────────┼──────────────┐
                        ▼              ▼              ▼
              ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
              │Media Service │  │Search Service│  │   Workers     │
              │Port: 8004    │  │Port: 8005    │  │ Thumbnail Gen │
              │FastAPI/Flask │  │Flask         │  │ RabbitMQ      │
              └──────┬───────┘  └──────┬───────┘  └───────────────┘
                     │                 │
    ┌────────────────┼─────────────────┼─────────────────────────┐
    │                │                 │                          │
    ▼                ▼                 ▼                          ▼
┌─────────┐    ┌──────────┐     ┌──────────────┐         ┌──────────┐
│PostgreSQL│    │  Redis   │     │ Elasticsearch │         │  MinIO   │
│Port: 5432│    │Port: 6379│     │  Port: 9200   │         │Port: 9000│
└──────────┘    └──────────┘     └───────────────┘         └──────────┘
     │               │                   │                       │
     └───────────────┴───────────────────┴───────────────────────┘
                        RabbitMQ (Port: 5672)

                    EXTERNAL SERVICES (Proxied via NGINX)
    ┌────────────────────────────────────────────────────────────┐
    │                                                              │
    │  ┌────────────────────────┐    ┌────────────────────────┐  │
    │  │   Chat Service         │    │ Comments/Likes Service │  │
    │  │   23.0.3.60:8006       │    │   23.0.3.39:8080       │  │
    │  │   Node.js + Socket.IO  │    │   PHP7 / CI3     │  │
    │  │   /api/chat/*          │    │   /api/likes/*         │  │
    │  │   Real-time messaging  │    │   Social interactions  │  │
    │  └────────────────────────┘    └────────────────────────┘  │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
```

---

## Services Details

### 1. Auth Service (Port 8001)

**Technology:** FastAPI + Uvicorn (4 workers)

**Responsibilities:**

- User registration & authentication
- JWT token generation (access + refresh)
- Token verification & refresh
- Password hashing (bcrypt)
- API key verification for external services

**Endpoints:**

- `POST /auth/register` - User registration
- `POST /auth/login` - Login & token generation
- `GET /auth/verify` - Token validation
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout & invalidate tokens
- `GET /api/users` - List users (for Chat Service)
- `GET /api/users/{user_id}` - Get user by ID

**Database Tables:**

- `users` - User credentials & info
- `refresh_tokens` - Active refresh tokens

---

### 2. Profile Service (Port 8002)

**Technology:** FastAPI + Uvicorn (4 workers)

**Responsibilities:**

- User profile management (bio, contact, social links)
- Avatar & theme music URLs
- Username updates
- Redis caching for performance
- Event publishing to RabbitMQ

**Endpoints:**

- `GET /profile/me` - Get own profile (cached)
- `PUT /profile/me` - Update profile (invalidates cache)
- `GET /profile/public/{username}` - Public profile view
- `GET /profile/user/{user_id}` - Profile lookup (cached)
- `GET /profile/external/{user_id}` - API key protected

**Database Tables:**

- `profiles` - Extended user information

**Cache Strategy:**

- Key: `profile:{user_id}`
- TTL: Default (invalidated on update)

**Events Published:**

- `profile.updated` - On profile changes

---

### 3. Portfolio Service (Port 8003)

**Technology:** FastAPI + Uvicorn (4 workers)

**Responsibilities:**

- Project CRUD operations
- Project ownership validation
- Thumbnail management
- View tracking & statistics
- Redis caching
- Event publishing

**Endpoints:**

- `POST /projects` - Create project (auth required)
- `GET /projects/{project_id}` - Get project details
- `PUT /projects/{project_id}` - Update project (owner only)
- `DELETE /projects/{project_id}` - Delete project (owner only)
- `GET /projects/user/{user_id}` - List user projects
- `PUT /projects/{project_id}/thumbnail` - Update thumbnail
- `POST /projects/{project_id}/view` - Track view
- `GET /projects/{project_id}/stats` - View statistics
- `POST /admin/reindex-projects` - Reindex to Elasticsearch

**Database Tables:**

- `projects` - Project data (title, description, tags, links, etc)
- `project_views` - View tracking

**Cache Strategy:**

- Key: `project:{project_id}`
- TTL: Default

**Events Published:**

- `project.created` - New project
- `project.updated` - Project modified
- `project.deleted` - Project removed

---

### 4. Media Service (Port 8004)

**Technology:** Flask (currently, FastAPI conversion pending)

**Responsibilities:**

- File uploads (images, audio)
- File validation (size, type)
- MinIO object storage integration
- Thumbnail generation triggering
- Metadata extraction

**Endpoints:**

- `POST /upload` - Upload media file
- `GET /media/{file_id}` - Get media URL
- `DELETE /media/{file_id}` - Delete media

**Storage:**

- MinIO buckets: `media`, `thumbnails`

**Events Published:**

- `thumbnail.generate` - Request thumbnail creation

**Validation:**

- Images: jpg, jpeg, png, gif (max 10MB)
- Audio: mp3, wav, ogg (max 50MB)

---

### 5. Search Service (Port 8005)

**Technology:** Flask

**Responsibilities:**

- Elasticsearch integration
- Full-text search across projects & profiles
- Fuzzy matching
- Filtering & sorting
- Real-time indexing via RabbitMQ

**Endpoints:**

- `GET /search` - Search projects/profiles
  - Query params: `query`, `type` (project/profile/all), `page`, `size`
- `POST /reindex` - Full reindex from database

**Elasticsearch Indices:**

- `portfolio_index` - Projects & profiles

**Events Consumed:**

- `project.created` - Index new project
- `project.updated` - Update project index
- `project.deleted` - Remove from index
- `profile.updated` - Update profile index

**Search Features:**

- Multi-field search (title, description, tags, username)
- Fuzzy matching (typo tolerance)
- Pagination
- Score-based ranking

---

### 6. Worker: Thumbnailer

**Technology:** Python + RabbitMQ + Pillow

**Responsibilities:**

- Async thumbnail generation
- Image processing (resize, optimize)
- MinIO upload
- Portfolio service notification

**Queue Consumed:**

- `thumbnail.queue`

**Processing:**

- Resize to 300x300 (maintain aspect ratio)
- Format: JPEG with quality optimization
- Upload to MinIO `thumbnails` bucket

---

## External Services (Proxied via NGINX)

### 7. Chat Service (External - 23.0.3.60:8006)

**Technology:** Node.js + Socket.IO + PostgreSQL

**Responsibilities:**

- Real-time messaging
- WebSocket connections
- Conversation management
- Message persistence
- User online status
- Message delivery tracking

**Endpoints:**

- `GET /api/chat/conversations` - List user conversations
- `GET /api/chat/conversations/{conversation_id}/messages` - Get messages
- `POST /api/chat/conversations` - Create/get conversation
- `POST /api/chat/conversations/{conversation_id}/messages` - Send message
- `POST /api/chat/register-user` - Sync user from Auth Service
- `GET /api/chat/users/search` - Search users for chat

**WebSocket Events:**

- `connect` - Client connection
- `join_conversation` - Join chat room
- `new_message` - Real-time message
- `message_sent` - Message delivery confirmation
- `typing` - Typing indicator
- `user_online` - Online status updates

**Database Tables (External PostgreSQL):**

- `chat_users` - Cached user info from Profile Service
- `conversations` - Chat conversations
- `conversation_participants` - Many-to-many relationship
- `messages` - Chat messages

**Authentication:**

- JWT token from Auth Service
- API key for service-to-service (e.g., profile sync)

**NGINX Route:**

- `/api/chat/*` → `http://23.0.3.60:8006`
- `/socket.io/*` → `http://23.0.3.60:8006/socket.io/` (WebSocket support)

**Features:**

- Real-time bidirectional communication
- Message history persistence
- Conversation search
- Unread message tracking
- Auto-sync with Profile Service for user data

---

### 8. Comments & Likes Service (External - 23.0.3.39:8080)

**Technology:** CodeIgniter 3 (PHP 7.4+) + PostgreSQL

**Responsibilities:**

- Like/unlike projects
- Comment CRUD operations
- Comment likes
- Statistics aggregation
- User interaction tracking

**Endpoints:**

- `POST /likes/{project_id}` - Toggle like on project
- `GET /check/{project_id}` - Check if user liked project
- `GET /stats/project/{project_id}` - Get project stats (likes + comments count)
- `POST /comments` - Create comment
- `GET /comments/project/{project_id}` - Get project comments
- `DELETE /comments/{comment_id}` - Delete comment
- `POST /comments/{comment_id}/like` - Like a comment

**Database Tables (PostgreSQL):**

- `likes` - Project likes (user_id, project_id, created_at)
- `comments` - Project comments
- `comment_likes` - Comment likes

**Authentication:**

- JWT token from Auth Service
- User info extracted from token (CI3 JWT library)

**NGINX Route:**

- `/api/likes/*` → `http://23.0.3.39:8080`

**Response Formats:**

```json
// Stats
{
  "data": {
    "total_likes": 42,
    "total_comments": 15
  }
}

// Like status
{
  "is_liked": true,
  "action": "liked"
}

// Comments
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "username": "string",
      "comment_text": "string",
      "created_at": "timestamp"
    }
  ]
}
```

**Features:**

- Fast aggregation for stats display
- Optimistic locking for concurrent likes
- Comment threading (future)
- Spam detection (future)
- Rate limiting per user

**Performance:**

- Timeout: 1-3 seconds (with fallback to cached data)
- Caching strategy: 30 seconds TTL in frontend
- Optimistic updates in UI for instant feedback

---

## Infrastructure Components

### PostgreSQL (Port 5432)

**Purpose:** Primary data store

**Tables:**

- `users` - Auth & basic user info
- `profiles` - Extended user data
- `projects` - Portfolio projects
- `project_views` - View tracking
- `refresh_tokens` - JWT refresh tokens

**Configuration:**

- User: `admin`
- Database: `distributed_system`
- Persistent volume: `postgres_data`

---

### Redis (Port 6379)

**Purpose:** Cache layer

**Usage:**

- Profile caching (reduce DB hits)
- Project caching
- Session management (optional)

**Eviction Policy:** LRU
**Persistence:** RDB snapshots

---

### RabbitMQ (Port 5672, Management: 15672)

**Purpose:** Message broker for async processing

**Exchanges:**

- `portfolio.events` - Project events
- `profile.events` - Profile events

**Queues:**

- `project.events` - For search indexing
- `profile.events` - For search indexing
- `thumbnail.queue` - For thumbnail generation

**Pattern:** Fanout (events broadcast to multiple consumers)

---

### Elasticsearch (Port 9200)

**Purpose:** Full-text search engine

**Index:** `portfolio_index`

**Mappings:**

- Projects: `project_id`, `title`, `description`, `tags`, `username`
- Profiles: `user_id`, `username`, `name`, `bio`, `expertise`

**Features:**

- Fuzzy search
- Stemming
- Multi-field analysis
- Score-based ranking

---

### MinIO (Port 9000, Console: 9001)

**Purpose:** S3-compatible object storage

**Buckets:**

- `media` - Original uploaded files
- `thumbnails` - Generated thumbnails

**Access:**

- Access Key: `minioadmin`
- Secret Key: `minioadmin`

---

### Nginx (Port 80)

**Purpose:** Reverse proxy & routing

**Routes:**

- `/` → Frontend (port 8080)
- `/api/auth/*` → Auth Service (8001)
- `/api/profile/*` → Profile Service (8002)
- `/api/portfolio/*` → Portfolio Service (8003)
- `/api/media/*` → Media Service (8004)
- `/api/search/*` → Search Service (8005)

**Features:**

- URL rewriting
- CORS headers
- Large file upload support (100MB for media)
- Gzip compression

---

## Data Flow Examples

### 1. User Registration & Login

```
1. User → POST /api/auth/register
2. Auth Service → Hash password (bcrypt)
3. Auth Service → Insert to PostgreSQL users table
4. Return user_id

5. User → POST /api/auth/login
6. Auth Service → Verify credentials
7. Auth Service → Generate JWT (access + refresh)
8. Auth Service → Store refresh token in DB
9. Return tokens to user
```

### 2. Create Project with Media

```
1. User → POST /api/media/upload (with auth token)
2. Media Service → Validate file
3. Media Service → Upload to MinIO
4. Media Service → Publish 'thumbnail.generate' to RabbitMQ
5. Media Service → Return media URL

6. User → POST /api/portfolio/projects (with media URL)
7. Portfolio Service → Verify JWT token
8. Portfolio Service → Insert to PostgreSQL
9. Portfolio Service → Publish 'project.created' to RabbitMQ
10. Portfolio Service → Return project data

// Async processing
11. Worker → Consume 'thumbnail.generate'
12. Worker → Download from MinIO, resize, optimize
13. Worker → Upload thumbnail to MinIO
14. Worker → Notify Portfolio Service

15. Search Service → Consume 'project.created'
16. Search Service → Index to Elasticsearch
```

### 3. Search Projects

```
1. User → GET /api/search?query=AI&type=project
2. Search Service → Query Elasticsearch
3. Elasticsearch → Return matching projects (scored)
4. Search Service → Return results to user
```

### 4. View Project (with caching)

```
1. User → GET /api/portfolio/projects/{id}
2. Portfolio Service → Check Redis cache
3. If cache hit → Return cached data
4. If cache miss:
   - Query PostgreSQL
   - Store in Redis (TTL default)
   - Return data
5. Track view in project_views table
```

### 5. Like & Comment on Project (External Service)

```
1. User → Click like button on project
2. Frontend → Optimistic update (instant UI feedback)
3. Frontend → POST /api/likes/{project_id} (JWT token)
4. NGINX → Proxy to Comments/Likes Service (23.0.3.39:8080)
5. Comments/Likes Service → Verify JWT token
6. Comments/Likes Service → Toggle like in PostgreSQL
7. Return like status

// Stats update (parallel)
8. Frontend → GET /api/likes/stats/project/{project_id}
9. Comments/Likes Service → Aggregate likes & comments count
10. Return stats (cached for 30s in frontend)

// Comment flow
11. User → Submit comment
12. Frontend → POST /api/likes/comments
13. Comments/Likes Service → Insert comment
14. Frontend → Refresh comments list
```

**Optimization:**

- Timeout: 1-3 seconds max
- Fallback to cached stats on timeout
- Optimistic UI updates for instant feedback

### 6. Real-time Chat (External Service)

```
// Initial connection
1. User → Open messages page
2. Frontend → Connect to Socket.IO (ws://localhost/socket.io/)
3. NGINX → Proxy WebSocket to Chat Service (23.0.3.60:8006)
4. Chat Service → Verify JWT token
5. Socket.IO → Establish WebSocket connection

// Load conversations
6. Frontend → GET /api/chat/conversations
7. Chat Service → Query conversations from PostgreSQL
8. Return conversation list with last message

// Send message
9. User → Type & send message
10. Frontend → Emit 'new_message' via Socket.IO
11. Chat Service → Save to PostgreSQL
12. Chat Service → Emit to recipient's socket
13. Both users receive message in real-time

// User sync (background)
- Chat Service → Periodically sync user data from Profile Service
- Cache user info in chat_users table for fast lookups
```

**Features:**

- Real-time bidirectional communication
- WebSocket for instant message delivery
- Automatic reconnection on disconnect
- Typing indicators (future)
- Read receipts (future)

---

## Communication Patterns

### Synchronous (HTTP/REST)

- Frontend ↔ Services
- Service ↔ Database
- Service ↔ Redis
- Service ↔ Elasticsearch
- Service ↔ MinIO

### Asynchronous (Message Queue)

- Services → RabbitMQ (event publishing)
- RabbitMQ → Search Service (indexing)
- RabbitMQ → Workers (background jobs)

---

## Security

### Authentication

- JWT tokens (HS256 algorithm)
- Access token: Short-lived (24h default)
- Refresh token: Long-lived (7 days)
- Stored in database for revocation

### Authorization

- Token verification via `Authorization: Bearer <token>` header
- Ownership validation (users can only edit own resources)
- API keys for inter-service communication

### Data Protection

- Password hashing: bcrypt with salt
- HTTPS support (nginx SSL termination)
- CORS configured per service

---

## Performance Optimizations

### Caching Strategy

- **Profile data:** Redis cache, invalidated on update
- **Project data:** Redis cache with TTL
- **Search results:** Elasticsearch in-memory cache

### Database

- Indexed columns: `user_id`, `created_at`, `username`, `email`
- Connection pooling per service

### Async Processing

- Thumbnail generation offloaded to worker
- Search indexing via message queue (non-blocking)

### FastAPI Services

- Uvicorn with 4 workers per service
- Async/await for I/O operations
- Concurrent request handling

---

## Scalability

### Horizontal Scaling

- **Services:** Add more containers behind nginx
- **Workers:** Add more thumbnail workers (consume same queue)
- **Database:** Read replicas for queries
- **Redis:** Redis Cluster for large datasets
- **Elasticsearch:** Multi-node cluster

### Vertical Scaling

- Increase container resources (CPU, RAM)
- Increase worker count per service (uvicorn --workers)

---

## Monitoring & Observability

### Health Checks

- All services expose `/health` endpoint
- Returns: `{"status": "healthy", "service": "service_name"}`

### Logging

- Service logs: stdout/stderr captured by Docker
- View logs: `docker logs <service_name>`

### Metrics (Recommended to Add)

- Prometheus for metrics collection
- Grafana for visualization
- Track: request rate, latency, error rate, cache hit ratio

---

## Deployment

### Development

```bash
docker-compose up -d
```

### Production Considerations

1. **Environment Variables:**

   - Store secrets in `.env` or secrets manager
   - Change default passwords
   - Generate secure JWT secret

2. **Database:**

   - Use managed PostgreSQL (RDS, Cloud SQL)
   - Enable backups
   - Read replicas for scaling

3. **Redis:**

   - Use managed Redis (ElastiCache, MemoryStore)
   - Enable persistence
   - Configure eviction policies

4. **Object Storage:**

   - Use S3 or GCS instead of MinIO
   - Enable CDN for media delivery

5. **Load Balancer:**

   - Replace nginx with cloud LB (ALB, GCP LB)
   - SSL termination at LB
   - Health check configuration

6. **Monitoring:**
   - Application Performance Monitoring (APM)
   - Error tracking (Sentry)
   - Log aggregation (ELK, CloudWatch)

---

## Testing

### Load Testing

Direct to services (no nginx overhead):

```bash
# 50 users
pytest tests/load/test_load_runner.py::TestLoadPerformance::test_load_50_users -v

# 100 users
pytest tests/load/test_load_runner.py::TestLoadPerformance::test_load_100_users -v

# 200 users (stress test)
pytest tests/load/test_load_runner.py::TestLoadPerformance::test_load_200_users -v
```

**Performance Benchmarks:**

- 50 users: ~1,000 req, 22ms avg, 18 req/s
- 100 users: ~2,200 req, 23ms avg, 36 req/s
- 200 users: Expected ~4,000+ req

### Unit Tests

```bash
pytest tests/unit/ -v
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

### Security Tests

```bash
pytest tests/security/ -v
```

---

## API Versioning

Current: v1 (implicit)
Future: `/api/v2/*` for breaking changes

---

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `409` - Conflict (duplicate resource)
- `422` - Validation error (FastAPI Pydantic)
- `500` - Internal server error

### Error Response Format

```json
{
  "detail": "Error message",
  "error": "Specific error type"
}
```

---

## Future Improvements

1. **Service Mesh:** Istio or Linkerd for advanced traffic management
2. **API Gateway:** Kong or AWS API Gateway for centralized management
3. **Event Sourcing:** Store all events for audit & replay
4. **CQRS:** Separate read/write models for better scaling
5. **GraphQL:** Alternative to REST for flexible queries
6. **WebSockets:** Real-time notifications
7. **Machine Learning:** Recommendation engine for projects
8. **Analytics:** User behavior tracking & insights

---

## Technologies Summary

| Component          | Technology        | Version      | Purpose             | Location        |
| ------------------ | ----------------- | ------------ | ------------------- | --------------- |
| Auth Service       | FastAPI           | 0.104.1      | Authentication      | Internal (8001) |
| Profile Service    | FastAPI           | 0.104.1      | User profiles       | Internal (8002) |
| Portfolio Service  | FastAPI           | 0.104.1      | Projects            | Internal (8003) |
| Media Service      | Flask             | 3.0.0        | File uploads        | Internal (8004) |
| Search Service     | Flask             | 3.0.0        | Search              | Internal (8005) |
| **Chat Service**   | **Node.js**       | **Latest**   | **Real-time chat**  | **External**    |
| **Comments/Likes** | **CodeIgniter 3** | **3.1.13**   | **Social features** | **External**    |
| Database           | PostgreSQL        | 13           | Data persistence    | Internal (5432) |
| Cache              | Redis             | 7-alpine     | Caching             | Internal (6379) |
| Message Queue      | RabbitMQ          | 3-management | Async messaging     | Internal (5672) |
| Search Engine      | Elasticsearch     | 8.11.0       | Full-text search    | Internal (9200) |
| Object Storage     | MinIO             | Latest       | Media storage       | Internal (9000) |
| Reverse Proxy      | Nginx             | Alpine       | Routing & Proxy     | Internal (80)   |
| ASGI Server        | Uvicorn           | 0.24.0       | FastAPI runtime     | Internal        |

---

## Quick Reference

### Service Ports

**Internal Services:**

- Auth: 8001
- Profile: 8002
- Portfolio: 8003
- Media: 8004
- Search: 8005
- PostgreSQL: 5432
- Redis: 6379
- RabbitMQ: 5672 (AMQP), 15672 (Management)
- Elasticsearch: 9200
- MinIO: 9000 (API), 9001 (Console)
- Nginx: 80

**External Services (Proxied):**

- Chat Service: 23.0.3.60:8006 → `/api/chat/*`, `/socket.io/*`
- Comments/Likes: 23.0.3.39:8080 → `/api/likes/*`

### Important Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild service
docker-compose build <service_name>

# View logs
docker logs <container_name> -f

# Reindex projects
curl -X POST http://localhost:8003/admin/reindex-projects

# Check service health
curl http://localhost:8001/health  # Auth
curl http://localhost:8002/health  # Profile
curl http://localhost:8003/health  # Portfolio
```

---

**Last Updated:** December 9, 2025  
**Architecture Version:** 1.0  
**Status:** Production Ready

