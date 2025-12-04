import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from models import SessionLocal
from models.db_models import Source, Product, ProductSource, Price, PriceAlert


def seed_sources(db: Session) -> list:
    sources_data = [
        {
            "name": "Amazon US",
            "base_url": "https://www.amazon.com",
            "country_code": "US",
            "currency_code": "USD",
            "rate_limit_per_minute": 60
        },
        {
            "name": "eBay US",
            "base_url": "https://www.ebay.com",
            "country_code": "US",
            "currency_code": "USD",
            "rate_limit_per_minute": 60
        },
        {
            "name": "Walmart",
            "base_url": "https://www.walmart.com",
            "country_code": "US",
            "currency_code": "USD",
            "rate_limit_per_minute": 30
        },
        {
            "name": "Best Buy",
            "base_url": "https://www.bestbuy.com",
            "country_code": "US",
            "currency_code": "USD",
            "rate_limit_per_minute": 30
        },
        {
            "name": "Target",
            "base_url": "https://www.target.com",
            "country_code": "US",
            "currency_code": "USD",
            "rate_limit_per_minute": 30
        }
    ]
    
    sources = []
    for data in sources_data:
        existing = db.query(Source).filter(Source.name == data["name"]).first()
        if not existing:
            source = Source(**data)
            db.add(source)
            sources.append(source)
        else:
            sources.append(existing)
    
    db.commit()
    for s in sources:
        db.refresh(s)
    
    return sources


def seed_products(db: Session) -> list:
    products_data = [
        {
            "name": "Apple iPhone 15 Pro Max 256GB",
            "category": "Electronics",
            "brand": "Apple",
            "sku": "IPHONE15PM256",
            "description": "Latest iPhone with A17 Pro chip"
        },
        {
            "name": "Samsung Galaxy S24 Ultra 512GB",
            "category": "Electronics",
            "brand": "Samsung",
            "sku": "SGS24U512",
            "description": "Premium Android smartphone"
        },
        {
            "name": "Sony WH-1000XM5 Wireless Headphones",
            "category": "Electronics",
            "brand": "Sony",
            "sku": "SONYWH1000XM5",
            "description": "Industry-leading noise canceling headphones"
        },
        {
            "name": "Apple MacBook Pro 14-inch M3 Pro",
            "category": "Electronics",
            "brand": "Apple",
            "sku": "MBP14M3PRO",
            "description": "Professional laptop with M3 Pro chip"
        },
        {
            "name": "Dell XPS 15 Laptop",
            "category": "Electronics",
            "brand": "Dell",
            "sku": "DELLXPS15",
            "description": "Premium Windows laptop"
        },
        {
            "name": "Ninja Foodi Air Fryer",
            "category": "Home & Kitchen",
            "brand": "Ninja",
            "sku": "NINJAAF101",
            "description": "4-quart air fryer"
        },
        {
            "name": "Instant Pot Duo 7-in-1",
            "category": "Home & Kitchen",
            "brand": "Instant Pot",
            "sku": "IPDUOV2",
            "description": "Electric pressure cooker"
        },
        {
            "name": "Dyson V15 Detect Vacuum",
            "category": "Home & Kitchen",
            "brand": "Dyson",
            "sku": "DYSONV15",
            "description": "Cordless vacuum with laser"
        },
        {
            "name": "PlayStation 5 Console",
            "category": "Gaming",
            "brand": "Sony",
            "sku": "PS5CONSOLE",
            "description": "Next-gen gaming console"
        },
        {
            "name": "Xbox Series X",
            "category": "Gaming",
            "brand": "Microsoft",
            "sku": "XBOXSERIESX",
            "description": "Most powerful Xbox ever"
        },
        {
            "name": "Nintendo Switch OLED",
            "category": "Gaming",
            "brand": "Nintendo",
            "sku": "NSWITCHOLED",
            "description": "Hybrid gaming console"
        },
        # Fashion
        {
            "name": "Nike Air Max 270",
            "category": "Fashion",
            "brand": "Nike",
            "sku": "NIKEAM270",
            "description": "Lifestyle running shoes"
        },
        {
            "name": "Levi's 501 Original Jeans",
            "category": "Fashion",
            "brand": "Levi's",
            "sku": "LEVIS501",
            "description": "Classic straight leg jeans"
        },
        # Sports
        {
            "name": "Fitbit Charge 6",
            "category": "Sports",
            "brand": "Fitbit",
            "sku": "FITBITC6",
            "description": "Advanced fitness tracker"
        },
        {
            "name": "YETI Rambler 26oz Bottle",
            "category": "Sports",
            "brand": "YETI",
            "sku": "YETIR26",
            "description": "Insulated water bottle"
        }
    ]
    
    products = []
    for data in products_data:
        existing = db.query(Product).filter(Product.sku == data["sku"]).first()
        if not existing:
            product = Product(id=uuid4(), **data)
            db.add(product)
            products.append(product)
        else:
            products.append(existing)
    
    db.commit()
    for p in products:
        db.refresh(p)
    
    return products


