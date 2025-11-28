"""
Helper script to add sources to database.
"""
from models import SessionLocal
from models.db_models import Source


def add_source(name: str, base_url: str, country_code: str = None, 
               currency_code: str = 'USD', rate_limit: int = 60):
    """Add a new source to the database."""
    db = SessionLocal()
    try:
        existing = db.query(Source).filter(Source.name == name).first()
        if existing:
            print(f"Source '{name}' already exists (ID: {existing.id})")
            return existing
        
        source = Source(
            name=name,
            base_url=base_url,
            country_code=country_code,
            currency_code=currency_code,
            rate_limit_per_minute=rate_limit
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        print(f"Created source '{name}' with ID: {source.id}")
        return source
    finally:
        db.close()


if __name__ == '__main__':
    sources = [
        {'name': 'Amazon US', 'base_url': 'https://www.amazon.com', 'country_code': 'US'},
        {'name': 'eBay US', 'base_url': 'https://www.ebay.com', 'country_code': 'US'},
        {'name': 'Walmart', 'base_url': 'https://www.walmart.com', 'country_code': 'US'},
    ]
    
    for source_data in sources:
        add_source(**source_data)

