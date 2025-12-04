from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from .db_models import (
    Product, ProductSource, Price, Source
)


PRODUCT_NAME_STOP_WORDS = frozenset(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'])


def normalize_product_name(name: str) -> str:
    normalized = name.lower().strip()
    words = [word for word in normalized.split() if word not in PRODUCT_NAME_STOP_WORDS]
    return ' '.join(words)


class ProductLookup:
    UNIQUE_IDENTIFIER_FIELDS = ('sku', 'upc', 'ean')
    
    @staticmethod
    def find_by_identifier(db: Session, sku: str = None, upc: str = None, ean: str = None) -> Optional[Product]:
        identifiers = {'sku': sku, 'upc': upc, 'ean': ean}
        for field, value in identifiers.items():
            if value:
                product = db.query(Product).filter(getattr(Product, field) == value).first()
                if product:
                    return product
        return None
    
    @staticmethod
    def find_by_normalized_name(db: Session, name: str) -> Optional[Product]:
        normalized = normalize_product_name(name)
        return db.query(Product).filter(
            func.lower(Product.normalized_name) == normalized
        ).first()


def find_or_create_product(
    db: Session,
    name: str,
    sku: Optional[str] = None,
    upc: Optional[str] = None,
    ean: Optional[str] = None,
    **kwargs
) -> Product:
    existing_product = ProductLookup.find_by_identifier(db, sku, upc, ean)
    if existing_product:
        return existing_product
    
    existing_product = ProductLookup.find_by_normalized_name(db, name)
    if existing_product:
        return existing_product
    
    product = Product(
        name=name,
        normalized_name=normalize_product_name(name),
        sku=sku,
        upc=upc,
        ean=ean,
        **kwargs
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_or_create_product_source(
    db: Session,
    product_id: str,
    source_id: int,
    source_product_id: str,
    source_product_url: str,
    source_product_name: Optional[str] = None
) -> ProductSource:
    product_source = db.query(ProductSource).filter(
        and_(
            ProductSource.source_id == source_id,
            ProductSource.source_product_id == source_product_id
        )
    ).first()
    
    if product_source:
        product_source.source_product_url = source_product_url
        if source_product_name:
            product_source.source_product_name = source_product_name
        product_source.last_seen_at = datetime.now(timezone.utc)
        product_source.is_active = True
        db.commit()
        db.refresh(product_source)
        return product_source
    
    product_source = ProductSource(
        product_id=product_id,
        source_id=source_id,
        source_product_id=source_product_id,
        source_product_url=source_product_url,
        source_product_name=source_product_name,
        last_seen_at=datetime.now(timezone.utc)
    )
    db.add(product_source)
    db.commit()
    db.refresh(product_source)
    return product_source


def insert_price(
    db: Session,
    product_source_id: int,
    price: Decimal,
    currency_code: str = 'USD',
    original_price: Optional[Decimal] = None,
    is_in_stock: bool = True,
    stock_quantity: Optional[int] = None,
    shipping_cost: Decimal = Decimal('0'),
    raw_data: Optional[Dict[str, Any]] = None,
    scraped_at: Optional[datetime] = None
) -> Price:
    price_record = Price(
        product_source_id=product_source_id,
        price=price,
        currency_code=currency_code,
        original_price=original_price,
        is_in_stock=is_in_stock,
        stock_quantity=stock_quantity,
        shipping_cost=shipping_cost,
        raw_data=raw_data,
        scraped_at=scraped_at or datetime.now(timezone.utc)
    )
    db.add(price_record)
    db.commit()
    db.refresh(price_record)
    return price_record


def get_latest_price(db: Session, product_source_id: int) -> Optional[Price]:
    return db.query(Price).filter(
        Price.product_source_id == product_source_id
    ).order_by(Price.scraped_at.desc()).first()


def get_price_history(
    db: Session,
    product_source_id: int,
    days: int = 30,
    limit: Optional[int] = None
) -> List[Price]:
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    query = db.query(Price).filter(
        and_(
            Price.product_source_id == product_source_id,
            Price.scraped_at >= cutoff_date
        )
    ).order_by(Price.scraped_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()


def calculate_price_metrics(
    db: Session,
    product_source_id: int,
    days: int = 30
) -> Dict[str, Optional[Decimal]]:
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    result = db.query(
        func.min(Price.price).label('min_price'),
        func.max(Price.price).label('max_price'),
        func.avg(Price.price).label('avg_price')
    ).filter(
        and_(
            Price.product_source_id == product_source_id,
            Price.scraped_at >= cutoff_date
        )
    ).first()
    
    return {
        'min_price': result.min_price,
        'max_price': result.max_price,
        'avg_price': result.avg_price
    }


def get_source_by_name(db: Session, name: str) -> Optional[Source]:
    return db.query(Source).filter(Source.name == name).first()


def get_active_sources(db: Session) -> List[Source]:
    return db.query(Source).filter(Source.is_active == True).all()

