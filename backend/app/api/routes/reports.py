import json
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models import Report, Event, Alert, AttackSession
from app.schemas.models import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=List[ReportResponse])
def list_reports(limit: int = 20, db: Session = Depends(get_db)):
    """List historical threat reports."""
    reports = db.query(Report).order_by(Report.generated_at.desc()).limit(limit).all()
    res = []
    for r in reports:
        sev_dist = json.loads(r.severity_distribution or "{}")
        findings = json.loads(r.key_findings or "[]")
        res.append(ReportResponse(
            id=r.id,
            title=r.title,
            time_period_start=r.time_period_start,
            time_period_end=r.time_period_end,
            total_events=r.total_events,
            total_alerts=r.total_alerts,
            attack_session_count=r.attack_session_count,
            severity_distribution=sev_dist,
            key_findings=findings,
            generated_at=r.generated_at
        ))
    return res

@router.post("/generate", response_model=ReportResponse)
def generate_report(payload: ReportCreate, db: Session = Depends(get_db)):
    """Generates an executive SOC intelligence report over the specified timeframe."""
    now = datetime.utcnow()
    start_time = now - timedelta(hours=payload.time_period_hours)

    total_events = db.query(Event).filter(Event.timestamp >= start_time).count()
    total_alerts = db.query(Alert).filter(Alert.created_at >= start_time).count()
    session_count = db.query(AttackSession).filter(AttackSession.last_seen >= start_time).count()

    # Severity distribution
    sev_counts = db.query(Event.severity, func.count(Event.id)).filter(
        Event.timestamp >= start_time
    ).group_by(Event.severity).all()
    sev_dist = {s: c for s, c in sev_counts}

    # Findings synthesis
    findings = [
        f"Total of {total_events} events ingested across {payload.time_period_hours} hour observation window.",
        f"{total_alerts} security alerts triggered requiring analyst review.",
        f"{session_count} correlated attack sessions identified across the lab network."
    ]

    crit_count = db.query(Alert).filter(Alert.created_at >= start_time, Alert.severity == "Critical").count()
    if crit_count > 0:
        findings.append(f"CRITICAL: {crit_count} high-priority threats detected involving unauthorized service access.")
    else:
        findings.append("No critical severity events observed during this observation window.")

    report = Report(
        title=payload.title,
        time_period_start=start_time,
        time_period_end=now,
        total_events=total_events,
        total_alerts=total_alerts,
        attack_session_count=session_count,
        severity_distribution=json.dumps(sev_dist),
        key_findings=json.dumps(findings),
        generated_at=now
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse(
        id=report.id,
        title=report.title,
        time_period_start=report.time_period_start,
        time_period_end=report.time_period_end,
        total_events=report.total_events,
        total_alerts=report.total_alerts,
        attack_session_count=report.attack_session_count,
        severity_distribution=sev_dist,
        key_findings=findings,
        generated_at=report.generated_at
    )
