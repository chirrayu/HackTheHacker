import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth, fetchSensorStatus } from '../services/api';
import { Settings as SettingsIcon, Server, Shield, CheckCircle2, XCircle, HardDrive, Network } from 'lucide-react';

export const Settings: React.FC = () => {
  const { data: health } = useQuery({
    queryKey: ['healthSettings'],
    queryFn: fetchHealth,
  });

  const { data: sensors } = useQuery({
    queryKey: ['sensorsStatus'],
    queryFn: fetchSensorStatus,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">System & Lab Configuration</h2>
        <p className="text-xs text-slate-400 mt-1">
          Review sensor engine status, network adapter parameters, and VirtualBox lab topology.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lab Network Topography */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
          <div className="flex items-center gap-2 text-white font-semibold text-sm">
            <Network className="w-4 h-4 text-cyan-400" />
            <h3>VirtualBox Host-Only Lab Topology</h3>
          </div>

          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-200 block">Windows Monitoring Host</span>
                <span className="text-[11px] text-slate-500">FastAPI Backend, React Dashboard & Sensors</span>
              </div>
              <span className="font-mono text-cyan-400 font-bold">192.168.56.1</span>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-200 block">Kali Linux Attacker VM</span>
                <span className="text-[11px] text-slate-500">Authorized Reconnaissance & Test Traffic</span>
              </div>
              <span className="font-mono text-amber-400 font-bold">192.168.56.20</span>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-200 block">Metasploitable 2 Target VM</span>
                <span className="text-[11px] text-slate-500">Isolated Vulnerable Services (No Default Gateway)</span>
              </div>
              <span className="font-mono text-red-400 font-bold">192.168.56.30</span>
            </div>
          </div>
        </div>

        {/* Sensor & Pipeline Diagnostics */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
          <div className="flex items-center gap-2 text-white font-semibold text-sm">
            <Server className="w-4 h-4 text-cyan-400" />
            <h3>Host Sensor & Engine Health</h3>
          </div>

          <div className="space-y-3 text-xs">
            {/* Database Engine */}
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-200 block">{health?.database.name || 'Database'}</span>
                <span className="text-[11px] text-slate-500">{health?.database.details || 'PostgreSQL Engine'}</span>
              </div>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {health?.database.status || 'Active'}
              </span>
            </div>

            {/* VirtualBox Manager */}
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-200 block">{health?.virtualbox.name || 'VirtualBox'}</span>
                <span className="text-[11px] text-slate-500">{health?.virtualbox.details}</span>
              </div>
              <span
                className={`flex items-center gap-1 font-medium ${
                  health?.virtualbox.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                {health?.virtualbox.status === 'healthy' ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : (
                  <XCircle className="w-3.5 h-3.5" />
                )}
                {health?.virtualbox.status}
              </span>
            </div>

            {/* Packet Capture Tool */}
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-200 block">{health?.capture_tool.name || 'Packet Capture'}</span>
                <span className="text-[11px] text-slate-500">{health?.capture_tool.details}</span>
              </div>
              <span
                className={`flex items-center gap-1 font-medium ${
                  health?.capture_tool.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                {health?.capture_tool.status === 'healthy' ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : (
                  <XCircle className="w-3.5 h-3.5" />
                )}
                {health?.capture_tool.status}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
