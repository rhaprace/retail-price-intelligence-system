"""
Source routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from models.db_models import Source
from models.schemas import Source as SourceSchema, SourceCreate
from ..dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[SourceSchema])
def get_sources(db: Session = Depends(get_db)):
    """Get all sources."""
    sources = db.query(Source).all()
    return sources


@router.get("/{source_id}", response_model=SourceSchema)
def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get source by ID."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.post("/", response_model=SourceSchema)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """Create a new source."""
    # Check if source already exists
    existing = db.query(Source).filter(Source.name == source.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

