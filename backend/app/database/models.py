import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index
)
from sqlalchemy.orm import relationship
from .connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=generate_uuid)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    hostname = Column(String(255), nullable=True)
    os_type = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)  # e.g., 'Target', 'Attacker', 'Monitor'
    status = Column(String(50), default="active")  # active, offline, unknown
    services = Column(Text, nullable=True)  # JSON-encoded array of open ports/services
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_assets_ip", "ip_address"),
    )

class AttackSession(Base):
    __tablename__ = "attack_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    source_ip = Column(String(45), nullable=False, index=True)
    destination_ip = Column(String(45), nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow, index=True)
    last_seen = Column(DateTime, default=datetime.utcnow, index=True)
    event_count = Column(Integer, default=1)
    detection_categories = Column(Text, default="[]")  # JSON list
    highest_severity = Column(String(20), default="Low")  # Low, Moderate, High, Critical
    threat_score = Column(Float, default=0.0)
    status = Column(String(50), default="active")  # active, closed, investigated
    summary = Column(Text, nullable=True)

    # Relationships
    events = relationship("Event", back_populates="attack_session")
    alerts = relationship("Alert", back_populates="attack_session")

    __table_args__ = (
        Index("ix_session_ips", "source_ip", "destination_ip"),
    )

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source_ip = Column(String(45), nullable=False, index=True)
    destination_ip = Column(String(45), nullable=False, index=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True, index=True)
    protocol = Column(String(20), nullable=False, default="TCP")
    event_type = Column(String(100), nullable=False, index=True)  # port_scan, brute_force, recon, traffic
    severity = Column(String(20), default="Low", index=True)  # Low, Moderate, High, Critical
    sensor = Column(String(50), default="pcap_parser")  # suricata, tshark, scapy, synthetic
    signature = Column(String(255), nullable=True)
    raw_evidence = Column(Text, nullable=True)  # JSON string
    related_attack_id = Column(String, ForeignKey("attack_sessions.id"), nullable=True, index=True)

    # Relationships
    attack_session = relationship("AttackSession", back_populates="events")
    alerts = relationship("Alert", back_populates="event")

    __table_args__ = (
        Index("ix_events_src_dst", "source_ip", "destination_ip"),
        Index("ix_events_ts_sev", "timestamp", "severity"),
    )

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("events.id"), nullable=True, index=True)
    related_attack_id = Column(String, ForeignKey("attack_sessions.id"), nullable=True, index=True)
    alert_type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, default="Moderate", index=True)
    source_ip = Column(String(45), nullable=False, index=True)
    destination_ip = Column(String(45), nullable=False, index=True)
    status = Column(String(50), default="new")  # new, investigating, acknowledged, resolved
    confidence = Column(Float, default=1.0)
    evidence = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    event = relationship("Event", back_populates="alerts")
    attack_session = relationship("AttackSession", back_populates="alerts")

class SourceIP(Base):
    __tablename__ = "source_ips"

    id = Column(String, primary_key=True, default=generate_uuid)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    total_events = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    threat_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="Low")  # Low, Moderate, High, Critical
    attack_count = Column(Integer, default=0)
    is_internal_lab = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

class AttackPattern(Base):
    __tablename__ = "attack_patterns"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)  # Reconnaissance, Initial Access, Discovery
    description = Column(Text, nullable=True)
    mitre_technique_id = Column(String(50), nullable=True)  # e.g., 'T1046', 'T1110'
    severity_default = Column(String(20), default="Moderate")

class ThreatScore(Base):
    __tablename__ = "threat_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    source_ip = Column(String(45), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0 to 100
    severity_component = Column(Float, default=0.0)
    frequency_component = Column(Float, default=0.0)
    behavioral_component = Column(Float, default=0.0)
    recurrence_component = Column(Float, default=0.0)
    reasons = Column(Text, nullable=False)  # JSON array of reasons
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    time_period_start = Column(DateTime, nullable=False)
    time_period_end = Column(DateTime, nullable=False)
    total_events = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    attack_session_count = Column(Integer, default=0)
    severity_distribution = Column(Text, nullable=True)  # JSON string
    key_findings = Column(Text, nullable=True)  # JSON string
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    detection_type = Column(String(50), nullable=False)  # port_scan, brute_force, recon, suspicious_conn
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="Moderate")
    enabled = Column(Boolean, default=True)
    parameters = Column(Text, nullable=True)  # JSON config (e.g. thresholds)
    created_at = Column(DateTime, default=datetime.utcnow)
