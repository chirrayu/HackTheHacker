import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.database.models import Event, Alert, ThreatScore, SourceIP

logger = logging.getLogger("hackthehacker.threat_scoring")

class ThreatScoringEngine:
    """
    Computes explainable risk scores (0 to 100) per source IP using the formula:
    Risk Score = (0.30 × Severity) + (0.25 × Frequency) + (0.25 × Behavioral) + (0.20 × Recurrence)
    """

    W_SEVERITY = 0.30
    W_FREQUENCY = 0.25
    W_BEHAVIORAL = 0.25
    W_RECURRENCE = 0.20

    @classmethod
    def calculate_score(cls, db: Session, source_ip: str, window_hours: int = 24) -> ThreatScore:
        since = datetime.utcnow() - timedelta(hours=window_hours)
        events = db.query(Event).filter(Event.source_ip == source_ip, Event.timestamp >= since).all()
        alerts = db.query(Alert).filter(Alert.source_ip == source_ip, Alert.created_at >= since).all()

        reasons: List[str] = []

        # 1. Severity Component (0 to 100)
        sev_score = 0.0
        if alerts:
            max_alert_sev = "Low"
            for a in alerts:
                if a.severity == "Critical":
                    max_alert_sev = "Critical"
                    break
                elif a.severity == "High":
                    max_alert_sev = "High"
                elif a.severity == "Moderate" and max_alert_sev != "High":
                    max_alert_sev = "Moderate"

            if max_alert_sev == "Critical":
                sev_score = 100.0
                reasons.append("Critical severity security alert triggered.")
            elif max_alert_sev == "High":
                sev_score = 75.0
                reasons.append("High severity detection alerts present.")
            elif max_alert_sev == "Moderate":
                sev_score = 45.0
                reasons.append("Moderate severity alerts observed.")
            else:
                sev_score = 20.0
        elif events:
            sev_score = 15.0

        # 2. Frequency Component (0 to 100)
        # Scaled: 1-10 events (20), 11-50 events (50), 51-200 (80), >200 (100)
        n_events = len(events)
        freq_score = 0.0
        if n_events > 200:
            freq_score = 100.0
            reasons.append(f"Very high event volume ({n_events} events in window).")
        elif n_events > 50:
            freq_score = 75.0
            reasons.append(f"High traffic frequency ({n_events} events).")
        elif n_events > 15:
            freq_score = 45.0
            reasons.append(f"Moderate connection frequency ({n_events} events).")
        elif n_events > 0:
            freq_score = 20.0
        else:
            freq_score = 0.0

        # 3. Behavioral Indicators (0 to 100)
        # Unique ports accessed & variety of alert categories
        unique_ports = {ev.destination_port for ev in events if ev.destination_port}
        alert_types = {a.alert_type for a in alerts}
        behavior_score = 0.0

        if len(unique_ports) >= 15:
            behavior_score += 50.0
            reasons.append(f"Probed multiple distinct destination ports ({len(unique_ports)} ports).")
        elif len(unique_ports) >= 5:
            behavior_score += 30.0
            reasons.append(f"Accessed several destination ports ({len(unique_ports)} ports).")

        if "port_scan" in alert_types:
            behavior_score += 25.0
            reasons.append("Evidence matches active reconnaissance / port scan pattern.")
        if "brute_force" in alert_types:
            behavior_score += 25.0
            reasons.append("Evidence indicates automated authentication failure / brute-force behavior.")
        if "suspicious_port_access" in alert_types:
            behavior_score += 30.0
            reasons.append("Connection to known backdoor or high-risk service.")

        behavior_score = min(100.0, behavior_score)

        # 4. Recurrence Component (0 to 100)
        # Check span of time between first and last observed event
        recurrence_score = 0.0
        if len(events) >= 2:
            first_ts = min(e.timestamp for e in events)
            last_ts = max(e.timestamp for e in events)
            time_span_minutes = (last_ts - first_ts).total_seconds() / 60.0

            if time_span_minutes > 120 and n_events > 20:
                recurrence_score = 90.0
                reasons.append(f"Persistent activity spanning {time_span_minutes/60:.1f} hours.")
            elif time_span_minutes > 30 and n_events > 10:
                recurrence_score = 60.0
                reasons.append("Sustained recurring activity observed across multiple timeframes.")
            elif time_span_minutes > 5:
                recurrence_score = 30.0
            else:
                recurrence_score = 15.0

        # Weighted calculation
        total_score = (
            (cls.W_SEVERITY * sev_score) +
            (cls.W_FREQUENCY * freq_score) +
            (cls.W_BEHAVIORAL * behavior_score) +
            (cls.W_RECURRENCE * recurrence_score)
        )
        total_score = round(min(100.0, max(0.0, total_score)), 1)

        if not reasons:
            reasons.append("Baseline normal activity within expected parameters.")

        # Save to DB
        score_record = ThreatScore(
            source_ip=source_ip,
            score=total_score,
            severity_component=round(sev_score, 1),
            frequency_component=round(freq_score, 1),
            behavioral_component=round(behavior_score, 1),
            recurrence_component=round(recurrence_score, 1),
            reasons=json.dumps(reasons),
            calculated_at=datetime.utcnow()
        )
        db.add(score_record)

        # Update SourceIP table
        src_entry = db.query(SourceIP).filter(SourceIP.ip_address == source_ip).first()
        if src_entry:
            src_entry.threat_score = total_score
            if total_score >= 75:
                src_entry.risk_level = "Critical"
            elif total_score >= 50:
                src_entry.risk_level = "High"
            elif total_score >= 25:
                src_entry.risk_level = "Moderate"
            else:
                src_entry.risk_level = "Low"

        db.commit()
        return score_record
