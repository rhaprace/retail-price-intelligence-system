"""
Analytics routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.db_models import DiscountAnalysis, ProductSource
from ..dependencies import get_db

router = APIRouter()


@router.get("/discounts")
def get_discount_analysis(
    product_source_id: Optional[int] = None,
    is_fake: Optional[bool] = None,
    analysis_date: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get discount analysis results."""
    query = db.query(DiscountAnalysis)
    
    if product_source_id:
        query = query.filter(DiscountAnalysis.product_source_id == product_source_id)
    if is_fake is not None:
        query = query.filter(DiscountAnalysis.is_fake_discount == is_fake)
    if analysis_date:
        query = query.filter(DiscountAnalysis.analysis_date == analysis_date)
    else:
        latest_date = db.query(DiscountAnalysis.analysis_date).order_by(
            desc(DiscountAnalysis.analysis_date)
        ).first()
        if latest_date:
            query = query.filter(DiscountAnalysis.analysis_date == latest_date[0])
    
    analyses = query.order_by(desc(DiscountAnalysis.analysis_date)).limit(limit).all()
    
    return [{
        "id": a.id,
        "product_source_id": a.product_source_id,
        "product_name": a.product_source.source_product_name if a.product_source else None,
        "analysis_date": a.analysis_date,
        "current_price": float(a.current_price) if a.current_price else None,
        "min_price_30d": float(a.min_price_30d) if a.min_price_30d else None,
        "max_price_30d": float(a.max_price_30d) if a.max_price_30d else None,
        "avg_price_30d": float(a.avg_price_30d) if a.avg_price_30d else None,
        "min_price_90d": float(a.min_price_90d) if a.min_price_90d else None,
        "claimed_discount_percentage": float(a.claimed_discount_percentage) if a.claimed_discount_percentage else None,
        "actual_discount_percentage": float(a.actual_discount_percentage) if a.actual_discount_percentage else None,
        "is_fake_discount": a.is_fake_discount,
        "fake_discount_reason": a.fake_discount_reason,
        "price_trend": a.price_trend
    } for a in analyses]


@router.get("/discounts/fake")
def get_fake_discounts(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all fake discounts."""
    return get_discount_analysis(is_fake=True, limit=limit, db=db)


@router.get("/discounts/product-source/{product_source_id}")
def get_product_source_discount_analysis(
    product_source_id: int,
    analysis_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get discount analysis for a specific product-source."""
    query = db.query(DiscountAnalysis).filter(
        DiscountAnalysis.product_source_id == product_source_id
    )
    
    if analysis_date:
        query = query.filter(DiscountAnalysis.analysis_date == analysis_date)
    else:
        query = query.order_by(desc(DiscountAnalysis.analysis_date))
    
    analysis = query.first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Discount analysis not found")
    
    return {
        "id": analysis.id,
        "product_source_id": analysis.product_source_id,
        "product_name": analysis.product_source.source_product_name if analysis.product_source else None,
        "analysis_date": analysis.analysis_date,
        "current_price": float(analysis.current_price) if analysis.current_price else None,
        "min_price_30d": float(analysis.min_price_30d) if analysis.min_price_30d else None,
        "max_price_30d": float(analysis.max_price_30d) if analysis.max_price_30d else None,
        "avg_price_30d": float(analysis.avg_price_30d) if analysis.avg_price_30d else None,
        "min_price_60d": float(analysis.min_price_60d) if analysis.min_price_60d else None,
        "max_price_60d": float(analysis.max_price_60d) if analysis.max_price_60d else None,
        "avg_price_60d": float(analysis.avg_price_60d) if analysis.avg_price_60d else None,
        "min_price_90d": float(analysis.min_price_90d) if analysis.min_price_90d else None,
        "max_price_90d": float(analysis.max_price_90d) if analysis.max_price_90d else None,
        "avg_price_90d": float(analysis.avg_price_90d) if analysis.avg_price_90d else None,
        "claimed_discount_percentage": float(analysis.claimed_discount_percentage) if analysis.claimed_discount_percentage else None,
        "actual_discount_percentage": float(analysis.actual_discount_percentage) if analysis.actual_discount_percentage else None,
        "is_fake_discount": analysis.is_fake_discount,
        "fake_discount_reason": analysis.fake_discount_reason,
        "price_trend": analysis.price_trend
    }

