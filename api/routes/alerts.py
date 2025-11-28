"""
Price alert routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.db_models import PriceAlert, Product
from models.schemas import PriceAlert as PriceAlertSchema, PriceAlertCreate
from ..dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[PriceAlertSchema])
def get_alerts(
    product_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get price alerts."""
    query = db.query(PriceAlert)
    
    if product_id:
        query = query.filter(PriceAlert.product_id == product_id)
    if is_active is not None:
        query = query.filter(PriceAlert.is_active == is_active)
    
    alerts = query.all()
    return alerts


@router.get("/{alert_id}", response_model=PriceAlertSchema)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get alert by ID."""
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/", response_model=PriceAlertSchema)
def create_alert(alert: PriceAlertCreate, db: Session = Depends(get_db)):
    """Create a new price alert."""
    product = db.query(Product).filter(Product.id == alert.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_alert = PriceAlert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.patch("/{alert_id}/activate")
def activate_alert(alert_id: int, db: Session = Depends(get_db)):
    """Activate an alert."""
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = True
    db.commit()
    return {"message": "Alert activated", "alert_id": alert_id}


@router.patch("/{alert_id}/deactivate")
def deactivate_alert(alert_id: int, db: Session = Depends(get_db)):
    """Deactivate an alert."""
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    db.commit()
    return {"message": "Alert deactivated", "alert_id": alert_id}


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert."""
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted", "alert_id": alert_id}

