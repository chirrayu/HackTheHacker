import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.database.models import Event, Alert

logger = logging.getLogger("hackthehacker.detector.bruteforce")

class BruteForceDetector:
    """
    Detects brute-force authentication behavior based on high-frequency connection
    attempts and authentication error signals towards authentication services (SSH:22, FTP:21, Web:80/8180).
    """

    AUTH_PORTS = {21, 22, 23, 80, 443, 3306, 5432, 8180}

    def __init__(self, failure_threshold: int = 5, window_seconds: int = 120):
        self.failure_threshold = failure_threshold
        self.time_window = timedelta(seconds=window_seconds)

    def analyze(self, db: Session) -> List[Alert]:
        now = datetime.utcnow()
        window_start = now - self.time_window

        # Query events against auth ports or brute force tags
        events = db.query(Event).filter(
            Event.timestamp >= window_start,
            Event.destination_port.in_(self.AUTH_PORTS)
        ).all()

        # Group by (src, dst, port)
        grouped: Dict[tuple, List[Event]] = {}
        for ev in events:
            key = (ev.source_ip, ev.destination_ip, ev.destination_port)
            grouped.setdefault(key, []).append(ev)

        alerts_created = []

        for (src, dst, port), ev_list in grouped.items():
            if len(ev_list) >= self.failure_threshold:
                # Deduplicate recent alert
                recent = db.query(Alert).filter(
                    Alert.alert_type == "brute_force",
                    Alert.source_ip == src,
                    Alert.destination_ip == dst,
                    Alert.created_at >= window_start
                ).first()

                if not recent:
                    service_map = {21: "FTP", 22: "SSH", 23: "Telnet", 80: "HTTP", 3306: "MySQL"}
                    srv = service_map.get(port, f"Port {port}")

                    evidence = {
                        "targeted_service": srv,
                        "targeted_port": port,
                        "connection_attempts": len(ev_list),
                        "window_seconds": self.time_window.total_seconds(),
                        "method": "Authentication Port Repetition Threshold"
                    }

                    alert = Alert(
                        alert_type="brute_force",
                        title=f"Potential Brute-Force Attack on {srv} ({src} -> {dst}:{port})",
                        description=f"Host {src} initiated {len(ev_list)} connection attempts to {srv} on {dst} in {self.time_window.total_seconds():.0f}s.",
                        severity="High" if len(ev_list) >= 12 else "Moderate",
                        source_ip=src,
                        destination_ip=dst,
                        status="new",
                        confidence=0.88,
                        evidence=json.dumps(evidence),
                        created_at=datetime.utcnow()
                    )
                    db.add(alert)
                    alerts_created.append(alert)

        if alerts_created:
            db.commit()
            logger.info(f"BruteForceDetector generated {len(alerts_created)} alerts.")

        return alerts_created
