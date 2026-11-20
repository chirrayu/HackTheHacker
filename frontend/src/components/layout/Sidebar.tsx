import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldAlert,
  Activity,
  Crosshair,
  Network,
  Server,
  Cpu,
  FileText,
  Settings,
  Radio
} from 'lucide-react';

const navigation = [
  { name: 'SOC Overview', href: '/', icon: Activity },
  { name: 'Live Threat Monitor', href: '/live', icon: Radio },
  { name: 'Attack Analysis', href: '/attacks', icon: Crosshair },
  { name: 'Network Intelligence', href: '/network', icon: Network },
  { name: 'Asset Monitoring', href: '/assets', icon: Server },
  { name: 'Threat Intelligence', href: '/intelligence', icon: Cpu },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Settings & Lab', href: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-wider text-white">HACK THE HACKER</h1>
          <p className="text-[10px] text-cyan-400/80 uppercase font-mono tracking-widest">SOC Platform</p>
        </div>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Lab Network Indicator */}
      <div className="p-4 border-t border-slate-800/80 m-3 rounded-lg bg-slate-900/40">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span>Lab Subnet</span>
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </div>
        <p className="text-xs font-mono font-medium text-slate-200">192.168.56.0/24</p>
        <p className="text-[10px] text-slate-500 mt-1">Host-Only Isolated Lab</p>
      </div>
    </aside>
  );
};
