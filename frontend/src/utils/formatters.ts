import { SeverityLevel } from '../types';

export const formatSeverityColor = (severity: SeverityLevel | string): {
  bg: string;
  text: string;
  border: string;
} => {
  switch (severity) {
    case 'Critical':
      return {
        bg: 'bg-red-500/10',
        text: 'text-red-400',
        border: 'border-red-500/30',
      };
    case 'High':
      return {
        bg: 'bg-amber-500/10',
        text: 'text-amber-400',
        border: 'border-amber-500/30',
      };
    case 'Moderate':
      return {
        bg: 'bg-cyan-500/10',
        text: 'text-cyan-400',
        border: 'border-cyan-500/30',
      };
    case 'Low':
    default:
      return {
        bg: 'bg-slate-500/10',
        text: 'text-slate-400',
        border: 'border-slate-500/30',
      };
  }
};

export const formatTimestamp = (isoString?: string): string => {
  if (!isoString) return '--:--:--';
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

export const formatDateTime = (isoString?: string): string => {
  if (!isoString) return 'N/A';
  const d = new Date(isoString);
  return d.toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};
