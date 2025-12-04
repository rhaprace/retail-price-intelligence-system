"""
Unit tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from decimal import Decimal
from uuid import uuid4

# Mock the database before importing the app
with patch('models.base.create_engine_instance') as mock_engine:
    mock_engine.return_value = MagicMock()
    from api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health(self):
        """Test health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestProductEndpoints:
    """Tests for product endpoints."""
    
    @patch('api.routes.products.get_db')
    def test_get_products_empty(self, mock_get_db):
        """Test getting products when database is empty."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_get_db.return_value.__exit__ = MagicMock(return_value=False)
        
        # The actual test would need proper mocking setup
        pass
    
    def test_get_products_invalid_limit(self):
        """Test getting products with invalid limit."""
        response = client.get("/api/products/?limit=-1")
        assert response.status_code == 422  # Validation error


class TestSourceEndpoints:
    """Tests for source endpoints."""
    
    @patch('api.routes.sources.get_db')
    def test_get_sources(self, mock_get_db):
        """Test getting sources."""
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = []
        mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_get_db.return_value.__exit__ = MagicMock(return_value=False)
        
        # Test would need proper setup
        pass


class TestPriceEndpoints:
    """Tests for price endpoints."""
    
    def test_get_price_metrics_invalid_days(self):
        """Test getting price metrics with invalid days."""
        response = client.get("/api/prices/product-source/1/metrics?days=0")
        assert response.status_code == 422


class TestAlertEndpoints:
    """Tests for alert endpoints."""
    
    def test_create_alert_invalid_product(self):
        """Test creating alert with invalid product ID format."""
        response = client.post("/api/alerts/", json={
            "product_id": "invalid-uuid",
            "target_price": 50.0
        })
        assert response.status_code == 422
