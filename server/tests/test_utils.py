"""
Unit tests for utility functions.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone

from models.utils import normalize_product_name


class TestNormalizeProductName:
    """Tests for product name normalization."""
    
    def test_lowercase(self):
        """Test that names are lowercased."""
        result = normalize_product_name("HELLO WORLD")
        assert result == "hello world"
    
    def test_strip_whitespace(self):
        """Test that whitespace is stripped."""
        result = normalize_product_name("  hello world  ")
        assert result == "hello world"
    
    def test_remove_stop_words(self):
        """Test that stop words are removed."""
        result = normalize_product_name("The quick brown fox")
        assert "the" not in result
        assert "quick" in result
    
    def test_empty_string(self):
        """Test with empty string."""
        result = normalize_product_name("")
        assert result == ""
    
    def test_only_stop_words(self):
        """Test string with only stop words."""
        result = normalize_product_name("the a an")
        assert result == ""


class TestRateLimiter:
    """Tests for rate limiter."""
    
    def test_rate_limiter_init(self):
        """Test rate limiter initialization."""
        from utils.rate_limiter import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=60)
        assert limiter.requests_per_minute == 60
        assert limiter.min_interval == 1.0
    
    def test_rate_limiter_reset(self):
        """Test rate limiter reset."""
        from utils.rate_limiter import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=60)
        limiter.last_request['test'] = 12345
        limiter.reset('test')
        assert limiter.last_request['test'] == 0.0


class TestHTTPClient:
    """Tests for HTTP client."""
    
    def test_client_init(self):
        """Test HTTP client initialization."""
        from utils.http_client import HTTPClient
        
        client = HTTPClient(timeout=30, max_retries=3)
        assert client.timeout == 30
        assert client.max_retries == 3
        client.close()
    
    def test_client_custom_user_agent(self):
        """Test custom user agent."""
        from utils.http_client import HTTPClient
        
        custom_agent = "TestBot/1.0"
        client = HTTPClient(user_agent=custom_agent)
        assert client.user_agent == custom_agent
        client.close()
