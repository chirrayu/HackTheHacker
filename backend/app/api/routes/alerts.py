from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Alert
from app.schemas.models import AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: Low, Moderate, High, Critical"),
    status: Optional[str] = Query(None, description="Filter by status: new, acknowledged, resolved"),
    source_ip: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve security alerts detected by rule and anomaly engines."""
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    if source_ip:
        query = query.filter(Alert.source_ip == source_ip)

    alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
    return alerts

@router.patch("/{alert_id}/status")
def update_alert_status(alert_id: str, new_status: str, db: Session = Depends(get_db)):
    """Update alert triage status."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = new_status
    db.commit()
    return {"status": "success", "alert_id": alert_id, "new_status": new_status}
