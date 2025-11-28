## Usage

### Creating a Custom Scraper

```python
from scrapers.base import BaseScraper
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

class MySiteScraper(BaseScraper):
    def scrape_product(self, product_url: str) -> Optional[Dict[str, Any]]:
        """Implement your scraping logic here."""
        response = self.http_client.get(product_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        name = soup.select_one('h1').get_text()
        price = self._extract_price(soup.select_one('.price').get_text())
        
        return {
            'name': name,
            'price': price,
            'source_product_id': 'extract-from-url-or-page',
            'source_product_url': product_url,
            'source_product_name': name,
            'is_in_stock': True
        }
```

### Running a Scraper

```python
from scrapers import ExampleScraper

scraper = ExampleScraper('Amazon US')

product_data = scraper.scrape_product('https://example.com/product/123')

urls = [
    'https://example.com/product/1',
    'https://example.com/product/2',
]
results = scraper.scrape(urls)
print(f"Success: {results['success']}, Failed: {results['failed']}")

scraper.close()
```

## Features

- **Rate Limiting**: Automatic rate limiting based on source settings
- **Retry Logic**: Built-in retry for failed requests
- **Database Integration**: Automatic saving to database
- **Error Handling**: Comprehensive error logging
- **Price Extraction**: Helper method for extracting prices from text

## Base Scraper Methods

- `scrape_product(url)`: Abstract method - implement for your site
- `save_product_data(data)`: Save scraped data to database
- `_extract_price(text)`: Extract price from text string
- `log_scraping(...)`: Log scraping activity
- `scrape(urls)`: Scrape multiple products

## Requirements

1. Source must exist in database (create via models or SQL)
2. Implement `scrape_product()` method
3. Return dictionary with required fields:
   - `name`: Product name
   - `price`: Current price (Decimal)
   - `source_product_id`: Product ID on source site
   - `source_product_url`: Product URL
   - Optional: `original_price`, `category`, `brand`, `sku`, etc.

