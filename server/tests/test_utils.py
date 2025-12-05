import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models.utils import (
    normalize_product_name, 
    ProductLookup,
    find_or_create_product,
    get_or_create_product_source,
    insert_price,
    get_latest_price,
    get_price_history,
    calculate_price_metrics,
    get_source_by_name,
    get_active_sources
)
from models.db_models import Base, Product, ProductSource, Price, Source


class TestUtils:
    """Unit tests for utility functions in models/utils.py"""
    
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
    
    def test_normalize_product_name_basic(self):
        """Test basic product name normalization"""
        result = normalize_product_name("The Amazing Product")
        assert result == "amazing product"
    
    def test_normalize_product_name_with_stop_words(self):
        """Test product name normalization with various stop words"""
        result = normalize_product_name("A Great Product or The Item And More")
        assert result == "great product item more"
    
    def test_normalize_product_name_case_insensitive(self):
        """Test that normalization handles case correctly"""
        result = normalize_product_name("THE AMAZING PRODUCT")
        assert result == "amazing product"
    
    def test_normalize_product_name_no_stop_words(self):
        """Test normalization when no stop words are present"""
        result = normalize_product_name("Widget Product")
        assert result == "widget product"
    
    def test_product_lookup_find_by_identifier_sku(self, db_session):
        """Test finding product by SKU identifier"""
        # Create a product with SKU
        product = Product(
            name="Test Product",
            sku="TEST123",
            normalized_name="test product"
        )
        db_session.add(product)
        db_session.commit()
        
        # Find by SKU
        found = ProductLookup.find_by_identifier(db_session, sku="TEST123")
        assert found is not None
        assert found.id == product.id
    
    def test_product_lookup_find_by_identifier_upc(self, db_session):
        """Test finding product by UPC identifier"""
        # Create a product with UPC
        product = Product(
            name="Test Product",
            upc="123456789012",
            normalized_name="test product"
        )
        db_session.add(product)
        db_session.commit()
        
        # Find by UPC
        found = ProductLookup.find_by_identifier(db_session, upc="123456789012")
        assert found is not None
        assert found.id == product.id
    
    def test_product_lookup_find_by_identifier_ean(self, db_session):
        """Test finding product by EAN identifier"""
        # Create a product with EAN
        product = Product(
            name="Test Product",
            ean="1234567890123",
            normalized_name="test product"
        )
        db_session.add(product)
        db_session.commit()
        
        # Find by EAN
        found = ProductLookup.find_by_identifier(db_session, ean="1234567890123")
        assert found is not None
        assert found.id == product.id
    
    def test_product_lookup_find_by_normalized_name(self, db_session):
        """Test finding product by normalized name"""
        # Create a product with normalized name
        product = Product(
            name="The Amazing Product",
            normalized_name="amazing product"
        )
        db_session.add(product)
        db_session.commit()
        
        # Find by normalized name
        found = ProductLookup.find_by_normalized_name(db_session, "The Amazing Product")
        assert found is not None
        assert found.id == product.id
    
    def test_product_lookup_find_by_normalized_name_case_insensitive(self, db_session):
        """Test finding product by normalized name with different case"""
        # Create a product with normalized name
        product = Product(
            name="The Amazing Product",
            normalized_name="amazing product"
        )
        db_session.add(product)
        db_session.commit()
        
        # Find by normalized name with different case
        found = ProductLookup.find_by_normalized_name(db_session, "THE AMAZING PRODUCT")
        assert found is not None
        assert found.id == product.id
    
    def test_find_or_create_product_new(self, db_session):
        """Test creating a new product"""
        result = find_or_create_product(
            db=db_session,
            name="New Test Product",
            description="A new product",
            category="Electronics"
        )
        
        assert result is not None
        assert result.name == "New Test Product"
        assert result.description == "A new product"
        assert result.category == "Electronics"
        assert result.normalized_name == "new test product"
    
    def test_find_or_create_product_existing_by_sku(self, db_session):
        """Test finding existing product by SKU"""
        # Create a product
        existing_product = Product(
            name="Existing Product",
            sku="EXISTING123",
            normalized_name="existing product"
        )
        db_session.add(existing_product)
        db_session.commit()
        
        # Try to create another product with same SKU
        result = find_or_create_product(
            db=db_session,
            name="Different Name",
            sku="EXISTING123",
            description="Different description"
        )
        
        # Should return existing product, not create a new one
        assert result.id == existing_product.id
        assert result.name == "Existing Product"  # Original name should be preserved
    
    def test_find_or_create_product_existing_by_normalized_name(self, db_session):
        """Test finding existing product by normalized name"""
        # Create a product
        existing_product = Product(
            name="The Amazing Product",
            normalized_name="amazing product"
        )
        db_session.add(existing_product)
        db_session.commit()
        
        # Try to create another product with same normalized name
        result = find_or_create_product(
            db=db_session,
            name="The Amazing Product",  # Same normalized name
            description="New description"
        )
        
        # Should return existing product, not create a new one
        assert result.id == existing_product.id
        assert result.name == "The Amazing Product"
    
    def test_get_or_create_product_source_new(self, db_session):
        """Test creating a new product source"""
        from uuid import uuid4
        
        # Create a product and source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            normalized_name="test product"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )
        db_session.add_all([product, source])
        db_session.commit()
        
        # Create a product source
        result = get_or_create_product_source(
            db=db_session,
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345",
            source_product_name="Test Product from Store"
        )
        
        assert result is not None
        assert result.product_id == product.id
        assert result.source_id == source.id
        assert result.source_product_id == "12345"
        assert result.source_product_url == "https://teststore.com/product/12345"
        assert result.source_product_name == "Test Product from Store"
    
    def test_get_or_create_product_source_existing(self, db_session):
        """Test getting existing product source"""
        from uuid import uuid4
        
        # Create a product and source first
        product = Product(
            id=uuid4(),
            name="Test Product",
            normalized_name="test product"
        )
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )
        db_session.add_all([product, source])
        db_session.commit()
        
        # Create a product source initially
        existing = ProductSource(
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",
            source_product_url="https://teststore.com/product/12345",
            source_product_name="Old Name"
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to get or create the same product source
        updated = get_or_create_product_source(
            db=db_session,
            product_id=product.id,
            source_id=source.id,
            source_product_id="12345",  # Same ID
            source_product_url="https://teststore.com/product/12345/updated",
            source_product_name="Updated Name"
        )
        
        # Should return the same product source but updated
        assert updated.id == existing.id
        assert updated.source_product_url == "https://teststore.com/product/12345/updated"
        assert updated.source_product_name == "Updated Name"
        assert updated.is_active is True
    
    def test_insert_price(self, db_session):
        """Test inserting a price record"""
        from uuid import uuid4
        
        # Create product, source, and product_source
        product = Product(
            id=uuid4(),
            name="Test Product",
            normalized_name="test product"
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
        
        # Insert a price
        result = insert_price(
            db=db_session,
            product_source_id=product_source.id,
            price=Decimal('99.99'),
            currency_code="USD",
            original_price=Decimal('119.99'),
            is_in_stock=True,
            stock_quantity=5,
            shipping_cost=Decimal('5.99'),
            raw_data={"test": "data"}
        )
        
        assert result is not None
        assert result.product_source_id == product_source.id
        assert result.price == Decimal('99.99')
        assert result.currency_code == "USD"
        assert result.original_price == Decimal('119.99')
        assert result.is_in_stock is True
        assert result.stock_quantity == 5
        assert result.shipping_cost == Decimal('5.99')
        assert result.raw_data == {"test": "data"}
    
    def test_get_latest_price(self, db_session):
        """Test getting the latest price for a product source"""
        from uuid import uuid4

        # Create product, source, and product_source
        product = Product(
            id=uuid4(),
            name="Test Product",
            normalized_name="test product"
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

        # Insert two prices at different times
        older_time = datetime.now(timezone.utc) - timedelta(hours=1)
        newer_time = datetime.now(timezone.utc)

        older_price = Price(
            product_source_id=product_source.id,
            price=Decimal('89.99'),
            scraped_at=older_time
        )
        newer_price = Price(
            product_source_id=product_source.id,
            price=Decimal('99.99'),
            scraped_at=newer_time
        )

        db_session.add_all([older_price, newer_price])
        db_session.commit()

        # Get the latest price
        latest = get_latest_price(db_session, product_source.id)
        assert latest is not None
        assert latest.price == Decimal('99.99')
        # Handle timezone-aware datetime comparison
        # Ensure both datetimes are timezone-aware or both are naive
        assert latest.scraped_at.replace(tzinfo=None) >= newer_time.replace(tzinfo=None)
    
    def test_get_price_history(self, db_session):
        """Test getting price history for a product source"""
        from uuid import uuid4
        
        # Create product, source, and product_source
        product = Product(
            id=uuid4(),
            name="Test Product",
            normalized_name="test product"
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
        
        # Insert multiple prices
        time1 = datetime.now(timezone.utc) - timedelta(days=2)
        time2 = datetime.now(timezone.utc) - timedelta(days=1)
        time3 = datetime.now(timezone.utc)
        
        price1 = Price(
            product_source_id=product_source.id,
            price=Decimal('89.99'),
            scraped_at=time1
        )
        price2 = Price(
            product_source_id=product_source.id,
            price=Decimal('94.99'),
            scraped_at=time2
        )
        price3 = Price(
            product_source_id=product_source.id,
            price=Decimal('99.99'),
            scraped_at=time3
        )
        
        db_session.add_all([price1, price2, price3])
        db_session.commit()
        
        # Get price history (last 30 days)
        history = get_price_history(db_session, product_source.id, days=30)
        assert len(history) == 3
        # Should be ordered from newest to oldest
        assert history[0].price == Decimal('99.99')
        assert history[1].price == Decimal('94.99')
        assert history[2].price == Decimal('89.99')
    
    def test_get_price_history_with_limit(self, db_session):
        """Test getting price history with a limit"""
        from uuid import uuid4
        
        # Create product, source, and product_source
        product = Product(
            id=uuid4(),
            name="Test Product",
            normalized_name="test product"
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
        
        # Insert multiple prices
        for i in range(5):
            time_i = datetime.now(timezone.utc) - timedelta(days=i)
            price = Price(
                product_source_id=product_source.id,
                price=Decimal(f'{90 + i}.99'),
                scraped_at=time_i
            )
            db_session.add(price)
        
        db_session.commit()
        
        # Get price history with a limit of 3
        history = get_price_history(db_session, product_source.id, days=30, limit=3)
        assert len(history) == 3
        # Should return the 3 most recent prices
    
    def test_calculate_price_metrics(self, db_session):
        """Test calculating price metrics"""
        from uuid import uuid4
        
        # Create product, source, and product_source
        product = Product(
            id=uuid4(),
            name="Test Product",
            normalized_name="test product"
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
        
        # Insert multiple prices
        for price_val in [Decimal('89.99'), Decimal('94.99'), Decimal('99.99')]:
            price = Price(
                product_source_id=product_source.id,
                price=price_val,
                scraped_at=datetime.now(timezone.utc)
            )
            db_session.add(price)
        
        db_session.commit()
        
        # Calculate metrics
        metrics = calculate_price_metrics(db_session, product_source.id, days=30)
        
        assert metrics['min_price'] == Decimal('89.99')
        assert metrics['max_price'] == Decimal('99.99')
        # Average should be around 94.99
        assert Decimal('94.90') < metrics['avg_price'] < Decimal('95.10')
    
    def test_get_source_by_name(self, db_session):
        """Test getting a source by name"""
        # Create a source
        source = Source(
            name="Test Store",
            base_url="https://teststore.com"
        )
        db_session.add(source)
        db_session.commit()
        
        # Get source by name
        found = get_source_by_name(db_session, "Test Store")
        assert found is not None
        assert found.id == source.id
        assert found.name == "Test Store"
    
    def test_get_active_sources(self, db_session):
        """Test getting all active sources"""
        # Create multiple sources with different active states
        active_source1 = Source(
            name="Active Store 1",
            base_url="https://active1.com",
            is_active=True
        )
        active_source2 = Source(
            name="Active Store 2",
            base_url="https://active2.com",
            is_active=True
        )
        inactive_source = Source(
            name="Inactive Store",
            base_url="https://inactive.com",
            is_active=False
        )
        
        db_session.add_all([active_source1, active_source2, inactive_source])
        db_session.commit()
        
        # Get active sources
        active_sources = get_active_sources(db_session)
        assert len(active_sources) == 2
        source_names = {source.name for source in active_sources}
        assert "Active Store 1" in source_names
        assert "Active Store 2" in source_names
        assert "Inactive Store" not in source_names