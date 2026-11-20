from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# ==================== Health Schemas ====================
class ComponentHealth(BaseModel):
    name: str
    status: str  # healthy, degraded, unavailable
    details: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    timestamp: datetime
    database: ComponentHealth
    virtualbox: ComponentHealth
    capture_tool: ComponentHealth
    active_threats: int

# ==================== Event Schemas ====================
class EventBase(BaseModel):
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: str = "TCP"
    event_type: str
    severity: str = "Low"
    sensor: str = "pcap_parser"
    signature: Optional[str] = None
    raw_evidence: Optional[str] = None

class EventCreate(EventBase):
    timestamp: Optional[datetime] = None

class EventResponse(EventBase):
    id: str
    timestamp: datetime
    related_attack_id: Optional[str] = None

    class Config:
        from_attributes = True

class EventFilter(BaseModel):
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    severity: Optional[str] = None
    event_type: Optional[str] = None
    limit: int = 50
    offset: int = 0

# ==================== Alert Schemas ====================
class AlertBase(BaseModel):
    alert_type: str
    title: str
    description: Optional[str] = None
    severity: str
    source_ip: str
    destination_ip: str
    status: str = "new"
    confidence: float = 1.0
    evidence: Optional[str] = None

class AlertCreate(AlertBase):
    event_id: Optional[str] = None
    related_attack_id: Optional[str] = None

class AlertResponse(AlertBase):
    id: str
    event_id: Optional[str] = None
    related_attack_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== Attack Session Schemas ====================
class AttackSessionResponse(BaseModel):
    id: str
    source_ip: str
    destination_ip: str
    first_seen: datetime
    last_seen: datetime
    event_count: int
    detection_categories: List[str]
    highest_severity: str
    threat_score: float
    status: str
    summary: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== Asset Schemas ====================
class AssetBase(BaseModel):
    ip_address: str
    hostname: Optional[str] = None
    os_type: Optional[str] = None
    role: Optional[str] = None
    status: str = "active"
    services: Optional[List[Dict[str, Any]]] = None

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: str
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True

# ==================== Threat Score Schemas ====================
class ThreatScoreResponse(BaseModel):
    source_ip: str
    score: float
    severity_component: float
    frequency_component: float
    behavioral_component: float
    recurrence_component: float
    reasons: List[str]
    calculated_at: datetime

# ==================== Analytics Schemas ====================
class TopSourceIP(BaseModel):
    ip_address: str
    event_count: int
    threat_score: float
    risk_level: str
    last_seen: datetime

class TimelinePoint(BaseModel):
    timestamp: str
    events: int
    alerts: int

class AnalyticsOverview(BaseModel):
    total_events: int
    active_alerts: int
    critical_threats: int
    monitored_assets: int
    severity_breakdown: Dict[str, int]
    top_sources: List[TopSourceIP]
    recent_activity_timeline: List[TimelinePoint]

# ==================== Report Schemas ====================
class ReportCreate(BaseModel):
    title: str
    time_period_hours: int = 24

class ReportResponse(BaseModel):
    id: str
    title: str
    time_period_start: datetime
    time_period_end: datetime
    total_events: int
    total_alerts: int
    attack_session_count: int
    severity_distribution: Dict[str, int]
    key_findings: List[str]
    generated_at: datetime

    class Config:
        from_attributes = True
