from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta, timezone

from models.db_models import Product, ProductSource
from models.schemas import Product as ProductSchema, ProductCreate
from models.utils import find_or_create_product, get_price_history
from ..dependencies import get_db

router = APIRouter()


class ProductNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Product not found")


class ProductQueryBuilder:
    def __init__(self, db: Session):
        self.query = db.query(Product)
    
    def filter_by_category(self, category: Optional[str]):
        if category:
            self.query = self.query.filter(Product.category == category)
        return self
    
    def filter_by_brand(self, brand: Optional[str]):
        if brand:
            self.query = self.query.filter(Product.brand == brand)
        return self
    
    def filter_by_search(self, search: Optional[str]):
        if search:
            self.query = self.query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        return self
    
    def paginate(self, skip: int, limit: int):
        return self.query.offset(skip).limit(limit).all()


def get_product_or_404(product_id: UUID, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ProductNotFoundError()
    return product


@router.get("/", response_model=List[ProductSchema])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return (
        ProductQueryBuilder(db)
        .filter_by_category(category)
        .filter_by_brand(brand)
        .filter_by_search(search)
        .paginate(skip, limit)
    )


@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    return get_product_or_404(product_id, db)


@router.post("/", response_model=ProductSchema)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return find_or_create_product(
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


@router.get("/{product_id}/sources")
def get_product_sources(product_id: UUID, db: Session = Depends(get_db)):
    get_product_or_404(product_id, db)
    
    sources = db.query(ProductSource).filter(
        ProductSource.product_id == product_id,
        ProductSource.is_active == True
    ).all()
    
    return [
        {
            "id": s.id,
            "source_id": s.source_id,
            "source_product_id": s.source_product_id,
            "source_product_url": s.source_product_url,
            "source_product_name": s.source_product_name,
            "last_seen_at": s.last_seen_at
        }
        for s in sources
    ]


@router.get("/{product_id}/prices")
def get_product_price_history(
    product_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    get_product_or_404(product_id, db)
    
    product_sources = db.query(ProductSource).filter(
        ProductSource.product_id == product_id,
        ProductSource.is_active == True
    ).all()
    
    prices_data = []
    for ps in product_sources:
        prices = get_price_history(db, ps.id, days=days)
        prices_data.extend(_format_price_records(ps, prices))
    
    return sorted(prices_data, key=lambda x: x['scraped_at'], reverse=True)


def _format_price_records(product_source: ProductSource, prices: list) -> list:
    return [
        {
            "product_source_id": product_source.id,
            "source_id": product_source.source_id,
            "price": float(price.price),
            "original_price": float(price.original_price) if price.original_price else None,
            "discount_percentage": float(price.discount_percentage) if price.discount_percentage else None,
            "is_in_stock": price.is_in_stock,
            "scraped_at": price.scraped_at
        }
        for price in prices
    ]

