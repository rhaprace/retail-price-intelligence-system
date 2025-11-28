"""
Price routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import SessionLocal, Price, ProductSource
from models.schemas import Price as PriceSchema
from models.utils import get_latest_price, get_price_history

router = APIRouter()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/latest", response_model=List[PriceSchema])
def get_latest_prices(
    source_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get latest prices for all products."""
    from models.utils import get_latest_price
    
    query = db.query(ProductSource).filter(ProductSource.is_active == True)
    if source_id:
        query = query.filter(ProductSource.source_id == source_id)
    
    product_sources = query.all()
    
    latest_prices = []
    for ps in product_sources:
        price = get_latest_price(db, ps.id)
        if price:
            latest_prices.append(price)
    
    latest_prices.sort(key=lambda p: p.scraped_at, reverse=True)
    return latest_prices[:limit]


@router.get("/product-source/{product_source_id}", response_model=List[PriceSchema])
def get_prices_by_product_source(
    product_source_id: int,
    days: int = Query(30, ge=1, le=365),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get price history for a specific product-source."""
    prices = get_price_history(db, product_source_id, days=days, limit=limit)
    return prices


@router.get("/product-source/{product_source_id}/latest", response_model=PriceSchema)
def get_latest_price_by_product_source(
    product_source_id: int,
    db: Session = Depends(get_db)
):
    """Get latest price for a product-source."""
    price = get_latest_price(db, product_source_id)
    if not price:
        raise HTTPException(status_code=404, detail="No price data found")
    return price


@router.get("/product-source/{product_source_id}/metrics")
def get_price_metrics(
    product_source_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get price metrics (min, max, avg) for a product-source."""
    from models.utils import calculate_price_metrics
    
    metrics = calculate_price_metrics(db, product_source_id, days=days)
    
    return {
        "product_source_id": product_source_id,
        "period_days": days,
        "min_price": float(metrics['min_price']) if metrics['min_price'] else None,
        "max_price": float(metrics['max_price']) if metrics['max_price'] else None,
        "avg_price": float(metrics['avg_price']) if metrics['avg_price'] else None
    }

