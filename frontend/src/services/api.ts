import axios from 'axios';
import {
  SecurityEvent,
  SecurityAlert,
  AttackSession,
  MonitoredAsset,
  AnalyticsOverview,
  SystemHealth,
  TopSourceIP,
  ThreatScoreData,
  ReportItem,
  TimelinePoint
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchHealth = async (): Promise<SystemHealth> => {
  const { data } = await api.get<SystemHealth>('/health');
  return data;
};

export const fetchEvents = async (limit: number = 50): Promise<SecurityEvent[]> => {
  const { data } = await api.get<SecurityEvent[]>('/events', { params: { limit } });
  return data;
};

export const fetchAlerts = async (limit: number = 50): Promise<SecurityAlert[]> => {
  const { data } = await api.get<SecurityAlert[]>('/alerts', { params: { limit } });
  return data;
};

export const fetchAttackSessions = async (limit: number = 50): Promise<AttackSession[]> => {
  const { data } = await api.get<AttackSession[]>('/attacks', { params: { limit } });
  return data;
};

export const fetchAssets = async (): Promise<MonitoredAsset[]> => {
  const { data } = await api.get<MonitoredAsset[]>('/assets');
  return data;
};

export const fetchAnalyticsOverview = async (): Promise<AnalyticsOverview> => {
  const { data } = await api.get<AnalyticsOverview>('/analytics/overview');
  return data;
};

export const fetchTimeline = async (hours: number = 12): Promise<TimelinePoint[]> => {
  const { data } = await api.get<TimelinePoint[]>('/analytics/timeline', { params: { hours } });
  return data;
};

export const fetchTopSources = async (limit: number = 10): Promise<TopSourceIP[]> => {
  const { data } = await api.get<TopSourceIP[]>('/intelligence/top-sources', { params: { limit } });
  return data;
};

export const fetchThreatScore = async (sourceIp: string): Promise<ThreatScoreData> => {
  const { data } = await api.get<ThreatScoreData>(`/intelligence/score/${sourceIp}`);
  return data;
};

export const fetchReports = async (): Promise<ReportItem[]> => {
  const { data } = await api.get<ReportItem[]>('/reports');
  return data;
};

export const generateReport = async (title: string, hours: number = 24): Promise<ReportItem> => {
  const { data } = await api.post<ReportItem>('/reports/generate', {
    title,
    time_period_hours: hours,
  });
  return data;
};

export const updateAlertStatus = async (alertId: string, status: string): Promise<any> => {
  const { data } = await api.patch(`/alerts/${alertId}/status`, null, {
    params: { new_status: status },
  });
  return data;
};

export const fetchSensorStatus = async (): Promise<any> => {
  const { data } = await api.get('/sensors/status');
  return data;
};

export default api;
