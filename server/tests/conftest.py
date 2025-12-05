import pytest
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from models.db_models import Base


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine"""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a test database session"""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client():
    """Create a test client for the API"""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for web scraping"""
    with patch('scrapers.base.requests') as mock_requests:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''
        mock_requests.get.return_value = mock_response
        yield mock_requests


@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return {
        "id": uuid4(),
        "name": "Test Product",
        "description": "A test product",
        "category": "Electronics",
        "brand": "Test Brand",
        "sku": "TEST123",
        "upc": "123456789012",
        "ean": "1234567890123",
        "image_url": "https://example.com/image.jpg",
        "normalized_name": "test product"
    }


@pytest.fixture
def sample_source_data():
    """Sample source data for testing"""
    return {
        "id": 1,
        "name": "Test Store",
        "base_url": "https://teststore.com",
        "country_code": "US",
        "currency_code": "USD",
        "is_active": True,
        "rate_limit_per_minute": 60
    }


@pytest.fixture
def sample_product_source_data(sample_product_data, sample_source_data):
    """Sample product source data for testing"""
    return {
        "id": 1,
        "product_id": sample_product_data["id"],
        "source_id": sample_source_data["id"],
        "source_product_id": "12345",
        "source_product_url": "https://teststore.com/product/12345",
        "source_product_name": "Test Product from Store",
        "is_active": True
    }


@pytest.fixture
def sample_price_data():
    """Sample price data for testing"""
    return {
        "id": 1,
        "price": Decimal('99.99'),
        "currency_code": "USD",
        "original_price": Decimal('119.99'),
        "discount_percentage": Decimal('16.67'),
        "is_in_stock": True,
        "stock_quantity": 5,
        "shipping_cost": Decimal('5.99'),
        "scraped_at": datetime.now(timezone.utc),
        "raw_data": {"test": "data"}
    }


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing"""
    with patch('scrapers.base.RateLimiter') as mock_rate_limiter_class:
        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.wait_if_needed.return_value = None
        mock_rate_limiter_class.return_value = mock_rate_limiter_instance
        yield mock_rate_limiter_instance


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    session = Mock()
    session.query.return_value = session
    session.filter.return_value = session
    session.first.return_value = None
    session.all.return_value = []
    session.offset.return_value = session
    session.limit.return_value = session
    return session