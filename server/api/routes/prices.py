from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from models.db_models import ProductSource
from models.schemas import Price as PriceSchema
from models.utils import get_latest_price, get_price_history, calculate_price_metrics
from ..dependencies import get_db

router = APIRouter()


class PriceNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="No price data found")


def collect_latest_prices_for_sources(db: Session, source_id: Optional[int], limit: int) -> List:
    query = db.query(ProductSource).filter(ProductSource.is_active == True)
    if source_id:
        query = query.filter(ProductSource.source_id == source_id)
    
    product_sources = query.all()
    
    latest_prices = [
        price for ps in product_sources
        if (price := get_latest_price(db, ps.id)) is not None
    ]
    
    latest_prices.sort(key=lambda p: p.scraped_at, reverse=True)
    return latest_prices[:limit]


def format_price_metrics(product_source_id: int, period_days: int, metrics: dict) -> dict:
    return {
        "product_source_id": product_source_id,
        "period_days": period_days,
        "min_price": float(metrics['min_price']) if metrics['min_price'] else None,
        "max_price": float(metrics['max_price']) if metrics['max_price'] else None,
        "avg_price": float(metrics['avg_price']) if metrics['avg_price'] else None
    }


@router.get("/latest", response_model=List[PriceSchema])
def list_latest_prices(
    source_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return collect_latest_prices_for_sources(db, source_id, limit)


@router.get("/product-source/{product_source_id}", response_model=List[PriceSchema])
def list_prices_for_product_source(
    product_source_id: int,
    days: int = Query(30, ge=1, le=365),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return get_price_history(db, product_source_id, days=days, limit=limit)


@router.get("/product-source/{product_source_id}/latest", response_model=PriceSchema)
def get_latest_price_for_product_source(
    product_source_id: int,
    db: Session = Depends(get_db)
):
    price = get_latest_price(db, product_source_id)
    if not price:
        raise PriceNotFoundError()
    return price


@router.get("/product-source/{product_source_id}/metrics")
def get_price_metrics_for_product_source(
    product_source_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    metrics = calculate_price_metrics(db, product_source_id, days=days)
    return format_price_metrics(product_source_id, days, metrics)

