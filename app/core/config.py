"""Configuration management for Post Service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/post_db"
    
    # Service Configuration
    service_name: str = "Post Service"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # RabbitMQ Configuration
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    post_exchange: str = "post_events"
    post_routing_key: str = "post.events"
    
    # JWT Configuration for authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    
    # External Services
    identity_service_url: str = "http://identity-service:8000"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables like POSTGRES_USER, POSTGRES_PASSWORD, etc.


settings = Settings()