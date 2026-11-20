import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '../../services/api';
import { Bell, ShieldCheck, AlertCircle } from 'lucide-react';

export const Header: React.FC = () => {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 10000,
  });

  const isHealthy = health?.status === 'healthy';

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/60 backdrop-blur px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-xs text-slate-400">Environment:</span>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
          Windows 11 VM Host
        </span>
      </div>

      <div className="flex items-center gap-6">
        {/* System Health Badge */}
        <div className="flex items-center gap-2 text-xs">
          {isHealthy ? (
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 text-amber-400" />
          )}
          <span className="text-slate-400">Platform Status:</span>
          <span
            className={`font-semibold capitalize ${
              isHealthy ? 'text-emerald-400' : 'text-amber-400'
            }`}
          >
            {health?.status || 'Connecting...'}
          </span>
        </div>

        {/* Active Threats Counter */}
        {health && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
            <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
            <span className="font-semibold">{health.active_threats}</span>
            <span>Active Alerts</span>
          </div>
        )}
      </div>
    </header>
  );
};
