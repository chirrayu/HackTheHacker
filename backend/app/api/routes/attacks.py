import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import AttackSession, Event, Alert
from app.schemas.models import AttackSessionResponse, EventResponse, AlertResponse

router = APIRouter(prefix="/attacks", tags=["Attacks"])

@router.get("", response_model=List[AttackSessionResponse])
def get_attack_sessions(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve correlated multi-event attack sessions."""
    query = db.query(AttackSession)
    if status:
        query = query.filter(AttackSession.status == status)

    sessions = query.order_by(AttackSession.last_seen.desc()).limit(limit).all()

    # Format detection_categories from JSON string to list
    res = []
    for s in sessions:
        cats = json.loads(s.detection_categories or "[]")
        res.append(AttackSessionResponse(
            id=s.id,
            source_ip=s.source_ip,
            destination_ip=s.destination_ip,
            first_seen=s.first_seen,
            last_seen=s.last_seen,
            event_count=s.event_count,
            detection_categories=cats,
            highest_severity=s.highest_severity,
            threat_score=s.threat_score,
            status=s.status,
            summary=s.summary
        ))
    return res

@router.get("/{session_id}/timeline")
def get_attack_timeline(session_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed event timeline and associated alerts for an attack session."""
    session = db.query(AttackSession).filter(AttackSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Attack session not found")

    events = db.query(Event).filter(Event.related_attack_id == session_id).order_by(Event.timestamp.asc()).all()
    alerts = db.query(Alert).filter(Alert.related_attack_id == session_id).order_by(Alert.created_at.asc()).all()

    return {
        "session": {
            "id": session.id,
            "source_ip": session.source_ip,
            "destination_ip": session.destination_ip,
            "first_seen": session.first_seen,
            "last_seen": session.last_seen,
            "threat_score": session.threat_score,
            "highest_severity": session.highest_severity
        },
        "event_timeline": [
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "protocol": e.protocol,
                "port": e.destination_port,
                "signature": e.signature,
                "severity": e.severity
            } for e in events
        ],
        "correlated_alerts": [
            {
                "id": a.id,
                "title": a.title,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "created_at": a.created_at
            } for a in alerts
        ]
    }
