import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from api.main import app
from models.db_models import Product, Source, ProductSource, Price
from models.schemas import ProductCreate


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    session = Mock()
    session.query.return_value = session
    session.filter.return_value = session
    session.first.return_value = None
    session.all.return_value = []
    session.offset.return_value = session
    session.limit.return_value = session
    return session


class TestProductsAPI:
    """Unit tests for product-related API endpoints"""

    def test_list_products_empty(self, client, mock_db_session):
        """Test listing products when none exist"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            response = client.get("/api/products/")
            assert response.status_code == 200
            assert response.json() == []

    def test_list_products_with_params(self, client, mock_db_session):
        """Test listing products with query parameters"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            # Mock a product to return
            mock_product = Product(
                id=uuid4(),
                name="Test Product",
                category="Electronics",
                brand="Test Brand"
            )
            mock_db_session.all.return_value = [mock_product]
            
            response = client.get("/api/products/?category=Electronics&brand=TestBrand")
            assert response.status_code == 200

    def test_get_product_not_found(self, client, mock_db_session):
        """Test getting a product that doesn't exist"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            invalid_uuid = str(uuid4())
            response = client.get(f"/api/products/{invalid_uuid}")
            assert response.status_code == 404

    def test_create_product(self, client, mock_db_session):
        """Test creating a product"""
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('models.utils.find_or_create_product') as mock_find_or_create:
            
            mock_get_db.__enter__.return_value = mock_db_session
            
            # Mock the return value
            mock_product = Product(
                id=uuid4(),
                name="New Test Product",
                category="Electronics"
            )
            mock_find_or_create.return_value = mock_product
            
            product_data = {
                "name": "New Test Product",
                "description": "A new test product",
                "category": "Electronics",
                "brand": "Test Brand",
                "sku": "TEST001",
                "image_url": "http://example.com/image.jpg"
            }
            
            response = client.post("/api/products/", json=product_data)
            assert response.status_code == 200
            assert response.json()["name"] == "New Test Product"

    def test_get_product_sources(self, client, mock_db_session):
        """Test retrieving product sources"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            # Mock product exists
            mock_product = Product(
                id=uuid4(),
                name="Test Product",
                category="Electronics"
            )
            mock_db_session.first.return_value = mock_product
            
            # Mock the join query result
            mock_source = Source(
                id=1,
                name="Test Store",
                base_url="https://teststore.com"
            )
            
            mock_product_source = ProductSource(
                id=1,
                product_id=mock_product.id,
                source_id=1,
                source_product_id="12345",
                source_product_url="https://teststore.com/product/12345"
            )
            
            # Mock the query.join().filter().all() chain
            mock_query = Mock()
            mock_query.join.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [(mock_product_source, mock_source)]
            mock_db_session.query.return_value = mock_query
            
            # Mock the price query
            with patch('api.routes.products.Price') as mock_price_model:
                mock_price = Mock()
                mock_price.price = Decimal('99.99')
                mock_db_session.query.return_value.order_by.return_value.first.return_value = mock_price
                
                response = client.get(f"/api/products/{mock_product.id}/sources")
                assert response.status_code == 200
                assert len(response.json()) == 1

    def test_get_product_price_history(self, client, mock_db_session):
        """Test retrieving product price history"""
        with patch('api.dependencies.get_db') as mock_get_db, \
             patch('api.routes.products.get_price_history') as mock_get_history:
            
            mock_get_db.__enter__.return_value = mock_db_session
            
            # Mock product exists
            mock_product = Product(
                id=uuid4(),
                name="Test Product",
                category="Electronics"
            )
            mock_db_session.first.return_value = mock_product
            
            # Mock product sources
            mock_product_source = ProductSource(
                id=1,
                product_id=mock_product.id,
                source_id=1,
                source_product_id="12345",
                source_product_url="https://teststore.com/product/12345"
            )
            mock_db_session.all.return_value = [mock_product_source]
            
            # Mock price history
            mock_price = Mock()
            mock_price.price = Decimal('99.99')
            mock_price.original_price = Decimal('119.99')
            mock_price.discount_percentage = Decimal('16.67')
            mock_price.is_in_stock = True
            mock_price.scraped_at = datetime.now(timezone.utc)
            mock_get_history.return_value = [mock_price]
            
            response = client.get(f"/api/products/{mock_product.id}/prices?days=30")
            assert response.status_code == 200


class TestSourcesAPI:
    """Unit tests for source-related API endpoints"""

    def test_list_sources_empty(self, client, mock_db_session):
        """Test listing sources when none exist"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            response = client.get("/api/sources/")
            assert response.status_code == 200
            assert response.json() == []


class TestPricesAPI:
    """Unit tests for price-related API endpoints"""

    def test_list_prices_empty(self, client, mock_db_session):
        """Test listing prices when none exist"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            response = client.get("/api/prices/")
            assert response.status_code == 200
            assert response.json() == []


class TestComparisonsAPI:
    """Unit tests for comparison-related API endpoints"""

    def test_list_comparisons_empty(self, client, mock_db_session):
        """Test listing comparisons when none exist"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            response = client.get("/api/comparisons/")
            assert response.status_code == 200
            assert response.json() == []


class TestAlertsAPI:
    """Unit tests for alert-related API endpoints"""

    def test_list_alerts_empty(self, client, mock_db_session):
        """Test listing alerts when none exist"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            response = client.get("/api/alerts/")
            assert response.status_code == 200
            assert response.json() == []


class TestAnalyticsAPI:
    """Unit tests for analytics-related API endpoints"""

    def test_get_analytics_empty(self, client, mock_db_session):
        """Test getting analytics when none exist"""
        with patch('api.dependencies.get_db') as mock_get_db:
            mock_get_db.__enter__.return_value = mock_db_session
            
            response = client.get("/api/analytics/")
            assert response.status_code == 200
            assert response.json() == {}


class TestAuthAPI:
    """Unit tests for authentication-related API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data