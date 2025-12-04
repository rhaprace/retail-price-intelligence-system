import re
import json
from typing import Optional, Dict, Any
from decimal import Decimal
from bs4 import BeautifulSoup

from .base import BaseScraper


class WalmartScraper(BaseScraper):
    def __init__(self, source_name: str = "Walmart", db=None):
        super().__init__(source_name, db)
    
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
            
            json_data = self._extract_json_ld(soup)
            if json_data:
                return self._parse_json_ld(json_data, product_url)
            
            return self._parse_html(soup, product_url)
            
        except Exception as e:
            self.log_scraping(
                status='error',
                error_message=str(e)
            )
            return None
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    return data
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            return item
            except (json.JSONDecodeError, TypeError):
                continue
        
        return None
    
    def _parse_json_ld(self, data: Dict, url: str) -> Optional[Dict[str, Any]]:
        item_id = self._extract_item_id(url)
        if not item_id:
            return None
        
        name = data.get('name')
        if not name:
            return None
        
        offers = data.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        price_str = offers.get('price')
        price = Decimal(str(price_str)) if price_str else None
        if not price:
            return None
        
        availability = offers.get('availability', '')
        is_in_stock = 'InStock' in availability or 'LimitedAvailability' in availability
        
        return {
            'name': name,
            'price': price,
            'original_price': None,
            'source_product_id': item_id,
            'source_product_url': url,
            'source_product_name': name,
            'brand': data.get('brand', {}).get('name'),
            'category': data.get('category'),
            'image_url': data.get('image'),
            'is_in_stock': is_in_stock,
            'currency_code': offers.get('priceCurrency', 'USD'),
            'sku': data.get('sku'),
            'raw_data': {
                'item_id': item_id,
                'gtin': data.get('gtin13'),
                'url': url
            }
        }
    
    def _parse_html(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        item_id = self._extract_item_id(url)
        if not item_id:
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
            'source_product_id': item_id,
            'source_product_url': url,
            'source_product_name': name,
            'brand': brand,
            'category': category,
            'image_url': image_url,
            'is_in_stock': is_in_stock,
            'currency_code': 'USD',
            'raw_data': {
                'item_id': item_id,
                'url': url
            }
        }
    
    def _extract_item_id(self, url: str) -> Optional[str]:
        match = re.search(r'/ip/(?:[^/]+/)?(\d+)', url)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            'h1[itemprop="name"]',
            'h1.prod-ProductTitle',
            'h1.f3.b.lh-copy',
            '[data-testid="product-title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        
        return None
    
    def _extract_current_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        selectors = [
            '[itemprop="price"]',
            'span.price-characteristic',
            '[data-testid="price-wrap"] span.f2',
            '.price-group .price-characteristic'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_content = element.get('content')
                if price_content:
                    try:
                        return Decimal(price_content)
                    except:
                        pass
                
                price = self._extract_price(element.get_text())
                if price:
                    return price
        
        return None
    
    def _extract_original_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        selectors = [
            '.price-old .price-characteristic',
            '[data-testid="was-price"] span',
            '.strike-through .price-characteristic'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price = self._extract_price(element.get_text())
                if price:
                    return price
        
        return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            'a.prod-brandName',
            '[itemprop="brand"]',
            '[data-testid="product-brand"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        
        return None
    
    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        breadcrumbs = soup.select('nav[aria-label="breadcrumb"] a, .breadcrumb-list a')
        if breadcrumbs:
            categories = [b.get_text(strip=True) for b in breadcrumbs]
            if categories:
                return categories[-1]
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            'img[data-testid="hero-image"]',
            '.prod-hero-image img',
            'img.hover-zoom-hero-image'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                url = element.get('src')
                if url:
                    return url
        
        return None
    
    def _check_stock(self, soup: BeautifulSoup) -> bool:
        out_of_stock = soup.select_one('[data-testid="out-of-stock-message"]')
        if out_of_stock:
            return False
        
        add_to_cart = soup.select_one('[data-testid="add-to-cart-button"]')
        if add_to_cart:
            return True
        
        return True
    
    def search_products(self, query: str, max_results: int = 20) -> list:
        search_url = f"{self.source.base_url}/search?q={query.replace(' ', '+')}"
        
        try:
            self.rate_limiter.wait_if_needed(self.source_name)
            response = self.http_client.get(search_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_links = []
            results = soup.select('[data-item-id] a[href*="/ip/"]')
            
            seen = set()
            for link in results:
                href = link.get('href')
                if href and '/ip/' in href:
                    if not href.startswith('http'):
                        href = f"{self.source.base_url}{href}"
                    if href not in seen:
                        seen.add(href)
                        product_links.append(href)
                        if len(product_links) >= max_results:
                            break
            
            return product_links
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
