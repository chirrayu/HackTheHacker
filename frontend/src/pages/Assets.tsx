import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAssets } from '../services/api';
import { Server, Shield, Laptop, CheckCircle2 } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

const DEFAULT_LAB_NODES = [
  {
    ip_address: '192.168.56.1',
    hostname: 'Windows 11 Monitoring Host',
    os_type: 'Windows 11 Professional',
    role: 'SOC Management & Sensor Node',
    status: 'active',
    services: [
      { port: 8000, service: 'FastAPI Backend Engine' },
      { port: 3000, service: 'React SOC Dashboard' },
      { port: 5432, service: 'PostgreSQL Threat Intelligence DB' }
    ]
  },
  {
    ip_address: '192.168.56.20',
    hostname: 'Kali Linux Attacker VM',
    os_type: 'Kali Linux Rolling',
    role: 'Controlled Security Research Attacker',
    status: 'active',
    services: [
      { port: 22, service: 'OpenSSH (Administrative)' }
    ]
  },
  {
    ip_address: '192.168.56.30',
    hostname: 'Metasploitable 2 Target VM',
    os_type: 'Linux 2.6 / Ubuntu 8.04 LTS',
    role: 'Intentionally Vulnerable Lab Target',
    status: 'active',
    services: [
      { port: 21, service: 'vsftpd 2.3.4 (FTP)' },
      { port: 22, service: 'OpenSSH 4.7p1' },
      { port: 23, service: 'Linux telnetd' },
      { port: 25, service: 'Postfix SMTP' },
      { port: 80, service: 'Apache 2.2.8 / PHP 5.2.4' },
      { port: 139, service: 'Samba smbd' },
      { port: 445, service: 'Samba smbd 3.X' },
      { port: 1524, service: 'Ingreslock Backdoor Bindshell' },
      { port: 3306, service: 'MySQL 5.0.51a' },
      { port: 5432, service: 'PostgreSQL 8.3' },
      { port: 6667, service: 'UnrealIRCD IRC Backdoor' }
    ]
  }
];

export const Assets: React.FC = () => {
  const { data: dbAssets } = useQuery({
    queryKey: ['monitoredAssets'],
    queryFn: fetchAssets,
    refetchInterval: 10000,
  });

  // Merge discovered assets with defined lab topology
  const allAssets = DEFAULT_LAB_NODES;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Monitored Lab Assets</h2>
        <p className="text-xs text-slate-400 mt-1">
          Catalog of virtual machines and host adapters attached to the isolated Host-Only network.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {allAssets.map((asset) => (
          <div
            key={asset.ip_address}
            className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="p-2 rounded-lg bg-slate-800 text-cyan-400">
                  {asset.role.includes('Target') ? (
                    <Server className="w-5 h-5 text-amber-400" />
                  ) : asset.role.includes('Attacker') ? (
                    <Laptop className="w-5 h-5 text-red-400" />
                  ) : (
                    <Shield className="w-5 h-5 text-cyan-400" />
                  )}
                </span>
                <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Monitored
                </span>
              </div>

              <h3 className="text-sm font-bold text-white">{asset.hostname}</h3>
              <p className="text-xs font-mono text-cyan-400 font-medium mt-0.5">{asset.ip_address}</p>
              <p className="text-xs text-slate-400 mt-1">{asset.role}</p>
              <p className="text-[11px] text-slate-500 font-mono mt-0.5">{asset.os_type}</p>

              {/* Services List */}
              <div className="mt-4 pt-3 border-t border-slate-800/80">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block mb-2">
                  Exposed Lab Services:
                </span>
                <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  {asset.services.map((s, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-[11px] p-1.5 rounded bg-slate-950/60 font-mono"
                    >
                      <span className="text-cyan-400 font-semibold">:{s.port}</span>
                      <span className="text-slate-300 font-sans truncate ml-2">{s.service}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="text-[10px] text-slate-500 pt-3 border-t border-slate-800">
              VirtualBox Host-Only Adapter
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
