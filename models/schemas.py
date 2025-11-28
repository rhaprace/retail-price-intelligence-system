"""
Pydantic schemas for data validation and serialization.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

class SourceBase(BaseModel):
    """Base source schema."""
    name: str = Field(..., max_length=100)
    base_url: str = Field(..., max_length=500)
    country_code: Optional[str] = Field(None, max_length=2)
    currency_code: str = Field('USD', max_length=3)
    is_active: bool = True
    rate_limit_per_minute: int = Field(60, ge=1)


class SourceCreate(SourceBase):
    """Schema for creating a source."""
    pass


class SourceUpdate(BaseModel):
    """Schema for updating a source."""
    name: Optional[str] = Field(None, max_length=100)
    base_url: Optional[str] = Field(None, max_length=500)
    country_code: Optional[str] = Field(None, max_length=2)
    currency_code: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1)


class Source(SourceBase):
    """Schema for source response."""
    id: int
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    """Base product schema."""
    name: str = Field(..., max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    upc: Optional[str] = Field(None, max_length=50)
    ean: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=1000)
    normalized_name: Optional[str] = Field(None, max_length=500)


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    upc: Optional[str] = Field(None, max_length=50)
    ean: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=1000)
    normalized_name: Optional[str] = Field(None, max_length=500)


class Product(ProductBase):
    """Schema for product response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductSourceBase(BaseModel):
    """Base product source schema."""
    product_id: UUID
    source_id: int
    source_product_id: str = Field(..., max_length=200)
    source_product_url: str = Field(..., max_length=1000)
    source_product_name: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class ProductSourceCreate(ProductSourceBase):
    """Schema for creating a product source."""
    pass


class ProductSourceUpdate(BaseModel):
    """Schema for updating a product source."""
    source_product_url: Optional[str] = Field(None, max_length=1000)
    source_product_name: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    last_seen_at: Optional[datetime] = None


class ProductSource(ProductSourceBase):
    """Schema for product source response."""
    id: int
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PriceBase(BaseModel):
    """Base price schema."""
    product_source_id: int
    price: Decimal = Field(..., gt=0)
    currency_code: str = Field('USD', max_length=3)
    original_price: Optional[Decimal] = None
    is_in_stock: bool = True
    stock_quantity: Optional[int] = None
    shipping_cost: Decimal = Field(0, ge=0)
    raw_data: Optional[Dict[str, Any]] = None


class PriceCreate(PriceBase):
    """Schema for creating a price."""
    scraped_at: Optional[datetime] = None


class Price(PriceBase):
    """Schema for price response."""
    id: int
    discount_percentage: Optional[Decimal] = None
    scraped_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class PriceAlertBase(BaseModel):
    """Base price alert schema."""
    product_id: UUID
    user_email: Optional[str] = Field(None, max_length=255)
    target_price: Optional[Decimal] = None
    price_drop_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: bool = True


class PriceAlertCreate(PriceAlertBase):
    """Schema for creating a price alert."""
    pass


class PriceAlertUpdate(BaseModel):
    """Schema for updating a price alert."""
    target_price: Optional[Decimal] = None
    price_drop_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class PriceAlert(PriceAlertBase):
    """Schema for price alert response."""
    id: int
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DiscountAnalysisBase(BaseModel):
    """Base discount analysis schema."""
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
    price_trend: Optional[str] = Field(None, max_length=20)


class DiscountAnalysisCreate(DiscountAnalysisBase):
    """Schema for creating discount analysis."""
    pass


class DiscountAnalysis(DiscountAnalysisBase):
    """Schema for discount analysis response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PriceComparisonBase(BaseModel):
    """Base price comparison schema."""
    product_id: UUID
    comparison_date: date
    best_price: Optional[Decimal] = None
    best_price_source_id: Optional[int] = None
    best_price_product_source_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    price_variance: Optional[Decimal] = None
    source_count: Optional[int] = None


class PriceComparisonCreate(PriceComparisonBase):
    """Schema for creating price comparison."""
    pass


class PriceComparison(PriceComparisonBase):
    """Schema for price comparison response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ScrapingLogBase(BaseModel):
    """Base scraping log schema."""
    source_id: Optional[int] = None
    product_source_id: Optional[int] = None
    status: str = Field(..., max_length=20)
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    http_status_code: Optional[int] = None
    scraped_count: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None


class ScrapingLogCreate(ScrapingLogBase):
    """Schema for creating scraping log."""
    pass


class ScrapingLog(ScrapingLogBase):
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

