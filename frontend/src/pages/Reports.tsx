import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchReports, generateReport } from '../services/api';
import { FileText, Plus, Calendar, Download, CheckCircle2 } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

export const Reports: React.FC = () => {
  const queryClient = useQueryClient();
  const [reportTitle, setReportTitle] = useState<string>('SOC Threat Intelligence Summary');
  const [timeWindow, setTimeWindow] = useState<number>(24);

  const { data: reports, isLoading } = useQuery({
    queryKey: ['threatReports'],
    queryFn: fetchReports,
  });

  const mutation = useMutation({
    mutationFn: () => generateReport(reportTitle, timeWindow),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threatReports'] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">Executive & Forensic Reports</h2>
          <p className="text-xs text-slate-400 mt-1">
            Generate and export synthesized security intelligence reports with evidence-backed findings.
          </p>
        </div>
      </div>

      {/* Generator Card */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40">
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Plus className="w-4 h-4 text-cyan-400" />
          Generate New Security Report
        </h3>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Report Title..."
            value={reportTitle}
            onChange={(e) => setReportTitle(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          />

          <select
            value={timeWindow}
            onChange={(e) => setTimeWindow(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value={6}>Past 6 Hours</option>
            <option value={12}>Past 12 Hours</option>
            <option value={24}>Past 24 Hours</option>
            <option value={48}>Past 48 Hours</option>
          </select>

          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs rounded-lg transition disabled:opacity-50"
          >
            {mutation.isPending ? 'Generating...' : 'Synthesize Report'}
          </button>
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-white">Generated Reports</h3>
        {isLoading && <p className="text-xs text-slate-500">Loading historical reports...</p>}

        {reports?.map((r) => (
          <div
            key={r.id}
            className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4"
          >
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  {r.title}
                </h4>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Generated: {formatDateTime(r.generated_at)}
                </p>
              </div>

              <div className="flex items-center gap-4 text-xs">
                <span className="text-slate-400">
                  Window: {formatDateTime(r.time_period_start)} &rarr; {formatDateTime(r.time_period_end)}
                </span>
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-800">
                <span className="text-slate-400 text-[10px] block">Analyzed Events</span>
                <span className="text-base font-bold text-white">{r.total_events}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-800">
                <span className="text-slate-400 text-[10px] block">Triggered Alerts</span>
                <span className="text-base font-bold text-amber-400">{r.total_alerts}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-800">
                <span className="text-slate-400 text-[10px] block">Correlated Attacks</span>
                <span className="text-base font-bold text-red-400">{r.attack_session_count}</span>
              </div>
            </div>

            {/* Key Findings */}
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
                Key Security Findings:
              </span>
              <ul className="space-y-1 text-xs text-slate-300">
                {r.key_findings.map((f, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-cyan-400 font-bold">&bull;</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}

        {(!reports || reports.length === 0) && !isLoading && (
          <div className="p-8 border border-slate-800 rounded-xl bg-slate-900/20 text-center text-xs text-slate-500">
            No threat reports generated yet. Click "Synthesize Report" above to compile telemetry data.
          </div>
        )}
      </div>
    </div>
  );
};
