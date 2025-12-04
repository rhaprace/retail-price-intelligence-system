from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


def get_database_url() -> str:
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
    if engine is None:
        engine = create_engine_instance()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


engine = create_engine_instance()
SessionLocal = create_session_factory(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

