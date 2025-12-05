import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models.db_models import (
    Base, Source, Product, ProductSource, Price,
    PriceAlert, DiscountAnalysis, PriceComparison, ScrapingLog
)


class TestDatabaseModels:
    """Unit tests for database models in models/db_models.py"""

    @pytest.fixture(scope="function")
    def db_session(self):
        """Create an in-memory SQLite database for testing"""
        engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        try:
            yield session
        finally:
            session.close()
            engine.dispose()

    def test_source_model(self, db_session):
        """Test Source model creation and properties"""
        # Create a source instance
        source = Source(
            name="Test Store",
            base_url="https://teststore.com",
            country_code="US",
            currency_code="USD",
            is_active=True,
            rate_limit_per_minute=60
        )

        # Add to session and commit
        db_session.add(source)
        db_session.commit()

        # Verify the source was created correctly
        assert source.id is not None
        assert source.name == "Test Store"
        assert source.base_url == "https://teststore.com"
        assert source.country_code == "US"
        assert source.currency_code == "USD"
        assert source.is_active is True
        assert source.rate_limit_per_minute == 60

        # Verify timestamps were set
        assert source.created_at is not None
        assert source.updated_at is not None

        # Test repr method
        expected_repr = "Source(id=1, name=Test Store)"
        assert expected_repr in repr(source)

    def test_product_model(self, db_session):
        """Test Product model creation and properties"""
        from uuid import uuid4

        # Create a product instance
        product = Product(
            id=uuid4(),  # Generate a new UUID
            name="Test Product",
            description="A test product",
            category="Electronics",
            brand="Test Brand",
            sku="TEST123",
            image_url="https://example.com/image.jpg",
            normalized_name="test product"
        )

        # Add to session and commit
        db_session.add(product)
        db_session.commit()

        # Verify the product was created correctly
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.description == "A test product"
        assert product.category == "Electronics"
        assert product.brand == "Test Brand"
        assert product.sku == "TEST123"
        assert product.image_url == "https://example.com/image.jpg"
        assert product.normalized_name == "test product"

        # Verify timestamps were set
        assert product.created_at is not None
        assert product.updated_at is not None

        # Test repr method
        expected_repr = "<Product(id="
        assert expected_repr in repr(product)

    def test_product_source_model(self, db_session):
        """Test ProductSource model creation and relationships"""
        from uuid import uuid4

        # Create a product and source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            category="Electronics"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )

        db_session.add_all([product, source])
        db_session.commit()

        # Create a product_source instance
        product_source = ProductSource(
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345",
            source_product_name="Test Product from Store"
        )

        db_session.add(product_source)
        db_session.commit()

        # Verify the product_source was created correctly
        assert product_source.id is not None
        assert product_source.product_id == product.id
        assert product_source.source_id == source.id
        assert product_source.source_product_id == "12345"
        assert product_source.source_product_url == "https://teststore.com/product/12345"
        assert product_source.source_product_name == "Test Product from Store"
        assert product_source.is_active is True  # Default value

        # Verify timestamps were set
        assert product_source.created_at is not None
        assert product_source.updated_at is not None

        # Test repr method
        expected_repr = f"<ProductSource(id={product_source.id}, product_id={product.id}, source_id={source.id})>"
        assert str(product_source) == expected_repr

    def test_price_model(self, db_session):
        """Test Price model creation and validation"""
        from uuid import uuid4

        # Create a product, source, and product_source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            category="Electronics"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )

        db_session.add_all([product, source])
        db_session.commit()

        product_source = ProductSource(
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345"
        )

        db_session.add(product_source)
        db_session.commit()

        # Create a price instance
        price = Price(
            product_source_id=product_source.id,
            price=Decimal('99.99'),
            currency_code="USD",
            original_price=Decimal('119.99'),
            discount_percentage=Decimal('16.67'),
            is_in_stock=True,
            stock_quantity=5,
            shipping_cost=Decimal('5.99'),
            raw_data={"test": "data"}
        )

        db_session.add(price)
        db_session.commit()

        # Verify the price was created correctly
        assert price.id is not None
        assert price.product_source_id == product_source.id
        assert price.price == Decimal('99.99')
        assert price.currency_code == "USD"
        assert price.original_price == Decimal('119.99')
        assert price.discount_percentage == Decimal('16.67')
        assert price.is_in_stock is True
        assert price.stock_quantity == 5
        assert price.shipping_cost == Decimal('5.99')
        assert price.raw_data == {"test": "data"}

        # Verify timestamps were set
        assert price.created_at is not None
        assert price.scraped_at is not None

        # Test repr method
        expected_repr = "Price(id=1, price=99.99)"
        assert repr(price) == expected_repr

    def test_price_model_negative_price_constraint(self, db_session):
        """Test Price model constraint for positive prices"""
        from uuid import uuid4

        # Create a product, source, and product_source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            category="Electronics"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )

        db_session.add_all([product, source])
        db_session.commit()

        product_source = ProductSource(
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345"
        )

        db_session.add(product_source)
        db_session.commit()

        # Try to create a price with negative value
        with pytest.raises(Exception):
            price = Price(
                product_source_id=product_source.id,
                price=Decimal('-10.00')  # Negative price should fail constraint
            )
            db_session.add(price)
            db_session.commit()

    def test_price_alert_model(self, db_session):
        """Test PriceAlert model creation and properties"""
        from uuid import uuid4

        # Create a product first
        product = Product(
            id=uuid4(),
            name="Test Product",
            category="Electronics"
        )

        db_session.add(product)
        db_session.commit()

        # Create a price alert
        alert = PriceAlert(
            product_id=product.id,
            user_email="test@example.com",
            target_price=Decimal('50.00'),
            price_drop_percentage=Decimal('20.0'),
            is_active=True
        )

        db_session.add(alert)
        db_session.commit()

        # Verify the alert was created correctly
        assert alert.id is not None
        assert alert.product_id == product.id
        assert alert.user_email == "test@example.com"
        assert alert.target_price == Decimal('50.00')
        assert alert.price_drop_percentage == Decimal('20.0')
        assert alert.is_active is True
        assert alert.trigger_count == 0  # Default value

        # Verify timestamps were set
        assert alert.created_at is not None
        assert alert.updated_at is not None

        # Test repr method
        expected_repr = f"<PriceAlert(id={alert.id}, product_id={product.id}, is_active=True)>"
        assert str(alert) == expected_repr

    def test_discount_analysis_model(self, db_session):
        """Test DiscountAnalysis model creation and properties"""
        from uuid import uuid4

        # Create a product, source, and product_source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            category="Electronics"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )

        db_session.add_all([product, source])
        db_session.commit()

        product_source = ProductSource(
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345"
        )

        db_session.add(product_source)
        db_session.commit()

        # Create a discount analysis
        analysis = DiscountAnalysis(
            product_source_id=product_source.id,
            analysis_date=datetime.now(timezone.utc),
            min_price_30d=Decimal('50.00'),
            max_price_30d=Decimal('100.00'),
            avg_price_30d=Decimal('75.00'),
            current_price=Decimal('60.00'),
            claimed_discount_percentage=Decimal('25.0'),
            actual_discount_percentage=Decimal('10.0'),
            is_fake_discount=False,
            fake_discount_reason="Price was not artificially inflated",
            price_trend="decreasing"
        )

        db_session.add(analysis)
        db_session.commit()

        # Verify the analysis was created correctly
        assert analysis.id is not None
        assert analysis.product_source_id == product_source.id
        assert analysis.min_price_30d == Decimal('50.00')
        assert analysis.max_price_30d == Decimal('100.00')
        assert analysis.avg_price_30d == Decimal('75.00')
        assert analysis.current_price == Decimal('60.00')
        assert analysis.claimed_discount_percentage == Decimal('25.0')
        assert analysis.actual_discount_percentage == Decimal('10.0')
        assert analysis.is_fake_discount is False
        assert analysis.fake_discount_reason == "Price was not artificially inflated"
        assert analysis.price_trend == "decreasing"

        # Verify timestamp was set
        assert analysis.created_at is not None

        # Test repr method
        expected_repr = f"<DiscountAnalysis(id={analysis.id}, is_fake_discount=False)>"
        assert str(analysis) == expected_repr

    def test_price_comparison_model(self, db_session):
        """Test PriceComparison model creation and properties"""
        from uuid import uuid4

        # Create a product and source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            category="Electronics"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )

        db_session.add_all([product, source])
        db_session.commit()

        product_source = ProductSource(
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345"
        )

        db_session.add(product_source)
        db_session.commit()

        # Create a price comparison
        comparison = PriceComparison(
            product_id=product.id,
            comparison_date=datetime.now(timezone.utc),
            best_price=Decimal('45.00'),
            best_price_source_id=source.id,
            best_price_product_source_id=product_source.id,
            min_price=Decimal('45.00'),
            max_price=Decimal('60.00'),
            price_variance=Decimal('15.00'),
            source_count=3
        )

        db_session.add(comparison)
        db_session.commit()

        # Verify the comparison was created correctly
        assert comparison.id is not None
        assert comparison.product_id == product.id
        assert comparison.best_price == Decimal('45.00')
        assert comparison.best_price_source_id == source.id
        assert comparison.best_price_product_source_id == product_source.id
        assert comparison.min_price == Decimal('45.00')
        assert comparison.max_price == Decimal('60.00')
        assert comparison.price_variance == Decimal('15.00')
        assert comparison.source_count == 3

        # Verify timestamp was set
        assert comparison.created_at is not None

        # Test repr method
        expected_repr = f"<PriceComparison(id={comparison.id}, product_id={product.id}, best_price=45.00)>"
        assert str(comparison) == expected_repr

    def test_scraping_log_model(self, db_session):
        """Test ScrapingLog model creation and properties"""
        from uuid import uuid4

        # Create a product, source, and product_source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            category="Electronics"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )

        db_session.add_all([product, source])
        db_session.commit()

        product_source = ProductSource(
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345"
        )

        db_session.add(product_source)
        db_session.commit()

        # Create a scraping log
        log = ScrapingLog(
            source_id=source.id,
            product_source_id=product_source.id,
            status="success",
            error_message=None,
            response_time_ms=150,
            http_status_code=200,
            scraped_count=10,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )

        db_session.add(log)
        db_session.commit()

        # Verify the log was created correctly
        assert log.id is not None
        assert log.source_id == source.id
        assert log.product_source_id == product_source.id
        assert log.status == "success"
        assert log.error_message is None
        assert log.response_time_ms == 150
        assert log.http_status_code == 200
        assert log.scraped_count == 10
        assert log.started_at is not None
        assert log.completed_at is not None

        # Verify timestamp was set
        assert log.created_at is not None

        # Test repr method
        expected_repr = f"<ScrapingLog(id={log.id}, status='success', source_id={source.id})>"
        assert str(log) == expected_repr