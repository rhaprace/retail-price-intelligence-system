"""
Unit tests for scrapers.
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, Dict, Any

from scrapers.base import BaseScraper


# Concrete implementation for testing
class TestScraperImpl(BaseScraper):
    """Concrete scraper implementation for testing."""
    
    def __init__(self):
        # Skip parent init to avoid DB dependencies
        self.source_name = "Test"
        self.db = None
        self.http_client = None
        self.rate_limiter = None
        self.source = None
    
    def scrape_product(self, product_url: str) -> Optional[Dict[str, Any]]:
        return None


class TestBaseScraper:
    """Tests for BaseScraper."""
    
    def test_extract_price_usd(self):
        """Test extracting USD prices."""
        scraper = TestScraperImpl()
        result = scraper._extract_price("$99.99")
        assert result == Decimal("99.99")
    
    def test_extract_price_with_commas(self):
        """Test extracting prices with commas."""
        scraper = TestScraperImpl()
        result = scraper._extract_price("$1,299.99")
        assert result == Decimal("1299.99")
    
    def test_extract_price_euro(self):
        """Test extracting Euro prices."""
        scraper = TestScraperImpl()
        result = scraper._extract_price("€49.99")
        assert result == Decimal("49.99")
    
    def test_extract_price_empty(self):
        """Test extracting from empty string."""
        scraper = TestScraperImpl()
        result = scraper._extract_price("")
        assert result is None
    
    def test_extract_price_none(self):
        """Test extracting from None."""
        scraper = TestScraperImpl()
        result = scraper._extract_price(None)
        assert result is None


class TestAmazonScraper:
    """Tests for Amazon scraper."""
    
    def test_extract_asin_from_dp_url(self):
        """Test extracting ASIN from /dp/ URL."""
        from scrapers.amazon import AmazonScraper
        from bs4 import BeautifulSoup
        
        with patch.object(AmazonScraper, '__init__', lambda self, *args, **kwargs: None):
            scraper = AmazonScraper.__new__(AmazonScraper)
            soup = BeautifulSoup("<html></html>", 'html.parser')
            
            url = "https://www.amazon.com/dp/B08N5WRWNW"
            result = scraper._extract_asin(url, soup)
            assert result == "B08N5WRWNW"
    
    def test_extract_asin_from_gp_url(self):
        """Test extracting ASIN from /gp/product/ URL."""
        from scrapers.amazon import AmazonScraper
        from bs4 import BeautifulSoup
        
        with patch.object(AmazonScraper, '__init__', lambda self, *args, **kwargs: None):
            scraper = AmazonScraper.__new__(AmazonScraper)
            soup = BeautifulSoup("<html></html>", 'html.parser')
            
            url = "https://www.amazon.com/gp/product/B08N5WRWNW"
            result = scraper._extract_asin(url, soup)
            assert result == "B08N5WRWNW"


class TestEbayScraper:
    """Tests for eBay scraper."""
    
    def test_extract_item_id(self):
        """Test extracting eBay item ID."""
        from scrapers.ebay import EbayScraper
        
        with patch.object(EbayScraper, '__init__', lambda self, *args, **kwargs: None):
            scraper = EbayScraper.__new__(EbayScraper)
            
            url = "https://www.ebay.com/itm/product-name/123456789"
            result = scraper._extract_item_id(url)
            assert result == "123456789"
    
    def test_extract_item_id_short_url(self):
        """Test extracting item ID from short URL."""
        from scrapers.ebay import EbayScraper
        
        with patch.object(EbayScraper, '__init__', lambda self, *args, **kwargs: None):
            scraper = EbayScraper.__new__(EbayScraper)
            
            url = "https://www.ebay.com/itm/123456789"
            result = scraper._extract_item_id(url)
            assert result == "123456789"


class TestWalmartScraper:
    """Tests for Walmart scraper."""
    
    def test_extract_item_id(self):
        """Test extracting Walmart item ID."""
        from scrapers.walmart import WalmartScraper
        
        with patch.object(WalmartScraper, '__init__', lambda self, *args, **kwargs: None):
            scraper = WalmartScraper.__new__(WalmartScraper)
            
            url = "https://www.walmart.com/ip/product-name/123456789"
            result = scraper._extract_item_id(url)
            assert result == "123456789"
