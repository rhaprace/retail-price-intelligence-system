from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.db_models import PriceAlert, Product
from models.schemas import PriceAlert as PriceAlertSchema, PriceAlertCreate
from ..dependencies import get_db

router = APIRouter()


class AlertNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Alert not found")


class ProductNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Product not found")


class AlertQueryBuilder:
    def __init__(self, db: Session):
        self.query = db.query(PriceAlert)
    
    def filter_by_product(self, product_id: Optional[UUID]):
        if product_id:
            self.query = self.query.filter(PriceAlert.product_id == product_id)
        return self
    
    def filter_by_active_status(self, is_active: Optional[bool]):
        if is_active is not None:
            self.query = self.query.filter(PriceAlert.is_active == is_active)
        return self
    
    def execute(self):
        return self.query.all()


def get_alert_or_404(alert_id: int, db: Session) -> PriceAlert:
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise AlertNotFoundError()
    return alert


def ensure_product_exists(product_id: UUID, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ProductNotFoundError()


def set_alert_active_status(alert: PriceAlert, is_active: bool, db: Session) -> dict:
    alert.is_active = is_active
    db.commit()
    status_message = "activated" if is_active else "deactivated"
    return {"message": f"Alert {status_message}", "alert_id": alert.id}


@router.get("/", response_model=List[PriceAlertSchema])
def list_alerts(
    product_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return (
        AlertQueryBuilder(db)
        .filter_by_product(product_id)
        .filter_by_active_status(is_active)
        .execute()
    )


@router.get("/{alert_id}", response_model=PriceAlertSchema)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    return get_alert_or_404(alert_id, db)


@router.post("/", response_model=PriceAlertSchema)
def create_alert(alert: PriceAlertCreate, db: Session = Depends(get_db)):
    ensure_product_exists(alert.product_id, db)
    
    db_alert = PriceAlert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.patch("/{alert_id}/activate")
def activate_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = get_alert_or_404(alert_id, db)
    return set_alert_active_status(alert, is_active=True, db=db)


@router.patch("/{alert_id}/deactivate")
def deactivate_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = get_alert_or_404(alert_id, db)
    return set_alert_active_status(alert, is_active=False, db=db)


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = get_alert_or_404(alert_id, db)
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted", "alert_id": alert_id}

