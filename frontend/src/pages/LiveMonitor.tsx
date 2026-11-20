import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchEvents } from '../services/api';
import { SecurityEvent } from '../types';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatTimestamp } from '../utils/formatters';
import { Radio, Search, Filter, RefreshCw, Terminal } from 'lucide-react';

export const LiveMonitor: React.FC = () => {
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  const { data: events, refetch, isFetching } = useQuery({
    queryKey: ['liveEvents'],
    queryFn: () => fetchEvents(100),
    refetchInterval: 3000,
  });

  const filteredEvents = (events || []).filter((e) => {
    if (filterSeverity !== 'all' && e.severity !== filterSeverity) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        e.source_ip.toLowerCase().includes(q) ||
        e.destination_ip.toLowerCase().includes(q) ||
        e.protocol.toLowerCase().includes(q) ||
        (e.signature && e.signature.toLowerCase().includes(q))
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white">Live Threat Monitor</h2>
            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Live Ingestion Feed
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time packet capture flows and normalized Suricata intrusion telemetry.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 text-xs text-slate-300 hover:text-white hover:bg-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh Stream
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search by IP, protocol, or signature..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="all">All Severities</option>
            <option value="Critical">Critical Only</option>
            <option value="High">High Only</option>
            <option value="Moderate">Moderate Only</option>
            <option value="Low">Low Only</option>
          </select>
        </div>
      </div>

      {/* Events Stream Table */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400">
              <tr>
                <th className="pb-3 font-medium">Timestamp</th>
                <th className="pb-3 font-medium">Severity</th>
                <th className="pb-3 font-medium">Source</th>
                <th className="pb-3 font-medium">Target</th>
                <th className="pb-3 font-medium">Proto</th>
                <th className="pb-3 font-medium">Event Type / Signature</th>
                <th className="pb-3 font-medium">Sensor</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredEvents.map((e) => (
                <tr
                  key={e.id}
                  onClick={() => setSelectedEvent(e)}
                  className="hover:bg-slate-800/40 cursor-pointer transition"
                >
                  <td className="py-2.5 text-slate-400">{formatTimestamp(e.timestamp)}</td>
                  <td className="py-2.5">
                    <StatusBadge severity={e.severity} size="sm" />
                  </td>
                  <td className="py-2.5 text-slate-200">
                    {e.source_ip}
                    {e.source_port ? `:${e.source_port}` : ''}
                  </td>
                  <td className="py-2.5 text-slate-200">
                    {e.destination_ip}
                    {e.destination_port ? `:${e.destination_port}` : ''}
                  </td>
                  <td className="py-2.5 font-sans font-medium text-slate-300">{e.protocol}</td>
                  <td className="py-2.5 font-sans text-slate-300 max-w-sm truncate">
                    {e.signature || e.event_type}
                  </td>
                  <td className="py-2.5 font-sans text-slate-500">{e.sensor}</td>
                </tr>
              ))}
              {filteredEvents.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 font-sans">
                    No matching network security events found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Raw Evidence Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Event Raw Evidence & Packet Details</h3>
              </div>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800"
              >
                Close (ESC)
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-slate-500">Event ID:</span>
                <p className="font-mono text-slate-300">{selectedEvent.id}</p>
              </div>
              <div>
                <span className="text-slate-500">Sensor:</span>
                <p className="text-slate-300">{selectedEvent.sensor}</p>
              </div>
              <div>
                <span className="text-slate-500">Source:</span>
                <p className="font-mono text-slate-300">
                  {selectedEvent.source_ip}:{selectedEvent.source_port}
                </p>
              </div>
              <div>
                <span className="text-slate-500">Target:</span>
                <p className="font-mono text-slate-300">
                  {selectedEvent.destination_ip}:{selectedEvent.destination_port}
                </p>
              </div>
            </div>

            <div>
              <span className="text-xs text-slate-500 mb-1 block">Raw Packet Telemetry:</span>
              <pre className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg text-xs font-mono text-cyan-300 overflow-x-auto max-h-56">
                {selectedEvent.raw_evidence
                  ? JSON.stringify(JSON.parse(selectedEvent.raw_evidence), null, 2)
                  : 'No raw payload available.'}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
