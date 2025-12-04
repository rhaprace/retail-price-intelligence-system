from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from utils.http_client import HTTPClient
from utils.rate_limiter import RateLimiter
from models import SessionLocal
from models.db_models import Source, ScrapingLog
from models.utils import (
    find_or_create_product,
    get_or_create_product_source,
    insert_price
)


class BaseScraper(ABC):
    def __init__(self, source_name: str, db: Optional[Session] = None):
        self.source_name = source_name
        self.db = db or SessionLocal()
        self.http_client = HTTPClient()
        self.rate_limiter = None
        self.source = self._get_source()
        self._setup_rate_limiter()
    
    def _get_source(self) -> Source:
        source = self.db.query(Source).filter(Source.name == self.source_name).first()
        if not source:
            raise ValueError(f"Source '{self.source_name}' not found in database")
        return source
    
    def _setup_rate_limiter(self):
        self.rate_limiter = RateLimiter(self.source.rate_limit_per_minute)
    
    @abstractmethod
    def scrape_product(self, product_url: str) -> Optional[Dict[str, Any]]:
        pass
    
    def _extract_price(self, text: str) -> Optional[Decimal]:
        if not text:
            return None
        
        cleaned = text.replace('$', '').replace(',', '').replace('€', '').replace('£', '')
        
        import re
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            try:
                return Decimal(numbers[0])
            except:
                return None
        return None
    
    def save_product_data(self, product_data: Dict[str, Any]) -> bool:
        try:
            product = find_or_create_product(
                db=self.db,
                name=product_data['name'],
                category=product_data.get('category'),
                brand=product_data.get('brand'),
                sku=product_data.get('sku'),
                upc=product_data.get('upc'),
                ean=product_data.get('ean'),
                image_url=product_data.get('image_url')
            )
            
            product_source = get_or_create_product_source(
                db=self.db,
                product_id=str(product.id),
                source_id=self.source.id,
                source_product_id=product_data['source_product_id'],
                source_product_url=product_data['source_product_url'],
                source_product_name=product_data.get('source_product_name', product_data['name'])
            )
            
            insert_price(
                db=self.db,
                product_source_id=product_source.id,
                price=product_data['price'],
                currency_code=product_data.get('currency_code', self.source.currency_code),
                original_price=product_data.get('original_price'),
                is_in_stock=product_data.get('is_in_stock', True),
                stock_quantity=product_data.get('stock_quantity'),
                shipping_cost=product_data.get('shipping_cost', Decimal('0')),
                raw_data=product_data.get('raw_data')
            )
            
            return True
        except Exception as e:
            print(f"Error saving product data: {e}")
            return False
    
    def log_scraping(self, status: str, error_message: Optional[str] = None, 
                     response_time_ms: Optional[int] = None, 
                     http_status_code: Optional[int] = None,
                     scraped_count: int = 0):
        log = ScrapingLog(
            source_id=self.source.id,
            status=status,
            error_message=error_message,
            response_time_ms=response_time_ms,
            http_status_code=http_status_code,
            scraped_count=scraped_count,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )
        self.db.add(log)
        self.db.commit()
    
    def scrape(self, product_urls: list) -> Dict[str, Any]:
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        start_time = datetime.utcnow()
        
        for url in product_urls:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed(self.source_name)
            
            try:
                product_data = self.scrape_product(url)
                if product_data:
                    if self.save_product_data(product_data):
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to save: {url}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to scrape: {url}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error scraping {url}: {str(e)}")
        
        self.source.last_scraped_at = datetime.now(timezone.utc)
        self.db.commit()
        
        elapsed_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        self.log_scraping(
            status='success' if results['failed'] == 0 else 'error',
            scraped_count=results['success'],
            response_time_ms=elapsed_ms
        )
        
        return results
    
    def close(self):
        self.http_client.close()
        if self.db:
            self.db.close()

