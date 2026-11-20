import pytest
from datetime import datetime, timedelta
from app.database.connection import SessionLocal, init_db
from app.database.models import Event, Alert
from app.detection.port_scan_detector import PortScanDetector
from app.detection.brute_force_detector import BruteForceDetector
from app.detection.suspicious_connection_detector import SuspiciousConnectionDetector

def test_port_scan_detector():
    init_db()
    db = SessionLocal()
    src = "192.168.56.20"
    dst = "192.168.56.30"
    now = datetime.utcnow()

    # Simulate multi-port scanning (ports 21, 22, 23, 25, 80, 445)
    events = []
    for port in [21, 22, 23, 25, 80, 445]:
        ev = Event(
            timestamp=now,
            source_ip=src,
            destination_ip=dst,
            destination_port=port,
            protocol="TCP",
            event_type="tcp_syn_probe",
            severity="Low",
            sensor="test"
        )
        db.add(ev)
        events.append(ev)
    db.commit()

    detector = PortScanDetector(port_threshold=5, time_window_seconds=120)
    alerts = detector.analyze(db, target_ip=dst)
    
    assert len(alerts) >= 1
    assert alerts[0].alert_type == "port_scan"
    assert alerts[0].source_ip == src
    assert alerts[0].destination_ip == dst

    # Cleanup
    for ev in events:
        db.delete(ev)
    for al in alerts:
        db.delete(al)
    db.commit()
    db.close()

def test_suspicious_port_access():
    init_db()
    db = SessionLocal()
    src = "192.168.56.20"
    dst = "192.168.56.30"

    # Port 1524 is the Metasploitable root bindshell backdoor
    ev = Event(
        timestamp=datetime.utcnow(),
        source_ip=src,
        destination_ip=dst,
        destination_port=1524,
        protocol="TCP",
        event_type="suspicious_connection",
        severity="Critical",
        sensor="test"
    )
    db.add(ev)
    db.commit()

    detector = SuspiciousConnectionDetector()
    alerts = detector.analyze(db)

    assert len(alerts) >= 1
    assert alerts[0].alert_type == "suspicious_port_access"
    assert alerts[0].severity == "Critical"

    # Cleanup
    db.delete(ev)
    for al in alerts:
        db.delete(al)
    db.commit()
    db.close()
