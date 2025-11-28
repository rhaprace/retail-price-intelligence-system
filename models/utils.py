"""
Utility functions for database operations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from .db_models import (
    Product, ProductSource, Price, Source,
    DiscountAnalysis, PriceComparison, PriceAlert
)


def normalize_product_name(name: str) -> str:
    """
    Normalize product name for fuzzy matching.
    
    Args:
        name: Product name
    
    Returns:
        Normalized name
    """
    normalized = name.lower().strip()
    stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
    words = normalized.split()
    words = [w for w in words if w not in stop_words]
    return ' '.join(words)


def find_or_create_product(
    db: Session,
    name: str,
    sku: Optional[str] = None,
    upc: Optional[str] = None,
    ean: Optional[str] = None,
    **kwargs
) -> Product:
    """Find existing product or create new one."""
    for field, value in [('sku', sku), ('upc', upc), ('ean', ean)]:
        if value:
            product = db.query(Product).filter(getattr(Product, field) == value).first()
            if product:
                return product
    
    normalized = normalize_product_name(name)
    product = db.query(Product).filter(
        func.lower(Product.normalized_name) == normalized
    ).first()
    
    if product:
        return product
    
    product = Product(
        name=name,
        normalized_name=normalized,
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
    """
    Get or create a product source link.
    
    Args:
        db: Database session
        product_id: Product UUID
        source_id: Source ID
        source_product_id: Product ID on the source website
        source_product_url: Product URL on source
        source_product_name: Product name on source
    
    Returns:
        ProductSource instance
    """
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
        product_source.last_seen_at = datetime.utcnow()
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
        last_seen_at=datetime.utcnow()
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
    """
    Insert a new price record.
    
    Args:
        db: Database session
        product_source_id: Product source ID
        price: Current price
        currency_code: Currency code
        original_price: Original/regular price
        is_in_stock: Stock availability
        stock_quantity: Stock quantity
        shipping_cost: Shipping cost
        raw_data: Raw scraped data
        scraped_at: Scraping timestamp
    
    Returns:
        Price instance
    """
    price_record = Price(
        product_source_id=product_source_id,
        price=price,
        currency_code=currency_code,
        original_price=original_price,
        is_in_stock=is_in_stock,
        stock_quantity=stock_quantity,
        shipping_cost=shipping_cost,
        raw_data=raw_data,
        scraped_at=scraped_at or datetime.utcnow()
    )
    db.add(price_record)
    db.commit()
    db.refresh(price_record)
    return price_record


def get_latest_price(db: Session, product_source_id: int) -> Optional[Price]:
    """
    Get the latest price for a product source.
    
    Args:
        db: Database session
        product_source_id: Product source ID
    
    Returns:
        Latest Price instance or None
    """
    return db.query(Price).filter(
        Price.product_source_id == product_source_id
    ).order_by(Price.scraped_at.desc()).first()


def get_price_history(
    db: Session,
    product_source_id: int,
    days: int = 30,
    limit: Optional[int] = None
) -> List[Price]:
    """
    Get price history for a product source.
    
    Args:
        db: Database session
        product_source_id: Product source ID
        days: Number of days to look back
        limit: Maximum number of records to return
    
    Returns:
        List of Price instances
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
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
    """
    Calculate price metrics (min, max, avg) for a time period.
    
    Args:
        db: Database session
        product_source_id: Product source ID
        days: Number of days to analyze
    
    Returns:
        Dictionary with min_price, max_price, avg_price
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
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
    """
    Get source by name.
    
    Args:
        db: Database session
        name: Source name
    
    Returns:
        Source instance or None
    """
    return db.query(Source).filter(Source.name == name).first()


def get_active_sources(db: Session) -> List[Source]:
    """
    Get all active sources.
    
    Args:
        db: Database session
    
    Returns:
        List of active Source instances
    """
    return db.query(Source).filter(Source.is_active == True).all()

