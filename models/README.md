# Models Package

This package contains SQLAlchemy ORM models and Pydantic schemas for the Retail Price Intelligence System.

## Structure

- **`base.py`**: SQLAlchemy base configuration and database connection utilities
- **`db_models.py`**: SQLAlchemy ORM models matching the database schema
- **`schemas.py`**: Pydantic schemas for data validation and API serialization
- **`__init__.py`**: Package exports

## Usage

### Database Connection

```python
from models import SessionLocal, get_db

db = SessionLocal()
try:
    pass
finally:
    db.close()

from fastapi import Depends
from models import get_db

@app.get("/products")
def get_products(db = Depends(get_db)):
    pass
```

### ORM Models

```python
from models import Product, Price, Source, SessionLocal

db = SessionLocal()

product = Product(
    name="iPhone 15 Pro",
    category="Electronics",
    brand="Apple"
)
db.add(product)
db.commit()

products = db.query(Product).filter(Product.category == "Electronics").all()

for product in products:
    for product_source in product.product_sources:
        latest_price = db.query(Price).filter(
            Price.product_source_id == product_source.id
        ).order_by(Price.scraped_at.desc()).first()
        print(f"{product.name}: ${latest_price.price}")
```

### Pydantic Schemas

```python
from models import ProductCreate, Product, PriceCreate
from models import SessionLocal

db = SessionLocal()

product_data = ProductCreate(
    name="iPhone 15 Pro",
    category="Electronics",
    brand="Apple"
)

product = Product(**product_data.dict())
db.add(product)
db.commit()

product_response = Product.from_orm(product)
print(product_response.json())
```

## Models Overview

### Core Models

1. **Source**: E-commerce websites
2. **Product**: Core product catalog
3. **ProductSource**: Links products to sources
4. **Price**: Time-series price data

### Analytics Models

5. **PriceAlert**: Price drop notifications
6. **DiscountAnalysis**: Fake discount detection
7. **PriceComparison**: Cross-source comparisons

### Operational Models

8. **ScrapingLog**: Scraping activity tracking

## Relationships

```
Source (1) ──< (many) ProductSource (many) ──> (1) Product
                                                      │
                                                      │
                                                      ▼
                                                Price (many)
                                                      │
                                                      │
                                                      ▼
                                        DiscountAnalysis (many)
```

## Environment Variables

The models use the following environment variables for database connection:

- `DB_HOST`: Database host (default: 'localhost')
- `DB_PORT`: Database port (default: '5432')
- `DB_NAME`: Database name (default: 'retail_price_intelligence')
- `DB_USER`: Database user (default: 'postgres')
- `DB_PASSWORD`: Database password (default: '')

## Installation

```bash
pip install -r requirements.txt
```

## Notes

- All models use timezone-aware timestamps
- UUIDs are used for Product IDs
- Decimal types are used for prices to avoid floating-point precision issues
- Relationships are configured with appropriate cascade behaviors
- Unique constraints are enforced at the database level

