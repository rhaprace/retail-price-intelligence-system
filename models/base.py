"""
Base configuration for SQLAlchemy models.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from typing import Optional

Base = declarative_base()


def get_database_url() -> str:
    """
    Get database URL from environment variables.
    
    Returns:
        Database connection URL
    """
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    database = os.getenv('DB_NAME', 'retail_price_intelligence')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def create_engine_instance(
    database_url: Optional[str] = None,
    pool_size: int = 10,
    max_overflow: int = 20,
    echo: bool = False
):
    """
    Create SQLAlchemy engine instance.
    
    Args:
        database_url: Database connection URL (defaults to env vars)
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        echo: Enable SQL query logging
    
    Returns:
        SQLAlchemy engine
    """
    url = database_url or get_database_url()
    return create_engine(
        url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
        echo=echo
    )


def create_session_factory(engine=None):
    """
    Create SQLAlchemy session factory.
    
    Args:
        engine: SQLAlchemy engine (creates new if None)
    
    Returns:
        Session factory
    """
    if engine is None:
        engine = create_engine_instance()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


engine = create_engine_instance()
SessionLocal = create_session_factory(engine)


def get_db():
    """
    Dependency function to get database session.
    Use with FastAPI or similar frameworks.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

