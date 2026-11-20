export type SeverityLevel = 'Low' | 'Moderate' | 'High' | 'Critical';

export interface SecurityEvent {
  id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol: string;
  event_type: string;
  severity: SeverityLevel;
  sensor: string;
  signature?: string;
  raw_evidence?: string;
  related_attack_id?: string;
}

export interface SecurityAlert {
  id: string;
  event_id?: string;
  related_attack_id?: string;
  alert_type: string;
  title: string;
  description?: string;
  severity: SeverityLevel;
  source_ip: string;
  destination_ip: string;
  status: 'new' | 'investigating' | 'acknowledged' | 'resolved';
  confidence: number;
  evidence?: string;
  created_at: string;
}

export interface AttackSession {
  id: string;
  source_ip: string;
  destination_ip: string;
  first_seen: string;
  last_seen: string;
  event_count: number;
  detection_categories: string[];
  highest_severity: SeverityLevel;
  threat_score: number;
  status: string;
  summary?: string;
}

export interface MonitoredAsset {
  id: string;
  ip_address: string;
  hostname?: string;
  os_type?: string;
  role?: string;
  status: 'active' | 'offline' | 'unknown';
  services?: Array<{ port: number; service: string; status: string }>;
  first_seen: string;
  last_seen: string;
}

export interface ThreatScoreData {
  source_ip: string;
  score: number;
  severity_component: number;
  frequency_component: number;
  behavioral_component: number;
  recurrence_component: number;
  reasons: string[];
  calculated_at: string;
}

export interface TopSourceIP {
  ip_address: string;
  event_count: number;
  threat_score: number;
  risk_level: SeverityLevel;
  last_seen: string;
}

export interface TimelinePoint {
  timestamp: string;
  events: number;
  alerts: number;
}

export interface AnalyticsOverview {
  total_events: number;
  active_alerts: number;
  critical_threats: number;
  monitored_assets: number;
  severity_breakdown: Record<SeverityLevel, number>;
  top_sources: TopSourceIP[];
  recent_activity_timeline: TimelinePoint[];
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unavailable';
  version: string;
  uptime_seconds: number;
  timestamp: string;
  database: { name: string; status: string; details?: string };
  virtualbox: { name: string; status: string; details?: string };
  capture_tool: { name: string; status: string; details?: string };
  active_threats: number;
}

export interface ReportItem {
  id: string;
  title: string;
  time_period_start: string;
  time_period_end: string;
  total_events: number;
  total_alerts: number;
  attack_session_count: number;
  severity_distribution: Record<string, number>;
  key_findings: string[];
  generated_at: string;
}
