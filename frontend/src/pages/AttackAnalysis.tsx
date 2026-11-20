import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAttackSessions } from '../services/api';
import { AttackSession } from '../types';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatDateTime } from '../utils/formatters';
import { Crosshair, ShieldAlert, ArrowRight, Clock, Hash } from 'lucide-react';

export const AttackAnalysis: React.FC = () => {
  const [selectedSession, setSelectedSession] = useState<AttackSession | null>(null);

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['attackSessions'],
    queryFn: () => fetchAttackSessions(50),
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Correlated Attack Sessions</h2>
        <p className="text-xs text-slate-400 mt-1">
          Algorithmic multi-event correlation grouping related reconnaissance, scans, and exploitation attempts.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sessions List */}
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-sm font-semibold text-white">Identified Attack Chains</h3>
          {isLoading && <p className="text-xs text-slate-500">Loading attack sessions...</p>}
          
          {sessions?.map((s) => (
            <div
              key={s.id}
              onClick={() => setSelectedSession(s)}
              className={`p-4 rounded-xl border cursor-pointer transition ${
                selectedSession?.id === s.id
                  ? 'border-cyan-500/50 bg-cyan-950/20'
                  : 'border-slate-800 bg-slate-900/40 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <StatusBadge severity={s.highest_severity} size="sm" />
                <span className="text-xs font-mono font-semibold text-cyan-400">
                  Risk: {s.threat_score}/100
                </span>
              </div>

              <div className="flex items-center gap-2 text-xs font-mono text-slate-200">
                <span>{s.source_ip}</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                <span>{s.destination_ip}</span>
              </div>

              <div className="flex items-center justify-between mt-3 text-[11px] text-slate-500">
                <span className="flex items-center gap-1">
                  <Hash className="w-3 h-3" />
                  {s.event_count} Events
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDateTime(s.last_seen)}
                </span>
              </div>
            </div>
          ))}

          {(!sessions || sessions.length === 0) && !isLoading && (
            <div className="p-8 border border-slate-800 rounded-xl bg-slate-900/20 text-center text-xs text-slate-500">
              No correlated attack sessions currently active.
            </div>
          )}
        </div>

        {/* Detailed Session Investigation View */}
        <div className="lg:col-span-2">
          {selectedSession ? (
            <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h3 className="text-base font-bold text-white">Investigation: {selectedSession.source_ip}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Session ID: {selectedSession.id}</p>
                </div>
                <StatusBadge severity={selectedSession.highest_severity} />
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800 text-xs">
                  <span className="text-slate-500 block mb-1">Target Machine</span>
                  <span className="font-mono font-bold text-slate-200">{selectedSession.destination_ip}</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800 text-xs">
                  <span className="text-slate-500 block mb-1">Overall Threat Score</span>
                  <span className="font-bold text-cyan-400">{selectedSession.threat_score} / 100</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800 text-xs">
                  <span className="text-slate-500 block mb-1">Event Volume</span>
                  <span className="font-bold text-slate-200">{selectedSession.event_count} events</span>
                </div>
              </div>

              {/* Categories Observed */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Observed Attack Categories
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedSession.detection_categories.map((cat, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-xs font-mono border border-slate-700"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </div>

              {/* Timeline summary */}
              <div className="border-t border-slate-800 pt-4 space-y-2 text-xs">
                <h4 className="font-semibold text-slate-300">Observation Timeframe</h4>
                <p className="text-slate-400">
                  <strong className="text-slate-200">First Observed:</strong>{' '}
                  {formatDateTime(selectedSession.first_seen)}
                </p>
                <p className="text-slate-400">
                  <strong className="text-slate-200">Last Activity:</strong>{' '}
                  {formatDateTime(selectedSession.last_seen)}
                </p>
              </div>
            </div>
          ) : (
            <div className="h-64 border border-dashed border-slate-800 rounded-xl flex items-center justify-center text-xs text-slate-500">
              Select an attack session from the left to inspect correlated forensic evidence.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
