"""
Price comparison routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import SessionLocal, PriceComparison, Product

router = APIRouter()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_comparisons(
    product_id: Optional[UUID] = None,
    comparison_date: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get price comparisons."""
    query = db.query(PriceComparison)
    
    if product_id:
        query = query.filter(PriceComparison.product_id == product_id)
    if comparison_date:
        query = query.filter(PriceComparison.comparison_date == comparison_date)
    else:
        latest_date = db.query(PriceComparison.comparison_date).order_by(
            desc(PriceComparison.comparison_date)
        ).first()
        if latest_date:
            query = query.filter(PriceComparison.comparison_date == latest_date[0])
    
    comparisons = query.order_by(desc(PriceComparison.comparison_date)).limit(limit).all()
    
    return [{
        "id": c.id,
        "product_id": c.product_id,
        "product_name": c.product.name if c.product else None,
        "comparison_date": c.comparison_date,
        "best_price": float(c.best_price) if c.best_price else None,
        "best_price_source_id": c.best_price_source_id,
        "min_price": float(c.min_price) if c.min_price else None,
        "max_price": float(c.max_price) if c.max_price else None,
        "price_variance": float(c.price_variance) if c.price_variance else None,
        "source_count": c.source_count
    } for c in comparisons]


@router.get("/product/{product_id}")
def get_product_comparison(
    product_id: UUID,
    comparison_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get price comparison for a specific product."""
    query = db.query(PriceComparison).filter(PriceComparison.product_id == product_id)
    
    if comparison_date:
        query = query.filter(PriceComparison.comparison_date == comparison_date)
    else:
        query = query.order_by(desc(PriceComparison.comparison_date))
    
    comparison = query.first()
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Price comparison not found")
    
    return {
        "id": comparison.id,
        "product_id": comparison.product_id,
        "product_name": comparison.product.name if comparison.product else None,
        "comparison_date": comparison.comparison_date,
        "best_price": float(comparison.best_price) if comparison.best_price else None,
        "best_price_source_id": comparison.best_price_source_id,
        "min_price": float(comparison.min_price) if comparison.min_price else None,
        "max_price": float(comparison.max_price) if comparison.max_price else None,
        "price_variance": float(comparison.price_variance) if comparison.price_variance else None,
        "source_count": comparison.source_count
    }

