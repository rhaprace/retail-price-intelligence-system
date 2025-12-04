from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.db_models import PriceComparison
from ..dependencies import get_db

router = APIRouter()


class ComparisonNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Price comparison not found")


class ComparisonQueryBuilder:
    def __init__(self, db: Session):
        self.db = db
        self.query = db.query(PriceComparison)
    
    def filter_by_product(self, product_id: Optional[UUID]):
        if product_id:
            self.query = self.query.filter(PriceComparison.product_id == product_id)
        return self
    
    def filter_by_date_or_latest(self, comparison_date: Optional[date]):
        if comparison_date:
            self.query = self.query.filter(PriceComparison.comparison_date == comparison_date)
        else:
            latest_date = self.db.query(PriceComparison.comparison_date).order_by(
                desc(PriceComparison.comparison_date)
            ).first()
            if latest_date:
                self.query = self.query.filter(PriceComparison.comparison_date == latest_date[0])
        return self
    
    def execute(self, limit: int):
        return self.query.order_by(desc(PriceComparison.comparison_date)).limit(limit).all()
    
    def get_first(self):
        return self.query.order_by(desc(PriceComparison.comparison_date)).first()


class ComparisonFormatter:
    @staticmethod
    def to_dict(comparison: PriceComparison) -> dict:
        return {
            "id": comparison.id,
            "product_id": comparison.product_id,
            "product_name": comparison.product.name if comparison.product else None,
            "comparison_date": comparison.comparison_date,
            "best_price": ComparisonFormatter._to_float(comparison.best_price),
            "best_price_source_id": comparison.best_price_source_id,
            "min_price": ComparisonFormatter._to_float(comparison.min_price),
            "max_price": ComparisonFormatter._to_float(comparison.max_price),
            "price_variance": ComparisonFormatter._to_float(comparison.price_variance),
            "source_count": comparison.source_count
        }
    
    @staticmethod
    def _to_float(value) -> Optional[float]:
        return float(value) if value else None


@router.get("/")
def list_comparisons(
    product_id: Optional[UUID] = None,
    comparison_date: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    comparisons = (
        ComparisonQueryBuilder(db)
        .filter_by_product(product_id)
        .filter_by_date_or_latest(comparison_date)
        .execute(limit)
    )
    return [ComparisonFormatter.to_dict(c) for c in comparisons]


@router.get("/product/{product_id}")
def get_comparison_for_product(
    product_id: UUID,
    comparison_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    comparison = (
        ComparisonQueryBuilder(db)
        .filter_by_product(product_id)
        .filter_by_date_or_latest(comparison_date)
        .get_first()
    )
    
    if not comparison:
        raise ComparisonNotFoundError()
    
    return ComparisonFormatter.to_dict(comparison)

