# Post Service

Short description: FastAPI service for managing posts (CRUD, search, filters), publishing events to RabbitMQ, and enforcing JWT on write operations.

## 🎯 Responsibilities
- Create, update, delete posts
- Persist data in PostgreSQL
- Publish PostCreated/PostUpdated/PostDeleted events to RabbitMQ
- Expose REST APIs for search and retrieval

Out of scope:
- ❌ User management or JWT issuance (relies on Identity Service)
- ❌ Likes/comments (handled by another service)
- ❌ Feed generation

## 🏗️ Architecture
- Framework: FastAPI (async)
- Architecture: Clean Architecture
- Layers:
	- api/routers
	- services (business logic)
	- repositories (DB access)
	- models (SQLAlchemy)
	- schemas (Pydantic)
	- messaging (RabbitMQ publisher)

Folder sketch:
```
app/
 ├─ api/
 ├─ services/
 ├─ repositories/
 ├─ models/
 ├─ schemas/
 ├─ messaging/
 └─ main.py
```

## 🔌 External Dependencies
- PostgreSQL
- RabbitMQ
- Identity Service (JWT validation for writes)

## 🔄 Service Communication
### 📤 Events – Publisher

| Event        | Exchange     | Routing Key   | Payload                                   |
|--------------|--------------|---------------|-------------------------------------------|
| PostCreated  | post_events  | post.events   | post_id, user_id, title, content, tags    |
| PostUpdated  | post_events  | post.events   | post_id, user_id, changes                 |
| PostDeleted  | post_events  | post.events   | post_id, user_id                          |

### 📥 Events – Consumer
- None at the moment. Add a binding in `app/messaging/rabbitmq.py` if this service should react to external events.

## 🌐 REST APIs (Overview)
- `POST   /posts` — create post (JWT required)
- `GET    /posts/{post_id}` — fetch by id (public)
- `GET    /posts` — search/filter + pagination (public)
- `GET    /posts/users/{user_id}` — posts by user (public)
- `GET    /posts/me/posts` — current user posts (JWT required)
- `PUT    /posts/{post_id}` — update (JWT + ownership)
- `DELETE /posts/{post_id}` — soft delete (JWT + ownership)
- `GET    /health`, `GET /health/detailed`

## ⚙️ Environment (.env)
- `DATABASE_URL` (e.g., postgresql+asyncpg://user:pass@host:5432/post_db)
- `RABBITMQ_URL` (e.g., amqp://guest:guest@rabbitmq:5672/)
- `POST_EXCHANGE` (default `post_events`)
- `POST_ROUTING_KEY` (default `post.events`)
- `JWT_SECRET_KEY` (HS256)
- `JWT_ALGORITHM` (default `HS256`)
- `IDENTITY_SERVICE_URL` (should match JWT signing key)
- `DEFAULT_PAGE_SIZE` (default `20`), `MAX_PAGE_SIZE` (default `100`)
- `SERVICE_NAME`, `SERVICE_VERSION`, `DEBUG`
- No `.env.example` in repo — create manually

## ▶️ Local Run
```bash
python -m venv venv
source venv/bin/activate   # or Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
python run.py
```

## Docker
```bash
docker-compose up -d post-service
```

## 🧪 Tests
```bash
pytest
```

## 🧠 Notes / Design Decisions
- Event-driven: publishing lets other services react without tight coupling
- Database per service for data ownership and isolation
- Writes require JWT; reads remain public for performance
- Default pagination protects the database

## 🔐 Authentication Model
- JWTs issued by the Identity Service
- Algorithm: HS256 (default across services)
- Claims: `sub` = user_id, plus `exp`, `iat`
- Tokens are validated locally in this service (no runtime call to Identity Service); ensure the signing key matches the Identity Service configuration