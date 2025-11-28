"""
Product routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from models.db_models import Product, ProductSource, Price
from models.schemas import Product as ProductSchema, ProductCreate
from models.utils import find_or_create_product
from ..dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[ProductSchema])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of products."""
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Get product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductSchema)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    db_product = find_or_create_product(
        db=db,
        name=product.name,
        description=product.description,
        category=product.category,
        brand=product.brand,
        sku=product.sku,
        upc=product.upc,
        ean=product.ean,
        image_url=product.image_url
    )
    return db_product


@router.get("/{product_id}/sources")
def get_product_sources(product_id: UUID, db: Session = Depends(get_db)):
    """Get all sources for a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    sources = db.query(ProductSource).filter(
        ProductSource.product_id == product_id,
        ProductSource.is_active == True
    ).all()
    
    return [{
        "id": s.id,
        "source_id": s.source_id,
        "source_product_id": s.source_product_id,
        "source_product_url": s.source_product_url,
        "source_product_name": s.source_product_name,
        "last_seen_at": s.last_seen_at
    } for s in sources]


@router.get("/{product_id}/prices")
def get_product_prices(
    product_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get price history for a product across all sources."""
    from datetime import datetime, timedelta, timezone
    from models.utils import get_price_history
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_sources = db.query(ProductSource).filter(
        ProductSource.product_id == product_id,
        ProductSource.is_active == True
    ).all()
    
    prices_data = []
    for ps in product_sources:
        prices = get_price_history(db, ps.id, days=days)
        for price in prices:
            prices_data.append({
                "product_source_id": ps.id,
                "source_id": ps.source_id,
                "price": float(price.price),
                "original_price": float(price.original_price) if price.original_price else None,
                "discount_percentage": float(price.discount_percentage) if price.discount_percentage else None,
                "is_in_stock": price.is_in_stock,
                "scraped_at": price.scraped_at
            })
    
    return sorted(prices_data, key=lambda x: x['scraped_at'], reverse=True)

