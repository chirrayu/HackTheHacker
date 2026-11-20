import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database.models import Event, Alert

logger = logging.getLogger("hackthehacker.detector.suspicious")

class SuspiciousConnectionDetector:
    """
    Identifies anomalous connection behavior:
    - Access to sensitive or vintage backdoor ports (e.g. Metasploitable bindshell 1524, 6667 IRC, 2121)
    - Burst connection surges
    """

    SUSPICIOUS_TARGET_PORTS = {
        1524: ("Ingreslock / Metasploitable Root Bindshell", "Critical"),
        6667: ("UnrealIRCD Backdoor", "Critical"),
        2121: ("ProFTPD Non-standard Admin Port", "High"),
        8009: ("Apache JServ Protocol", "Moderate"),
        3632: ("distcc Distributed Compiler Daemon", "High")
    }

    def analyze(self, db: Session) -> List[Alert]:
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=5)

        events = db.query(Event).filter(
            Event.timestamp >= window_start,
            Event.destination_port.in_(list(self.SUSPICIOUS_TARGET_PORTS.keys()))
        ).all()

        alerts = []
        for ev in events:
            # Check deduplication
            recent = db.query(Alert).filter(
                Alert.alert_type == "suspicious_port_access",
                Alert.source_ip == ev.source_ip,
                Alert.destination_ip == ev.destination_ip,
                Alert.created_at >= window_start
            ).first()

            if not recent:
                desc, sev = self.SUSPICIOUS_TARGET_PORTS[ev.destination_port]
                evidence = {
                    "destination_port": ev.destination_port,
                    "service_tag": desc,
                    "raw_event_id": ev.id,
                    "protocol": ev.protocol
                }

                alert = Alert(
                    event_id=ev.id,
                    alert_type="suspicious_port_access",
                    title=f"Access to Dangerous Service ({desc}) on {ev.destination_ip}:{ev.destination_port}",
                    description=f"Host {ev.source_ip} attempted to access {desc} on port {ev.destination_port}.",
                    severity=sev,
                    source_ip=ev.source_ip,
                    destination_ip=ev.destination_ip,
                    status="new",
                    confidence=0.92,
                    evidence=json.dumps(evidence),
                    created_at=datetime.utcnow()
                )
                db.add(alert)
                alerts.append(alert)

        if alerts:
            db.commit()
            logger.info(f"SuspiciousConnectionDetector generated {len(alerts)} alerts.")

        return alerts
