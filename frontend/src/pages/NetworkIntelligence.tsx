import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchEvents, fetchTopSources } from '../services/api';
import { Network, Server, ArrowUpDown } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

export const NetworkIntelligence: React.FC = () => {
  const { data: events } = useQuery({
    queryKey: ['networkEvents'],
    queryFn: () => fetchEvents(200),
    refetchInterval: 10000,
  });

  const { data: topSources } = useQuery({
    queryKey: ['topSources'],
    queryFn: () => fetchTopSources(10),
  });

  // Calculate Port Breakdown
  const portCounts: Record<number, number> = {};
  (events || []).forEach((e) => {
    if (e.destination_port) {
      portCounts[e.destination_port] = (portCounts[e.destination_port] || 0) + 1;
    }
  });

  const portData = Object.entries(portCounts)
    .map(([port, count]) => ({
      port: `Port ${port}`,
      count,
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  // Protocol Distribution
  const protoCounts: Record<string, number> = {};
  (events || []).forEach((e) => {
    protoCounts[e.protocol] = (protoCounts[e.protocol] || 0) + 1;
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Network Traffic Intelligence</h2>
        <p className="text-xs text-slate-400 mt-1">
          Analysis of communicating endpoints, targeted application ports, and transport protocols.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Probed Destination Ports */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40">
          <h3 className="text-sm font-semibold text-white mb-4">Frequently Accessed Services & Ports</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={portData} layout="vertical">
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="port" type="category" stroke="#64748b" fontSize={11} width={80} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Protocol Breakdown */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">Transport Protocols</h3>
            <div className="grid grid-cols-3 gap-3 text-center">
              {Object.entries(protoCounts).map(([proto, count]) => (
                <div key={proto} className="p-4 rounded-lg bg-slate-800/40 border border-slate-800">
                  <span className="text-xs text-slate-400 block mb-1 font-mono">{proto}</span>
                  <span className="text-xl font-bold text-cyan-400">{count}</span>
                  <span className="text-[10px] text-slate-500 block mt-1">Packets/Flows</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-400 mt-6">
            <p className="font-semibold text-slate-300 mb-1">Host-Only Lab Topology</p>
            <p>Windows Host (192.168.56.1) &bull; Kali Attacker (192.168.56.20) &bull; Metasploitable (192.168.56.30)</p>
          </div>
        </div>
      </div>
    </div>
  );
};
