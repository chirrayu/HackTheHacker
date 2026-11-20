import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Event, Asset, SourceIP
from app.schemas.models import EventCreate

logger = logging.getLogger("hackthehacker.event_ingestor")

class EventIngestor:
    """
    Ingests normalized security events into the database,
    maintains asset discovery, and triggers detection analysis.
    """

    def __init__(self, db: Session):
        self.db = db

    def ingest_single_event(self, event_in: EventCreate) -> Event:
        """Stores a single event and updates asset and source IP telemetry."""
        # Check for duplicate within small window (idempotency)
        existing = self.db.query(Event).filter(
            Event.source_ip == event_in.source_ip,
            Event.destination_ip == event_in.destination_ip,
            Event.timestamp == event_in.timestamp,
            Event.signature == event_in.signature
        ).first()

        if existing:
            return existing

        db_event = Event(
            timestamp=event_in.timestamp or datetime.utcnow(),
            source_ip=event_in.source_ip,
            destination_ip=event_in.destination_ip,
            source_port=event_in.source_port,
            destination_port=event_in.destination_port,
            protocol=event_in.protocol,
            event_type=event_in.event_type,
            severity=event_in.severity,
            sensor=event_in.sensor,
            signature=event_in.signature,
            raw_evidence=event_in.raw_evidence
        )
        self.db.add(db_event)

        # Update or create SourceIP profile
        source = self.db.query(SourceIP).filter(SourceIP.ip_address == event_in.source_ip).first()
        if source:
            source.total_events += 1
            source.last_seen = db_event.timestamp
        else:
            source = SourceIP(
                ip_address=event_in.source_ip,
                total_events=1,
                first_seen=db_event.timestamp,
                last_seen=db_event.timestamp
            )
            self.db.add(source)

        # Register discovered destination asset if unknown
        asset = self.db.query(Asset).filter(Asset.ip_address == event_in.destination_ip).first()
        if not asset:
            asset = Asset(
                ip_address=event_in.destination_ip,
                hostname="Discovered Target Node",
                status="active",
                role="Target" if event_in.destination_ip == "192.168.56.30" else "Host",
                first_seen=db_event.timestamp,
                last_seen=db_event.timestamp
            )
            self.db.add(asset)
        else:
            asset.last_seen = db_event.timestamp

        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def ingest_batch(self, events: List[EventCreate]) -> int:
        """Efficiently ingests a list of normalized events."""
        ingested_count = 0
        for ev in events:
            try:
                self.ingest_single_event(ev)
                ingested_count += 1
            except Exception as e:
                logger.error(f"Failed to ingest event {ev}: {e}")
                self.db.rollback()

        return ingested_count