def seed_product_sources(db: Session, products: list, sources: list) -> list:
    product_sources = []
    
    for product in products:
        num_sources = random.randint(2, min(4, len(sources)))
        selected_sources = random.sample(sources, num_sources)
        
        for source in selected_sources:
            existing = db.query(ProductSource).filter(
                ProductSource.product_id == product.id,
                ProductSource.source_id == source.id
            ).first()
            
            if not existing:
                ps = ProductSource(
                    product_id=product.id,
                    source_id=source.id,
                    source_product_id=f"{source.name[:3].upper()}-{product.sku}",
                    source_product_url=f"{source.base_url}/product/{product.sku}",
                    source_product_name=product.name,
                    last_seen_at=datetime.now(timezone.utc)
                )
                db.add(ps)
                product_sources.append(ps)
            else:
                product_sources.append(existing)
    
    db.commit()
    for ps in product_sources:
        db.refresh(ps)
    
    return product_sources


def seed_prices(db: Session, product_sources: list, days: int = 30) -> list:
    prices = []
    category_prices = {
        "Electronics": (200, 2000),
        "Home & Kitchen": (50, 500),
        "Gaming": (300, 600),
        "Fashion": (30, 200),
        "Sports": (25, 150)
    }
    
    for ps in product_sources:
        product = db.query(Product).filter(Product.id == ps.product_id).first()
        category = product.category if product else "Electronics"
        
        price_range = category_prices.get(category, (50, 500))
        base_price = random.uniform(price_range[0], price_range[1])
        
        for day in range(days):
            date = datetime.now(timezone.utc) - timedelta(days=day)
            
            variation = random.uniform(-0.1, 0.1)
            daily_price = base_price * (1 + variation)
            
            if random.random() < 0.2:
                original_price = Decimal(str(round(daily_price * 1.2, 2)))
                sale_price = Decimal(str(round(daily_price, 2)))
            else:
                original_price = None
                sale_price = Decimal(str(round(daily_price, 2)))
            
            price = Price(
                product_source_id=ps.id,
                price=sale_price,
                original_price=original_price,
                currency_code="USD",
                is_in_stock=random.random() > 0.05,
                scraped_at=date
            )
            db.add(price)
            prices.append(price)
    
    db.commit()
    return prices


def seed_alerts(db: Session, products: list) -> list:
    alerts = []
    for product in random.sample(products, min(5, len(products))):
        latest_price = db.query(Price).join(ProductSource).filter(
            ProductSource.product_id == product.id
        ).order_by(Price.scraped_at.desc()).first()
        
        if latest_price:
            target = float(latest_price.price) * 0.8
            
            alert = PriceAlert(
                product_id=product.id,
                user_email="demo@example.com",
                target_price=Decimal(str(round(target, 2))),
                is_active=True
            )
            db.add(alert)
            alerts.append(alert)
    
    db.commit()
    return alerts


def seed_database(days: int = 30):
    print("=" * 60)
    print("Seeding Database with Sample Data")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        print("\n📦 Creating sources...")
        sources = seed_sources(db)
        print(f"   Created {len(sources)} sources")
        
        print("\n📦 Creating products...")
        products = seed_products(db)
        print(f"   Created {len(products)} products")
        
        print("\n🔗 Linking products to sources...")
        product_sources = seed_product_sources(db, products, sources)
        print(f"   Created {len(product_sources)} product-source links")
        
        print(f"\n💰 Generating {days} days of price history...")
        prices = seed_prices(db, product_sources, days)
        print(f"   Created {len(prices)} price records")
        
        print("\n🔔 Creating sample alerts...")
        alerts = seed_alerts(db, products)
        print(f"   Created {len(alerts)} alerts")
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed!")
        print("=" * 60)
        
        print("\nSummary:")
        print(f"  - Sources: {len(sources)}")
        print(f"  - Products: {len(products)}")
        print(f"  - Product Sources: {len(product_sources)}")
        print(f"  - Price Records: {len(prices)}")
        print(f"  - Alerts: {len(alerts)}")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    days = 30
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"Invalid days argument: {sys.argv[1]}")
            sys.exit(1)
    
    seed_database(days)
