import pytest
from app.database.connection import SessionLocal, init_db
from app.database.models import Event, Alert
from app.intelligence.threat_scoring import ThreatScoringEngine
from datetime import datetime

def test_threat_scoring_formula():
    init_db()
    db = SessionLocal()
    test_ip = "192.168.56.99"

    # Inject test alerts and events
    alert = Alert(
        alert_type="port_scan",
        title="Test Port Scan",
        severity="High",
        source_ip=test_ip,
        destination_ip="192.168.56.30",
        created_at=datetime.utcnow()
    )
    db.add(alert)
    db.commit()

    score_record = ThreatScoringEngine.calculate_score(db, test_ip)
    assert score_record.score >= 0.0
    assert score_record.score <= 100.0
    assert len(score_record.reasons) > 0

    # Cleanup
    db.delete(alert)
    db.delete(score_record)
    db.commit()
    db.close()
