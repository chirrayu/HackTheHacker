from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models import Event, Alert, Asset, SourceIP
from app.schemas.models import AnalyticsOverview, TimelinePoint, TopSourceIP

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(db: Session = Depends(get_db)):
    """Summary metrics for the SOC Dashboard Overview page."""
    total_events = db.query(Event).count()
    active_alerts = db.query(Alert).filter(Alert.status.in_(["new", "investigating"])).count()
    critical_threats = db.query(Alert).filter(Alert.severity == "Critical").count()
    monitored_assets = db.query(Asset).count()

    # Severity Breakdown
    sev_counts = db.query(Event.severity, func.count(Event.id)).group_by(Event.severity).all()
    sev_map = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
    for s, c in sev_counts:
        if s in sev_map:
            sev_map[s] = c

    # Top Sources
    top_src_rows = db.query(SourceIP).order_by(SourceIP.total_events.desc()).limit(5).all()
    top_sources = [
        TopSourceIP(
            ip_address=s.ip_address,
            event_count=s.total_events,
            threat_score=s.threat_score,
            risk_level=s.risk_level,
            last_seen=s.last_seen
        ) for s in top_src_rows
    ]

    # Timeline (last 12 points, hourly or segmented)
    now = datetime.utcnow()
    timeline: List[TimelinePoint] = []
    for i in range(6, -1, -1):
        window_start = now - timedelta(hours=i+1)
        window_end = now - timedelta(hours=i)
        ev_count = db.query(Event).filter(Event.timestamp >= window_start, Event.timestamp < window_end).count()
        al_count = db.query(Alert).filter(Alert.created_at >= window_start, Alert.created_at < window_end).count()
        timeline.append(TimelinePoint(
            timestamp=window_end.strftime("%H:%M"),
            events=ev_count,
            alerts=al_count
        ))

    return AnalyticsOverview(
        total_events=total_events,
        active_alerts=active_alerts,
        critical_threats=critical_threats,
        monitored_assets=monitored_assets,
        severity_breakdown=sev_map,
        top_sources=top_sources,
        recent_activity_timeline=timeline
    )

@router.get("/timeline", response_model=List[TimelinePoint])
def get_timeline(hours: int = 12, db: Session = Depends(get_db)):
    """Timeline trend data for events and alerts."""
    now = datetime.utcnow()
    points = []
    for h in range(hours, -1, -1):
        w_start = now - timedelta(hours=h+1)
        w_end = now - timedelta(hours=h)
        ev_cnt = db.query(Event).filter(Event.timestamp >= w_start, Event.timestamp < w_end).count()
        al_cnt = db.query(Alert).filter(Alert.created_at >= w_start, Alert.created_at < w_end).count()
        points.append(TimelinePoint(
            timestamp=w_end.strftime("%m-%d %H:%M"),
            events=ev_cnt,
            alerts=al_cnt
        ))
    return points
