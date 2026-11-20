import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAnalyticsOverview, fetchAlerts } from '../services/api';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatDateTime } from '../utils/formatters';
import { Activity, ShieldAlert, AlertTriangle, Server } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

const SEVERITY_COLORS = {
  Critical: '#ef4444',
  High: '#f59e0b',
  Moderate: '#06b6d4',
  Low: '#64748b',
};

export const Overview: React.FC = () => {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analyticsOverview'],
    queryFn: fetchAnalyticsOverview,
    refetchInterval: 5000,
  });

  const { data: recentAlerts } = useQuery({
    queryKey: ['recentAlerts'],
    queryFn: () => fetchAlerts(6),
    refetchInterval: 5000,
  });

  if (analyticsLoading) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-400">
        Loading telemetry and sensor intelligence...
      </div>
    );
  }

  const pieData = analytics?.severity_breakdown
    ? Object.entries(analytics.severity_breakdown).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Security Operations Overview</h2>
        <p className="text-xs text-slate-400 mt-1">
          Real-time network monitoring, alert triage, and correlated threat intelligence.
        </p>
      </div>

      {/* Top 4 Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Events Ingested"
          value={analytics?.total_events.toLocaleString() || 0}
          subtitle="From PCAP & Suricata sensors"
          icon={Activity}
          variant="default"
        />
        <MetricCard
          title="Active Security Alerts"
          value={analytics?.active_alerts || 0}
          subtitle="Requiring triage"
          icon={AlertTriangle}
          variant="amber"
        />
        <MetricCard
          title="Critical Threats"
          value={analytics?.critical_threats || 0}
          subtitle="Exploitation & backdoor indicators"
          icon={ShieldAlert}
          variant="critical"
        />
        <MetricCard
          title="Monitored Lab Assets"
          value={analytics?.monitored_assets || 3}
          subtitle="Windows, Kali & Target"
          icon={Server}
          variant="cyan"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 p-5 rounded-xl border border-slate-800 bg-slate-900/40">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Event & Alert Activity Timeline</h3>
            <span className="text-xs text-slate-500">Last observed activity</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analytics?.recent_activity_timeline || []}>
                <defs>
                  <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="events" stroke="#06b6d4" fillOpacity={1} fill="url(#colorEvents)" name="Events" />
                <Area type="monotone" dataKey="alerts" stroke="#ef4444" fillOpacity={1} fill="url(#colorAlerts)" name="Alerts" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Pie Chart */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 flex flex-col">
          <h3 className="text-sm font-semibold text-white mb-2">Severity Distribution</h3>
          <div className="h-64 flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry) => (
                    <Cell
                      key={`cell-${entry.name}`}
                      fill={SEVERITY_COLORS[entry.name as keyof typeof SEVERITY_COLORS] || '#64748b'}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Tables Row: Top Sources & Recent Detections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Active Source IPs */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40">
          <h3 className="text-sm font-semibold text-white mb-4">Top Communicating Source IPs</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400">
                <tr>
                  <th className="pb-2 font-medium">Source IP</th>
                  <th className="pb-2 font-medium">Events</th>
                  <th className="pb-2 font-medium">Threat Score</th>
                  <th className="pb-2 font-medium">Risk Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {analytics?.top_sources?.map((s) => (
                  <tr key={s.ip_address} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-mono text-slate-200">{s.ip_address}</td>
                    <td className="py-2.5 text-slate-400">{s.event_count}</td>
                    <td className="py-2.5 font-semibold text-slate-200">{s.threat_score} / 100</td>
                    <td className="py-2.5">
                      <StatusBadge severity={s.risk_level} size="sm" />
                    </td>
                  </tr>
                ))}
                {(!analytics?.top_sources || analytics.top_sources.length === 0) && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-slate-500">
                      No active source nodes recorded yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Security Alerts */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40">
          <h3 className="text-sm font-semibold text-white mb-4">Recent Detection Alerts</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400">
                <tr>
                  <th className="pb-2 font-medium">Severity</th>
                  <th className="pb-2 font-medium">Alert</th>
                  <th className="pb-2 font-medium">Target</th>
                  <th className="pb-2 font-medium">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentAlerts?.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5">
                      <StatusBadge severity={a.severity} size="sm" />
                    </td>
                    <td className="py-2.5 font-medium text-slate-200 max-w-xs truncate">{a.title}</td>
                    <td className="py-2.5 font-mono text-slate-400">{a.destination_ip}</td>
                    <td className="py-2.5 text-slate-500">{formatDateTime(a.created_at)}</td>
                  </tr>
                ))}
                {(!recentAlerts || recentAlerts.length === 0) && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-slate-500">
                      No security alerts recorded.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
