from dataclasses import dataclass
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.db_models import DiscountAnalysis
from ..dependencies import get_db

router = APIRouter()


class DiscountAnalysisNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Discount analysis not found")


class DiscountAnalysisQueryBuilder:
    def __init__(self, db: Session):
        self.db = db
        self.query = db.query(DiscountAnalysis)
    
    def filter_by_product_source(self, product_source_id: Optional[int]):
        if product_source_id:
            self.query = self.query.filter(DiscountAnalysis.product_source_id == product_source_id)
        return self
    
    def filter_by_fake_status(self, is_fake: Optional[bool]):
        if is_fake is not None:
            self.query = self.query.filter(DiscountAnalysis.is_fake_discount == is_fake)
        return self
    
    def filter_by_date_or_latest(self, analysis_date: Optional[date]):
        if analysis_date:
            self.query = self.query.filter(DiscountAnalysis.analysis_date == analysis_date)
        else:
            latest_date = self.db.query(DiscountAnalysis.analysis_date).order_by(
                desc(DiscountAnalysis.analysis_date)
            ).first()
            if latest_date:
                self.query = self.query.filter(DiscountAnalysis.analysis_date == latest_date[0])
        return self
    
    def execute(self, limit: int):
        return self.query.order_by(desc(DiscountAnalysis.analysis_date)).limit(limit).all()
    
    def get_first(self):
        return self.query.order_by(desc(DiscountAnalysis.analysis_date)).first()


class DiscountAnalysisFormatter:
    @staticmethod
    def to_summary_dict(analysis: DiscountAnalysis) -> dict:
        return {
            "id": analysis.id,
            "product_source_id": analysis.product_source_id,
            "product_name": analysis.product_source.source_product_name if analysis.product_source else None,
            "analysis_date": analysis.analysis_date,
            "current_price": DiscountAnalysisFormatter._to_float(analysis.current_price),
            "min_price_30d": DiscountAnalysisFormatter._to_float(analysis.min_price_30d),
            "max_price_30d": DiscountAnalysisFormatter._to_float(analysis.max_price_30d),
            "avg_price_30d": DiscountAnalysisFormatter._to_float(analysis.avg_price_30d),
            "min_price_90d": DiscountAnalysisFormatter._to_float(analysis.min_price_90d),
            "claimed_discount_percentage": DiscountAnalysisFormatter._to_float(analysis.claimed_discount_percentage),
            "actual_discount_percentage": DiscountAnalysisFormatter._to_float(analysis.actual_discount_percentage),
            "is_fake_discount": analysis.is_fake_discount,
            "fake_discount_reason": analysis.fake_discount_reason,
            "price_trend": analysis.price_trend
        }
    
    @staticmethod
    def to_detailed_dict(analysis: DiscountAnalysis) -> dict:
        return {
            "id": analysis.id,
            "product_source_id": analysis.product_source_id,
            "product_name": analysis.product_source.source_product_name if analysis.product_source else None,
            "analysis_date": analysis.analysis_date,
            "current_price": DiscountAnalysisFormatter._to_float(analysis.current_price),
            "min_price_30d": DiscountAnalysisFormatter._to_float(analysis.min_price_30d),
            "max_price_30d": DiscountAnalysisFormatter._to_float(analysis.max_price_30d),
            "avg_price_30d": DiscountAnalysisFormatter._to_float(analysis.avg_price_30d),
            "min_price_60d": DiscountAnalysisFormatter._to_float(analysis.min_price_60d),
            "max_price_60d": DiscountAnalysisFormatter._to_float(analysis.max_price_60d),
            "avg_price_60d": DiscountAnalysisFormatter._to_float(analysis.avg_price_60d),
            "min_price_90d": DiscountAnalysisFormatter._to_float(analysis.min_price_90d),
            "max_price_90d": DiscountAnalysisFormatter._to_float(analysis.max_price_90d),
            "avg_price_90d": DiscountAnalysisFormatter._to_float(analysis.avg_price_90d),
            "claimed_discount_percentage": DiscountAnalysisFormatter._to_float(analysis.claimed_discount_percentage),
            "actual_discount_percentage": DiscountAnalysisFormatter._to_float(analysis.actual_discount_percentage),
            "is_fake_discount": analysis.is_fake_discount,
            "fake_discount_reason": analysis.fake_discount_reason,
            "price_trend": analysis.price_trend
        }
    
    @staticmethod
    def _to_float(value) -> Optional[float]:
        return float(value) if value else None


@router.get("/discounts")
def list_discount_analyses(
    product_source_id: Optional[int] = None,
    is_fake: Optional[bool] = None,
    analysis_date: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    analyses = (
        DiscountAnalysisQueryBuilder(db)
        .filter_by_product_source(product_source_id)
        .filter_by_fake_status(is_fake)
        .filter_by_date_or_latest(analysis_date)
        .execute(limit)
    )
    return [DiscountAnalysisFormatter.to_summary_dict(a) for a in analyses]


@router.get("/discounts/fake")
def list_fake_discounts(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return list_discount_analyses(is_fake=True, limit=limit, db=db)


@router.get("/discounts/product-source/{product_source_id}")
def get_discount_analysis_for_product_source(
    product_source_id: int,
    analysis_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    analysis = (
        DiscountAnalysisQueryBuilder(db)
        .filter_by_product_source(product_source_id)
        .filter_by_date_or_latest(analysis_date)
        .get_first()
    )
    
    if not analysis:
        raise DiscountAnalysisNotFoundError()
    
    return DiscountAnalysisFormatter.to_detailed_dict(analysis)

