# Post Service

A FastAPI-based microservice for managing user posts with RabbitMQ messaging integration.

## Features

- **CRUD Operations**: Create, read, update, delete posts
- **Search & Filtering**: Search posts by content, filter by tags and users
- **Pagination**: Efficient pagination for large datasets
- **Event-Driven**: RabbitMQ integration for real-time events
- **Authentication**: JWT token validation for secure operations
- **Clean Architecture**: Layered design with repositories and services

## Architecture

The service follows a clean architecture pattern:

- **API Layer**: FastAPI routers handling HTTP requests
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access and database operations
- **Models**: SQLAlchemy ORM models
- **Schemas**: Pydantic models for request/response validation
- **Messaging**: RabbitMQ integration for event publishing

## API Endpoints

### Posts Management
- `POST /posts` - Create a new post
- `GET /posts/{post_id}` - Get post by ID
- `GET /posts` - Search posts with filters
- `GET /posts/users/{user_id}` - Get posts by user
- `GET /posts/me/posts` - Get current user's posts
- `PUT /posts/{post_id}` - Update post
- `DELETE /posts/{post_id}` - Delete post

### Health Checks
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with dependencies

## Event System

The service publishes events to RabbitMQ for other services:

- `post.created` - When a new post is created
- `post.updated` - When a post is updated
- `post.deleted` - When a post is deleted

## Setup and Running

### Using Docker Compose (Recommended)

```bash
# Start all services including PostgreSQL and RabbitMQ
docker-compose up -d

# View logs
docker-compose logs -f post-service
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations (after setting up PostgreSQL)
alembic upgrade head

# Start the service
python run.py
```

## Environment Variables

Key environment variables (see `.env` file):

- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `JWT_SECRET_KEY`: Secret key for JWT validation
- `DEBUG`: Enable debug mode

## Database Schema

The service uses a simple post model:

- `id`: UUID primary key
- `user_id`: UUID of the post creator
- `title`: Post title (max 255 chars)
- `content`: Post content (text)
- `tags`: Array of tag strings
- `likes_count`: Denormalized like count
- `comments_count`: Denormalized comment count
- `is_active`: Soft delete flag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Dependencies

- PostgreSQL 15+ for data persistence
- RabbitMQ 3.12+ for event messaging
- Python 3.12+ runtime environment

## Development

The codebase follows these principles:

- **Clean Architecture**: Separation of concerns across layers
- **Functional Programming**: Immutable data where possible
- **English Comments**: All code comments in English
- **Type Hints**: Full typing support with mypy compatibility

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```