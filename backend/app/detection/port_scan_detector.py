import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Event, Alert

logger = logging.getLogger("hackthehacker.detector.portscan")

class PortScanDetector:
    """
    Detects horizontal and vertical port scanning activity by analyzing
    distinct destination ports accessed by a source IP within a sliding time window.
    """

    def __init__(self, port_threshold: int = 5, time_window_seconds: int = 120):
        self.port_threshold = port_threshold
        self.time_window = timedelta(seconds=time_window_seconds)

    def analyze(self, db: Session, target_ip: Optional[str] = None) -> List[Alert]:
        """Scans recent events for multi-port scanning patterns."""
        now = datetime.utcnow()
        window_start = now - self.time_window

        query = db.query(Event).filter(
            Event.timestamp >= window_start,
            Event.destination_port.isnot(None)
        )
        if target_ip:
            query = query.filter(Event.destination_ip == target_ip)

        events = query.all()

        # Group ports by (source_ip, destination_ip)
        pairs: Dict[tuple, set] = {}
        pair_events: Dict[tuple, List[Event]] = {}

        for ev in events:
            key = (ev.source_ip, ev.destination_ip)
            if key not in pairs:
                pairs[key] = set()
                pair_events[key] = []
            pairs[key].add(ev.destination_port)
            pair_events[key].append(ev)

        alerts_created = []

        for (src, dst), ports in pairs.items():
            if len(ports) >= self.port_threshold:
                # Check if alert already exists recently to avoid flood
                recent_alert = db.query(Alert).filter(
                    Alert.alert_type == "port_scan",
                    Alert.source_ip == src,
                    Alert.destination_ip == dst,
                    Alert.created_at >= window_start
                ).first()

                if not recent_alert:
                    sorted_ports = sorted(list(ports))
                    evidence = {
                        "distinct_ports_scanned": len(ports),
                        "ports_sample": sorted_ports[:15],
                        "first_event": pair_events[(src, dst)][0].timestamp.isoformat(),
                        "last_event": pair_events[(src, dst)][-1].timestamp.isoformat(),
                        "method": "Sliding Window Unique Destination Port Threshold"
                    }

                    sev = "High" if len(ports) > 20 else "Moderate"

                    alert = Alert(
                        alert_type="port_scan",
                        title=f"Port Scan Detected from {src}",
                        description=f"Host {src} probed {len(ports)} distinct ports on {dst} within {self.time_window.total_seconds():.0f}s.",
                        severity=sev,
                        source_ip=src,
                        destination_ip=dst,
                        status="new",
                        confidence=0.95,
                        evidence=json.dumps(evidence),
                        created_at=datetime.utcnow()
                    )
                    db.add(alert)
                    alerts_created.append(alert)

        if alerts_created:
            db.commit()
            logger.info(f"PortScanDetector generated {len(alerts_created)} alerts.")

        return alerts_created
