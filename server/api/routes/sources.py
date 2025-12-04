from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from models.db_models import Source
from models.schemas import Source as SourceSchema, SourceCreate
from ..dependencies import get_db

router = APIRouter()


class SourceNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Source not found")


class SourceAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Source with this name already exists")


def get_source_or_404(source_id: int, db: Session) -> Source:
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise SourceNotFoundError()
    return source


def ensure_source_name_unique(name: str, db: Session):
    existing = db.query(Source).filter(Source.name == name).first()
    if existing:
        raise SourceAlreadyExistsError()


@router.get("/", response_model=List[SourceSchema])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


@router.get("/{source_id}", response_model=SourceSchema)
def get_source(source_id: int, db: Session = Depends(get_db)):
    return get_source_or_404(source_id, db)


@router.post("/", response_model=SourceSchema)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    ensure_source_name_unique(source.name, db)
    
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

