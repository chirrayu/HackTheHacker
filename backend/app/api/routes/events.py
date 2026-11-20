from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Event
from app.schemas.models import EventResponse

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("", response_model=List[EventResponse])
def get_events(
    source_ip: Optional[str] = Query(None, description="Filter by source IP"),
    destination_ip: Optional[str] = Query(None, description="Filter by destination IP"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve filtered, paginated security telemetry events."""
    query = db.query(Event)

    if source_ip:
        query = query.filter(Event.source_ip == source_ip)
    if destination_ip:
        query = query.filter(Event.destination_ip == destination_ip)
    if severity:
        query = query.filter(Event.severity == severity)
    if event_type:
        query = query.filter(Event.event_type == event_type)

    events = query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
    return events
