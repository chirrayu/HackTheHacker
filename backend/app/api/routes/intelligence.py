import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import SourceIP, ThreatScore
from app.intelligence.threat_scoring import ThreatScoringEngine
from app.schemas.models import TopSourceIP, ThreatScoreResponse

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])

@router.get("/top-sources", response_model=List[TopSourceIP])
def get_top_sources(limit: int = 10, db: Session = Depends(get_db)):
    """List most active and high-risk source IP nodes."""
    rows = db.query(SourceIP).order_by(SourceIP.threat_score.desc(), SourceIP.total_events.desc()).limit(limit).all()
    return [
        TopSourceIP(
            ip_address=r.ip_address,
            event_count=r.total_events,
            threat_score=r.threat_score,
            risk_level=r.risk_level,
            last_seen=r.last_seen
        ) for r in rows
    ]

@router.get("/score/{source_ip}", response_model=ThreatScoreResponse)
def get_threat_score(source_ip: str, db: Session = Depends(get_db)):
    """Calculate and return an explainable threat risk score (0-100) for a given IP."""
    score_record = ThreatScoringEngine.calculate_score(db, source_ip)
    reasons = json.loads(score_record.reasons) if score_record.reasons else []

    return ThreatScoreResponse(
        source_ip=score_record.source_ip,
        score=score_record.score,
        severity_component=score_record.severity_component,
        frequency_component=score_record.frequency_component,
        behavioral_component=score_record.behavioral_component,
        recurrence_component=score_record.recurrence_component,
        reasons=reasons,
        calculated_at=score_record.calculated_at
    )
