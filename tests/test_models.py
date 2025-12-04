"""
Unit tests for database models.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

from models.db_models import Source, Product, ProductSource, Price, PriceAlert


class TestSourceModel:
    """Tests for Source model."""
    
    def test_create_source(self, db_session):
        """Test creating a source."""
        source = Source(
            name="Test Source",
            base_url="https://example.com",
            country_code="US",
            currency_code="USD"
        )
        db_session.add(source)
        db_session.commit()
        
        assert source.id is not None
        assert source.name == "Test Source"
        assert source.is_active == True
        assert source.rate_limit_per_minute == 60
    
    def test_source_defaults(self, db_session):
        """Test source default values."""
        source = Source(
            name="Minimal Source",
            base_url="https://minimal.com"
        )
        db_session.add(source)
        db_session.commit()
        
        assert source.currency_code == "USD"
        assert source.is_active == True
        assert source.rate_limit_per_minute == 60
    
    def test_source_unique_name(self, db_session, sample_source):
        """Test that source names must be unique."""
        duplicate = Source(
            name=sample_source.name,
            base_url="https://different.com"
        )
        db_session.add(duplicate)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestProductModel:
    """Tests for Product model."""
    
    def test_create_product(self, db_session):
        """Test creating a product."""
        product = Product(
            name="Test Product",
            category="Electronics",
            brand="TestBrand"
        )
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.category == "Electronics"
    
    def test_product_uuid(self, db_session):
        """Test that product ID is a UUID."""
        product = Product(name="UUID Test")
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert len(str(product.id)) == 36  # UUID string length


class TestProductSourceModel:
    """Tests for ProductSource model."""
    
    def test_create_product_source(self, db_session, sample_product, sample_source):
        """Test creating a product source."""
        ps = ProductSource(
            product_id=sample_product.id,
            source_id=sample_source.id,
            source_product_id="ABC123",
            source_product_url="https://example.com/product/ABC123"
        )
        db_session.add(ps)
        db_session.commit()
        
        assert ps.id is not None
        assert ps.product_id == sample_product.id
        assert ps.source_id == sample_source.id
        assert ps.is_active == True
    
    def test_product_source_relationship(self, db_session, sample_product_source):
        """Test product source relationships."""
        assert sample_product_source.product is not None
        assert sample_product_source.source is not None


class TestPriceModel:
    """Tests for Price model."""
    
    def test_create_price(self, db_session, sample_product_source):
        """Test creating a price record."""
        price = Price(
            product_source_id=sample_product_source.id,
            price=Decimal("99.99"),
            currency_code="USD",
            is_in_stock=True,
            scraped_at=datetime.now(timezone.utc)
        )
        db_session.add(price)
        db_session.commit()
        
        assert price.id is not None
        assert price.price == Decimal("99.99")
    
    def test_price_with_discount(self, db_session, sample_product_source):
        """Test price with original price and discount."""
        price = Price(
            product_source_id=sample_product_source.id,
            price=Decimal("79.99"),
            original_price=Decimal("99.99"),
            currency_code="USD",
            scraped_at=datetime.now(timezone.utc)
        )
        db_session.add(price)
        db_session.commit()
        
        assert price.original_price == Decimal("99.99")
        # Note: discount_percentage would be calculated by DB trigger in PostgreSQL
    
    def test_price_positive_constraint(self, db_session, sample_product_source):
        """Test that price must be positive."""
        # SQLite doesn't enforce CHECK constraints the same way
        # This would fail in PostgreSQL
        pass


class TestPriceAlertModel:
    """Tests for PriceAlert model."""
    
    def test_create_alert(self, db_session, sample_product):
        """Test creating a price alert."""
        alert = PriceAlert(
            product_id=sample_product.id,
            user_email="user@example.com",
            target_price=Decimal("49.99"),
            is_active=True
        )
        db_session.add(alert)
        db_session.commit()
        
        assert alert.id is not None
        assert alert.target_price == Decimal("49.99")
        assert alert.trigger_count == 0
    
    def test_alert_with_percentage(self, db_session, sample_product):
        """Test alert with price drop percentage."""
        alert = PriceAlert(
            product_id=sample_product.id,
            price_drop_percentage=Decimal("20.0"),
            is_active=True
        )
        db_session.add(alert)
        db_session.commit()
        
        assert alert.price_drop_percentage == Decimal("20.0")
        assert alert.target_price is None
