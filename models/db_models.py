"""
SQLAlchemy ORM models for Retail Price Intelligence System.
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, Text, 
    DateTime, ForeignKey, UniqueConstraint, CheckConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .base import Base


class Source(Base):
    """E-commerce website source."""
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    base_url = Column(String(500), nullable=False)
    country_code = Column(String(2))
    currency_code = Column(String(3), default='USD')
    is_active = Column(Boolean, default=True)
    rate_limit_per_minute = Column(Integer, default=60)
    last_scraped_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    product_sources = relationship('ProductSource', back_populates='source', cascade='all, delete-orphan')
    scraping_logs = relationship('ScrapingLog', back_populates='source')
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}')>"


class Product(Base):
    """Core product catalog."""
    __tablename__ = 'products'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    brand = Column(String(100))
    sku = Column(String(100))
    upc = Column(String(50))
    ean = Column(String(50))
    image_url = Column(String(1000))
    normalized_name = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    product_sources = relationship('ProductSource', back_populates='product', cascade='all, delete-orphan')
    price_alerts = relationship('PriceAlert', back_populates='product', cascade='all, delete-orphan')
    price_comparisons = relationship('PriceComparison', back_populates='product', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name[:50]}...')>"


class ProductSource(Base):
    """Links products to sources with source-specific identifiers."""
    __tablename__ = 'product_sources'
    __table_args__ = (
        UniqueConstraint('source_id', 'source_product_id', name='uq_source_product'),
    )
    
    id = Column(Integer, primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='CASCADE'), nullable=False)
    source_product_id = Column(String(200), nullable=False)
    source_product_url = Column(String(1000), nullable=False)
    source_product_name = Column(String(500))
    is_active = Column(Boolean, default=True)
    last_seen_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    product = relationship('Product', back_populates='product_sources')
    source = relationship('Source', back_populates='product_sources')
    prices = relationship('Price', back_populates='product_source', cascade='all, delete-orphan')
    discount_analyses = relationship('DiscountAnalysis', back_populates='product_source', cascade='all, delete-orphan')
    scraping_logs = relationship('ScrapingLog', back_populates='product_source')
    
    def __repr__(self):
        return f"<ProductSource(id={self.id}, product_id={self.product_id}, source_id={self.source_id})>"


class Price(Base):
    """Time-series price data."""
    __tablename__ = 'prices'
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_source_id = Column(Integer, ForeignKey('product_sources.id', ondelete='CASCADE'), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    original_price = Column(Numeric(10, 2))
    discount_percentage = Column(Numeric(5, 2))
    is_in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer)
    shipping_cost = Column(Numeric(10, 2), default=0)
    scraped_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    raw_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product_source = relationship('ProductSource', back_populates='prices')
    
    def __repr__(self):
        return f"<Price(id={self.id}, price={self.price}, scraped_at={self.scraped_at})>"


class PriceAlert(Base):
    """Price drop alerts and notifications."""
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_email = Column(String(255))
    target_price = Column(Numeric(10, 2))
    price_drop_percentage = Column(Numeric(5, 2))
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True))
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    product = relationship('Product', back_populates='price_alerts')
    
    def __repr__(self):
        return f"<PriceAlert(id={self.id}, product_id={self.product_id}, is_active={self.is_active})>"


class DiscountAnalysis(Base):
    """Fake discount detection and analysis."""
    __tablename__ = 'discount_analysis'
    __table_args__ = (
        UniqueConstraint('product_source_id', 'analysis_date', name='uq_discount_analysis'),
    )
    
    id = Column(Integer, primary_key=True)
    product_source_id = Column(Integer, ForeignKey('product_sources.id', ondelete='CASCADE'), nullable=False)
    analysis_date = Column(DateTime, nullable=False)
    min_price_30d = Column(Numeric(10, 2))
    max_price_30d = Column(Numeric(10, 2))
    avg_price_30d = Column(Numeric(10, 2))
    min_price_60d = Column(Numeric(10, 2))
    max_price_60d = Column(Numeric(10, 2))
    avg_price_60d = Column(Numeric(10, 2))
    min_price_90d = Column(Numeric(10, 2))
    max_price_90d = Column(Numeric(10, 2))
    avg_price_90d = Column(Numeric(10, 2))
    current_price = Column(Numeric(10, 2))
    claimed_discount_percentage = Column(Numeric(5, 2))
    actual_discount_percentage = Column(Numeric(5, 2))
    is_fake_discount = Column(Boolean, default=False)
    fake_discount_reason = Column(Text)
    price_trend = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product_source = relationship('ProductSource', back_populates='discount_analyses')
    
    def __repr__(self):
        return f"<DiscountAnalysis(id={self.id}, is_fake_discount={self.is_fake_discount})>"


class PriceComparison(Base):
    """Cross-source price comparisons."""
    __tablename__ = 'price_comparisons'
    __table_args__ = (
        UniqueConstraint('product_id', 'comparison_date', name='uq_price_comparison'),
    )
    
    id = Column(Integer, primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    comparison_date = Column(DateTime, nullable=False)
    best_price = Column(Numeric(10, 2))
    best_price_source_id = Column(Integer, ForeignKey('sources.id'))
    best_price_product_source_id = Column(Integer, ForeignKey('product_sources.id'))
    min_price = Column(Numeric(10, 2))
    max_price = Column(Numeric(10, 2))
    price_variance = Column(Numeric(10, 2))
    source_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship('Product', back_populates='price_comparisons')
    best_price_source = relationship('Source', foreign_keys=[best_price_source_id])
    best_price_product_source = relationship('ProductSource', foreign_keys=[best_price_product_source_id])
    
    def __repr__(self):
        return f"<PriceComparison(id={self.id}, product_id={self.product_id}, best_price={self.best_price})>"


class ScrapingLog(Base):
    """Scraping activity logs."""
    __tablename__ = 'scraping_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='SET NULL'))
    product_source_id = Column(Integer, ForeignKey('product_sources.id', ondelete='SET NULL'))
    status = Column(String(20), nullable=False)
    error_message = Column(Text)
    response_time_ms = Column(Integer)
    http_status_code = Column(Integer)
    scraped_count = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    source = relationship('Source', back_populates='scraping_logs')
    product_source = relationship('ProductSource', back_populates='scraping_logs')
    
    def __repr__(self):
        return f"<ScrapingLog(id={self.id}, status='{self.status}', source_id={self.source_id})>"

