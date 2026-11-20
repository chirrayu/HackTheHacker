import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.schemas.models import EventCreate

logger = logging.getLogger("hackthehacker.normalizer")

class EventNormalizer:
    """
    Standardizes disparate security logs (PCAP extracted flows, Suricata EVE JSON,
    and synthetic test fixtures) into a strictly validated UTC event structure.
    """

    VALID_SEVERITIES = {"Low", "Moderate", "High", "Critical"}

    @classmethod
    def normalize_timestamp(cls, raw_ts: Any) -> datetime:
        """Converts diverse timestamp representations to UTC datetime."""
        if isinstance(raw_ts, datetime):
            if raw_ts.tzinfo is not None:
                return raw_ts.astimezone(timezone.utc).replace(tzinfo=None)
            return raw_ts

        if isinstance(raw_ts, (int, float)):
            return datetime.fromtimestamp(raw_ts, tz=timezone.utc).replace(tzinfo=None)

        if isinstance(raw_ts, str):
            # Try ISO formats with or without Z
            cleaned = raw_ts.replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(cleaned)
                if dt.tzinfo is not None:
                    return dt.astimezone(timezone.utc).replace(tzinfo=None)
                return dt
            except ValueError:
                pass

        return datetime.utcnow()

    @classmethod
    def normalize_severity(cls, raw_sev: Any) -> str:
        """Maps numerical or text severity into standard project tiers."""
        if isinstance(raw_sev, (int, float)):
            if raw_sev >= 75:
                return "Critical"
            elif raw_sev >= 50:
                return "High"
            elif raw_sev >= 25:
                return "Moderate"
            return "Low"

        if isinstance(raw_sev, str):
            s = raw_sev.strip().capitalize()
            if s in cls.VALID_SEVERITIES:
                return s
            if s.lower() in ("info", "informational", "debug"):
                return "Low"
            if s.lower() in ("warn", "warning", "medium"):
                return "Moderate"
            if s.lower() in ("crit", "emergency", "fatal"):
                return "Critical"

        return "Low"

    @classmethod
    def from_suricata_eve(cls, record: Dict[str, Any]) -> Optional[EventCreate]:
        """Parses a single Suricata EVE JSON event into normalized EventCreate."""
        try:
            event_type = record.get("event_type", "alert")
            src_ip = record.get("src_ip")
            dest_ip = record.get("dest_ip")

            if not src_ip or not dest_ip:
                return None

            alert_data = record.get("alert", {})
            raw_sev = alert_data.get("severity", 3)
            # Suricata severity: 1=high/critical, 2=medium, 3=low/info
            sev_map = {1: "High", 2: "Moderate", 3: "Low"}
            severity = sev_map.get(raw_sev, "Moderate")
            
            signature = alert_data.get("signature", f"Suricata {event_type.upper()}")

            return EventCreate(
                timestamp=cls.normalize_timestamp(record.get("timestamp")),
                source_ip=str(src_ip),
                destination_ip=str(dest_ip),
                source_port=record.get("src_port"),
                destination_port=record.get("dest_port"),
                protocol=str(record.get("proto", "TCP")).upper(),
                event_type=f"suricata_{event_type}",
                severity=severity,
                sensor="suricata_eve",
                signature=signature,
                raw_evidence=json.dumps(record)
            )
        except Exception as e:
            logger.warning(f"Failed to normalize Suricata record: {e}")
            return None

    @classmethod
    def from_flow_packet(
        cls,
        src_ip: str,
        dst_ip: str,
        src_port: Optional[int],
        dst_port: Optional[int],
        protocol: str,
        event_type: str,
        severity: str = "Low",
        sensor: str = "pcap_parser",
        signature: Optional[str] = None,
        raw_evidence: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> EventCreate:
        """Constructs an EventCreate from extracted packet / flow metadata."""
        return EventCreate(
            timestamp=cls.normalize_timestamp(timestamp or datetime.utcnow()),
            source_ip=src_ip,
            destination_ip=dst_ip,
            source_port=src_port,
            destination_port=dst_port,
            protocol=protocol.upper(),
            event_type=event_type,
            severity=cls.normalize_severity(severity),
            sensor=sensor,
            signature=signature or f"{protocol} {event_type}",
            raw_evidence=json.dumps(raw_evidence or {})
        )
