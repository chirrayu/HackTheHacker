import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'default' | 'cyan' | 'amber' | 'critical';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default',
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'cyan':
        return 'text-cyan-400 border-cyan-500/20 bg-cyan-950/20';
      case 'amber':
        return 'text-amber-400 border-amber-500/20 bg-amber-950/20';
      case 'critical':
        return 'text-red-400 border-red-500/20 bg-red-950/20';
      default:
        return 'text-slate-300 border-slate-800 bg-slate-900/60';
    }
  };

  return (
    <div className={`p-5 rounded-xl border backdrop-blur-sm transition-all duration-200 ${getVariantStyles()}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase font-medium tracking-wider text-slate-400">{title}</span>
        <div className="p-2 rounded-lg bg-slate-800/80 text-current">
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl font-bold tracking-tight text-white">{value}</span>
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};
