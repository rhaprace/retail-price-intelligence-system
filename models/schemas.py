"""
Pydantic schemas for data validation and serialization.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class SourceCreate(BaseModel):
    """Schema for creating a source."""
    name: str = Field(..., max_length=100)
    base_url: str = Field(..., max_length=500)
    country_code: Optional[str] = None
    currency_code: str = 'USD'
    is_active: bool = True
    rate_limit_per_minute: int = 60


class Source(SourceCreate):
    """Schema for source response."""
    id: int
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    upc: Optional[str] = None
    ean: Optional[str] = None
    image_url: Optional[str] = None
    normalized_name: Optional[str] = None


class Product(ProductCreate):
    """Schema for product response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductSourceCreate(BaseModel):
    """Schema for creating a product source."""
    product_id: UUID
    source_id: int
    source_product_id: str
    source_product_url: str
    source_product_name: Optional[str] = None
    is_active: bool = True


class ProductSource(ProductSourceCreate):
    """Schema for product source response."""
    id: int
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PriceCreate(BaseModel):
    """Schema for creating a price."""
    product_source_id: int
    price: Decimal = Field(..., gt=0)
    currency_code: str = 'USD'
    original_price: Optional[Decimal] = None
    is_in_stock: bool = True
    stock_quantity: Optional[int] = None
    shipping_cost: Decimal = 0
    raw_data: Optional[Dict[str, Any]] = None
    scraped_at: Optional[datetime] = None


class Price(PriceCreate):
    """Schema for price response."""
    id: int
    discount_percentage: Optional[Decimal] = None
    scraped_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class PriceAlertCreate(BaseModel):
    """Schema for creating a price alert."""
    product_id: UUID
    user_email: Optional[str] = None
    target_price: Optional[Decimal] = None
    price_drop_percentage: Optional[Decimal] = None
    is_active: bool = True


class PriceAlert(PriceAlertCreate):
    """Schema for price alert response."""
    id: int
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DiscountAnalysisCreate(BaseModel):
    """Schema for creating discount analysis."""
    product_source_id: int
    analysis_date: date
    min_price_30d: Optional[Decimal] = None
    max_price_30d: Optional[Decimal] = None
    avg_price_30d: Optional[Decimal] = None
    min_price_60d: Optional[Decimal] = None
    max_price_60d: Optional[Decimal] = None
    avg_price_60d: Optional[Decimal] = None
    min_price_90d: Optional[Decimal] = None
    max_price_90d: Optional[Decimal] = None
    avg_price_90d: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    claimed_discount_percentage: Optional[Decimal] = None
    actual_discount_percentage: Optional[Decimal] = None
    is_fake_discount: bool = False
    fake_discount_reason: Optional[str] = None
    price_trend: Optional[str] = None


class DiscountAnalysis(DiscountAnalysisCreate):
    """Schema for discount analysis response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PriceComparisonCreate(BaseModel):
    """Schema for creating price comparison."""
    product_id: UUID
    comparison_date: date
    best_price: Optional[Decimal] = None
    best_price_source_id: Optional[int] = None
    best_price_product_source_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    price_variance: Optional[Decimal] = None
    source_count: Optional[int] = None


class PriceComparison(PriceComparisonCreate):
    """Schema for price comparison response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ScrapingLogCreate(BaseModel):
    """Schema for creating scraping log."""
    source_id: Optional[int] = None
    product_source_id: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    http_status_code: Optional[int] = None
    scraped_count: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None


class ScrapingLog(ScrapingLogCreate):
    """Schema for scraping log response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class LatestPrice(BaseModel):
    """Schema for latest price view."""
    product_id: UUID
    product_name: str
    source_name: str
    source_id: int
    product_source_id: int
    price: Decimal
    currency_code: str
    original_price: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    is_in_stock: bool
    scraped_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class PriceComparisonView(BaseModel):
    """Schema for price comparison view."""
    product_id: UUID
    product_name: str
    source_count: int
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    avg_price: Optional[Decimal] = None
    price_stddev: Optional[Decimal] = None
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True

