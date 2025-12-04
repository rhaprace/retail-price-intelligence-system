import pytest
import os
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

os.environ['DB_NAME'] = 'retail_price_intelligence_test'

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.db_models import Source, Product, ProductSource, Price, PriceAlert


@pytest.fixture(scope="function")
def engine():
    test_engine = create_engine(
        "sqlite:///:memory:",
        echo=False
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture
def sample_source(db_session):
    source = Source(
        name=f"Test Amazon {uuid4().hex[:8]}",
        base_url="https://www.amazon.com",
        country_code="US",
        currency_code="USD",
        rate_limit_per_minute=60
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    return source


@pytest.fixture
def sample_product(db_session):
    product = Product(
        id=uuid4(),
        name="Test Product",
        description="A test product for unit testing",
        category="Electronics",
        brand="TestBrand",
        sku="TEST-SKU-001"
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_product_source(db_session, sample_product, sample_source):
    product_source = ProductSource(
        product_id=sample_product.id,
        source_id=sample_source.id,
        source_product_id="B001234567",
        source_product_url="https://www.amazon.com/dp/B001234567",
        source_product_name="Test Product on Amazon"
    )
    db_session.add(product_source)
    db_session.commit()
    db_session.refresh(product_source)
    return product_source


@pytest.fixture
def sample_prices(db_session, sample_product_source):
    prices = []
    base_price = Decimal("99.99")
    
    for i in range(10):
        price = Price(
            product_source_id=sample_product_source.id,
            price=base_price - Decimal(str(i * 2)),
            currency_code="USD",
            original_price=Decimal("129.99"),
            is_in_stock=True,
            scraped_at=datetime.now(timezone.utc)
        )
        prices.append(price)
        db_session.add(price)
    
    db_session.commit()
    for p in prices:
        db_session.refresh(p)
    
    return prices


@pytest.fixture
def sample_alert(db_session, sample_product):
    alert = PriceAlert(
        product_id=sample_product.id,
        user_email="test@example.com",
        target_price=Decimal("79.99"),
        is_active=True
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert
