import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database.models import Event, Alert, AttackSession

logger = logging.getLogger("hackthehacker.correlation")

class EventCorrelationEngine:
    """
    Correlates disparate events and alerts into cohesive Attack Sessions
    based on Source-Destination IP pairs, temporal proximity (sliding session timeout),
    and common signature vectors.
    """

    SESSION_TIMEOUT_MINUTES = 30

    @classmethod
    def correlate_sessions(cls, db: Session) -> List[AttackSession]:
        """Correlates unassigned events into attack sessions."""
        unassigned_events = db.query(Event).filter(
            Event.related_attack_id.is_(None)
        ).order_by(Event.timestamp.asc()).all()

        if not unassigned_events:
            return []

        sessions_updated = []

        for ev in unassigned_events:
            # Find an active attack session for this (src, dst) pair within timeout
            session = db.query(AttackSession).filter(
                AttackSession.source_ip == ev.source_ip,
                AttackSession.destination_ip == ev.destination_ip,
                AttackSession.status == "active",
                AttackSession.last_seen >= (ev.timestamp - timedelta(minutes=cls.SESSION_TIMEOUT_MINUTES))
            ).first()

            if session:
                # Append to existing session
                ev.related_attack_id = session.id
                session.event_count += 1
                session.last_seen = max(session.last_seen, ev.timestamp)

                # Update categories
                categories = json.loads(session.detection_categories or "[]")
                if ev.event_type not in categories:
                    categories.append(ev.event_type)
                    session.detection_categories = json.dumps(categories)

                # Update severity if higher
                sev_order = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}
                if sev_order.get(ev.severity, 1) > sev_order.get(session.highest_severity, 1):
                    session.highest_severity = ev.severity

                sessions_updated.append(session)
            else:
                # Create a new AttackSession
                new_session = AttackSession(
                    source_ip=ev.source_ip,
                    destination_ip=ev.destination_ip,
                    first_seen=ev.timestamp,
                    last_seen=ev.timestamp,
                    event_count=1,
                    detection_categories=json.dumps([ev.event_type]),
                    highest_severity=ev.severity,
                    threat_score=20.0 if ev.severity == "Low" else (50.0 if ev.severity == "Moderate" else 75.0),
                    status="active",
                    summary=f"Attack session from {ev.source_ip} targeting {ev.destination_ip}"
                )
                db.add(new_session)
                db.flush()  # Generate new_session.id
                ev.related_attack_id = new_session.id
                sessions_updated.append(new_session)

        # Correlate alerts to sessions as well
        unassigned_alerts = db.query(Alert).filter(Alert.related_attack_id.is_(None)).all()
        for al in unassigned_alerts:
            match_session = db.query(AttackSession).filter(
                AttackSession.source_ip == al.source_ip,
                AttackSession.destination_ip == al.destination_ip
            ).order_by(AttackSession.last_seen.desc()).first()

            if match_session:
                al.related_attack_id = match_session.id

        db.commit()
        logger.info(f"Event correlation finished. Processed {len(unassigned_events)} events.")
        return sessions_updated
