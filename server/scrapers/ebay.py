"""
eBay scraper implementation.
"""
import re
from typing import Optional, Dict, Any
from decimal import Decimal
from bs4 import BeautifulSoup

from .base import BaseScraper


class EbayScraper(BaseScraper):
    def __init__(self, source_name: str = "eBay US", db=None):
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
            
            item_id = self._extract_item_id(product_url)
            if not item_id:
                return None
            
            name = self._extract_name(soup)
            if not name:
                return None
            
            price = self._extract_current_price(soup)
            if not price:
                return None
            
            original_price = self._extract_original_price(soup)
            
            category = self._extract_category(soup)
            image_url = self._extract_image(soup)
            is_in_stock = self._check_stock(soup)
            condition = self._extract_condition(soup)
            seller = self._extract_seller(soup)
            
            return {
                'name': name,
                'price': price,
                'original_price': original_price,
                'source_product_id': item_id,
                'source_product_url': product_url,
                'source_product_name': name,
                'category': category,
                'image_url': image_url,
                'is_in_stock': is_in_stock,
                'currency_code': 'USD',
                'raw_data': {
                    'item_id': item_id,
                    'condition': condition,
                    'seller': seller,
                    'url': product_url
                }
            }
            
        except Exception as e:
            self.log_scraping(
                status='error',
                error_message=str(e)
            )
            return None
    
    def _extract_item_id(self, url: str) -> Optional[str]:
        match = re.search(r'/itm/(?:[^/]+/)?(\d+)', url)
        if match:
            return match.group(1)
        
        match = re.search(r'item=(\d+)', url)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            'h1.x-item-title__mainTitle span',
            'h1#itemTitle',
            '.x-item-title__mainTitle',
            'h1[itemprop="name"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                text = re.sub(r'^Details about\s*', '', text)
                if text:
                    return text
        
        return None
    
    def _extract_current_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        selectors = [
            '.x-price-primary span',
            '#prcIsum',
            '#mm-saleDscPrc',
            'span[itemprop="price"]',
            '.x-bin-price__content span.ux-textspans'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price = self._extract_price(element.get_text())
                if price:
                    return price
        
        return None
    
    def _extract_original_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        selectors = [
            '.x-price-was span',
            '#orgPrc',
            '.vi-originalPrice'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price = self._extract_price(element.get_text())
                if price:
                    return price
        
        return None
    
    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        breadcrumbs = soup.select('nav.breadcrumbs a span')
        if breadcrumbs:
            categories = [b.get_text(strip=True) for b in breadcrumbs]
            if categories:
                return categories[-1]
        
        breadcrumbs = soup.select('li[itemprop="itemListElement"] a span')
        if breadcrumbs:
            categories = [b.get_text(strip=True) for b in breadcrumbs]
            if categories:
                return categories[-1]
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            'img#icImg',
            '.ux-image-carousel-item img',
            'img[itemprop="image"]',
            '.img-wrapper img'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                url = element.get('src') or element.get('data-src')
                if url:
                    url = re.sub(r'/s-l\d+\.', '/s-l1600.', url)
                    return url
        
        return None
    
    def _check_stock(self, soup: BeautifulSoup) -> bool:
        sold_out = soup.select_one('.vi-quantity-soldout, .msgTextAlign')
        if sold_out:
            text = sold_out.get_text(strip=True).lower()
            if 'sold' in text or 'ended' in text:
                return False
        
        quantity = soup.select_one('.x-quantity__availability span')
        if quantity:
            text = quantity.get_text(strip=True).lower()
            if 'available' in text:
                return True
        
        return True
    
    def _extract_condition(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            '.x-item-condition span.ux-textspans',
            '#vi-itm-cond',
            'span[itemprop="itemCondition"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_seller(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            '.x-sellercard-atf__info__about-seller a span',
            'a.seller-persona span'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def search_products(self, query: str, max_results: int = 20) -> list:
        search_url = f"{self.source.base_url}/sch/i.html?_nkw={query.replace(' ', '+')}"
        
        try:
            self.rate_limiter.wait_if_needed(self.source_name)
            response = self.http_client.get(search_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_links = []
            results = soup.select('.s-item__link')
            
            for link in results[:max_results]:
                href = link.get('href')
                if href and '/itm/' in href:
                    product_links.append(href)
            
            return product_links
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
