import re
from typing import Optional, Dict, Any, List
from decimal import Decimal
from bs4 import BeautifulSoup

from .base import BaseScraper


class SelectorExtractor:
    def extract_first_match(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None
    
    def extract_attribute(self, soup: BeautifulSoup, selectors: List[str], attributes: List[str]) -> Optional[str]:
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                for attr in attributes:
                    value = element.get(attr)
                    if value:
                        return value
        return None


class AmazonScraper(BaseScraper):
    ASIN_PATTERNS = [
        r'/dp/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})'
    ]
    
    NAME_SELECTORS = [
        '#productTitle',
        '#title',
        'h1.product-title-word-break',
        'span.product-title-word-break'
    ]
    
    PRICE_SELECTORS = [
        'span.a-price span.a-offscreen',
        '#priceblock_ourprice',
        '#priceblock_dealprice',
        '#priceblock_saleprice',
        'span.a-price-whole',
        '.a-price .a-offscreen'
    ]
    
    ORIGINAL_PRICE_SELECTORS = [
        'span.a-price.a-text-price span.a-offscreen',
        '#priceblock_listprice',
        '.a-text-strike',
        'span.priceBlockStrikePriceString'
    ]
    
    BRAND_SELECTORS = [
        '#bylineInfo',
        'a#bylineInfo',
        '.po-brand .a-span9 .a-size-base',
        'tr.po-brand td.a-span9 span'
    ]
    
    IMAGE_SELECTORS = [
        '#landingImage',
        '#imgBlkFront',
        '#main-image',
        '.a-dynamic-image'
    ]
    
    OUT_OF_STOCK_SELECTORS = [
        '#outOfStock',
        '#availability span.a-color-error',
        '.a-color-price.a-text-bold'
    ]
    
    def __init__(self, source_name: str = "Amazon US", db=None):
        super().__init__(source_name, db)
        self._selector_extractor = SelectorExtractor()
    
    def scrape_product(self, product_url: str) -> Optional[Dict[str, Any]]:
        try:
            self.rate_limiter.wait_if_needed(self.source_name)
            response = self.http_client.get(product_url)
            
            if response.status_code != 200:
                self.log_scraping(
                    status='error',
                    error_message=f"HTTP {response.status_code}",
                    http_status_code=response.status_code
                )
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            asin = self._extract_asin(product_url, soup)
            if not asin:
                return None
            
            name = self._extract_name(soup)
            if not name:
                return None

            price = self._extract_current_price(soup)
            if not price:
                return None
            
            original_price = self._extract_original_price(soup)
            
            brand = self._extract_brand(soup)
            category = self._extract_category(soup)
            image_url = self._extract_image(soup)
            is_in_stock = self._check_stock(soup)
            
            return {
                'name': name,
                'price': price,
                'original_price': original_price,
                'source_product_id': asin,
                'source_product_url': product_url,
                'source_product_name': name,
                'brand': brand,
                'category': category,
                'image_url': image_url,
                'is_in_stock': is_in_stock,
                'currency_code': 'USD',
                'raw_data': {
                    'asin': asin,
                    'url': product_url
                }
            }
            
        except Exception as e:
            self.log_scraping(
                status='error',
                error_message=str(e)
            )
            return None
    
    def _extract_asin(self, url: str, soup: BeautifulSoup) -> Optional[str]:
        for pattern in self.ASIN_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        asin_element = soup.find('input', {'id': 'ASIN'})
        if asin_element:
            return asin_element.get('value')
        
        return None
    
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        return self._selector_extractor.extract_first_match(soup, self.NAME_SELECTORS)
    
    def _extract_current_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        return self._extract_price_from_selectors(soup, self.PRICE_SELECTORS)
    
    def _extract_original_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        return self._extract_price_from_selectors(soup, self.ORIGINAL_PRICE_SELECTORS)
    
    def _extract_price_from_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[Decimal]:
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price = self._extract_price(element.get_text())
                if price:
                    return price
        return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        text = self._selector_extractor.extract_first_match(soup, self.BRAND_SELECTORS)
        if text:
            return self._clean_brand_text(text)
        return None
    
    def _clean_brand_text(self, text: str) -> str:
        text = re.sub(r'^Visit the\s+', '', text)
        text = re.sub(r'\s+Store$', '', text)
        text = re.sub(r'^Brand:\s*', '', text)
        return text
    
    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        breadcrumb = soup.select('#wayfinding-breadcrumbs_feature_div ul li a')
        if breadcrumb:
            categories = [a.get_text(strip=True) for a in breadcrumb]
            return categories[-1] if categories else None
        return None
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        return self._selector_extractor.extract_attribute(
            soup, self.IMAGE_SELECTORS, ['data-old-hires', 'src']
        )
    
    def _check_stock(self, soup: BeautifulSoup) -> bool:
        for selector in self.OUT_OF_STOCK_SELECTORS:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True).lower()
                if 'unavailable' in text or 'out of stock' in text:
                    return False
        
        availability = soup.select_one('#availability span')
        if availability:
            text = availability.get_text(strip=True).lower()
            return 'in stock' in text
        
        return True
    
    def search_products(self, query: str, max_results: int = 20) -> list:
        search_url = f"{self.source.base_url}/s?k={query.replace(' ', '+')}"
        
        try:
            self.rate_limiter.wait_if_needed(self.source_name)
            response = self.http_client.get(search_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_product_links(soup, max_results)
            
        except Exception:
            return []
    
    def _extract_product_links(self, soup: BeautifulSoup, max_results: int) -> list:
        product_links = []
        results = soup.select('[data-asin]:not([data-asin=""]) h2 a.a-link-normal')
        
        for link in results[:max_results]:
            href = link.get('href')
            if href:
                full_url = href if href.startswith('http') else f"{self.source.base_url}{href}"
                product_links.append(full_url)
        
        return product_links
