import React from 'react';
import { formatSeverityColor } from '../../utils/formatters';
import { SeverityLevel } from '../../types';

interface StatusBadgeProps {
  severity: SeverityLevel | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ severity, size = 'md' }) => {
  const { bg, text, border } = formatSeverityColor(severity);
  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${bg} ${text} ${border} ${px}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current" />
      {severity}
    </span>
  );
};
