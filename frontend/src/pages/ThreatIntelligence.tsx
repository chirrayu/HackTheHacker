import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchTopSources, fetchThreatScore } from '../services/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { Cpu, ShieldAlert, CheckCircle, Info } from 'lucide-react';

export const ThreatIntelligence: React.FC = () => {
  const [selectedIp, setSelectedIp] = useState<string>('192.168.56.20');

  const { data: sources } = useQuery({
    queryKey: ['threatIntelSources'],
    queryFn: () => fetchTopSources(10),
  });

  const { data: scoreData, isLoading: scoreLoading } = useQuery({
    queryKey: ['threatScore', selectedIp],
    queryFn: () => fetchThreatScore(selectedIp),
    enabled: !!selectedIp,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Threat Intelligence & Scoring</h2>
        <p className="text-xs text-slate-400 mt-1">
          Explainable, mathematically formulated risk scores (0–100) backed by observable telemetry evidence.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Source Nodes */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
          <h3 className="text-sm font-semibold text-white">Observed Source Nodes</h3>
          <div className="space-y-2">
            {sources?.map((s) => (
              <div
                key={s.ip_address}
                onClick={() => setSelectedIp(s.ip_address)}
                className={`p-3 rounded-lg border cursor-pointer transition flex items-center justify-between ${
                  selectedIp === s.ip_address
                    ? 'border-cyan-500/50 bg-cyan-950/20'
                    : 'border-slate-800 bg-slate-900/60 hover:bg-slate-800/40'
                }`}
              >
                <div>
                  <span className="font-mono text-xs font-semibold text-white block">{s.ip_address}</span>
                  <span className="text-[11px] text-slate-500">{s.event_count} Events</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-cyan-400 block">{s.threat_score}/100</span>
                  <StatusBadge severity={s.risk_level} size="sm" />
                </div>
              </div>
            ))}
            {(!sources || sources.length === 0) && (
              <div
                onClick={() => setSelectedIp('192.168.56.20')}
                className="p-3 rounded-lg border border-cyan-500/50 bg-cyan-950/20 cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold text-white">192.168.56.20</span>
                  <span className="text-xs font-bold text-cyan-400">Kali Attacker</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Explainable Threat Score Card */}
        <div className="lg:col-span-2 p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-cyan-400" />
                <h3 className="text-base font-bold text-white">Risk Score: {selectedIp}</h3>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Model: Risk = (0.30 &times; Severity) + (0.25 &times; Frequency) + (0.25 &times; Behavioral) + (0.20 &times; Recurrence)
              </p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-black text-cyan-400">
                {scoreData?.score ?? 0}
              </span>
              <span className="text-xs text-slate-500 block">/ 100</span>
            </div>
          </div>

          {scoreLoading ? (
            <p className="text-xs text-slate-500">Calculating explainable threat score...</p>
          ) : (
            <div className="space-y-6">
              {/* Component Progress Bars */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Severity Component (30%)</span>
                    <span className="font-bold text-slate-200">{scoreData?.severity_component}/100</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${scoreData?.severity_component ?? 0}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Frequency Component (25%)</span>
                    <span className="font-bold text-slate-200">{scoreData?.frequency_component}/100</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-amber-500 h-2 rounded-full"
                      style={{ width: `${scoreData?.frequency_component ?? 0}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Behavioral Indicators (25%)</span>
                    <span className="font-bold text-slate-200">{scoreData?.behavioral_component}/100</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-cyan-500 h-2 rounded-full"
                      style={{ width: `${scoreData?.behavioral_component ?? 0}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Recurrence Factor (20%)</span>
                    <span className="font-bold text-slate-200">{scoreData?.recurrence_component}/100</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full"
                      style={{ width: `${scoreData?.recurrence_component ?? 0}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Explainable Reasons */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Observable Justification & Evidence
                </h4>
                <div className="space-y-2">
                  {scoreData?.reasons.map((reason, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-300"
                    >
                      <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>{reason}</span>
                    </div>
                  ))}
                  {(!scoreData?.reasons || scoreData.reasons.length === 0) && (
                    <p className="text-xs text-slate-500">No adverse threat factors identified for this node.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
