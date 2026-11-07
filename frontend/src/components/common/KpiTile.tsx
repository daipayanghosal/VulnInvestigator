import React from 'react';

export type KpiAccent = 'yellow' | 'pink' | 'cyan' | 'lime' | 'orange' | 'purple' | 'zinc';

export interface KpiTileProps {
  label?: string;
  title?: string;
  value: string | number;
  sublabel?: string;
  subtitle?: string;
  accent?: KpiAccent;
  accentColor?: KpiAccent;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
  onClick?: () => void;
  className?: string;
}

export const KpiTile: React.FC<KpiTileProps> = ({
  label,
  title,
  value,
  sublabel,
  subtitle,
  accent,
  accentColor,
  icon,
  badge,
  delta,
  deltaType = 'neutral',
  onClick,
  className = '',
}) => {
  const activeLabel = title || label || '';
  const activeSublabel = subtitle || sublabel;
  const activeAccent: KpiAccent = accentColor || accent || 'yellow';

  const accentBorderColors: Record<KpiAccent, string> = {
    yellow: 'hover:border-[#FFE600]',
    pink: 'hover:border-[#FF5376]',
    cyan: 'hover:border-[#00F0FF]',
    lime: 'hover:border-[#B8FF00]',
    orange: 'hover:border-[#FB923C]',
    purple: 'hover:border-[#A78BFA]',
    zinc: 'hover:border-zinc-400',
  };

  const accentPillColors: Record<KpiAccent, string> = {
    yellow: 'bg-[#FFE600] text-black',
    pink: 'bg-[#FF5376] text-white',
    cyan: 'bg-[#00F0FF] text-black',
    lime: 'bg-[#B8FF00] text-black',
    orange: 'bg-[#FB923C] text-black',
    purple: 'bg-[#A78BFA] text-black',
    zinc: 'bg-zinc-200 dark:bg-zinc-800 text-black dark:text-white',
  };

  return (
    <div
      onClick={onClick}
      className={`border-2 sm:border-[2.5px] border-black dark:border-white bg-white dark:bg-[#141418] p-4 neo-shadow transition-all ${
        onClick ? 'cursor-pointer hover:-translate-y-0.5' : ''
      } ${accentBorderColors[activeAccent]} ${className}`}
    >
      {/* Top row: Label and optional Badge / Icon */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="font-mono text-[10px] sm:text-[11px] font-bold uppercase tracking-wider text-neutral-600 dark:text-neutral-400 line-clamp-1">
          {activeLabel}
        </span>
        {icon && (
          <div className={`p-1 border border-black dark:border-white ${accentPillColors[activeAccent]}`}>
            {icon}
          </div>
        )}
      </div>

      {/* Main value display */}
      <div className="flex items-baseline space-x-2 my-1">
        <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-black dark:text-white">
          {value}
        </span>

        {delta && (
          <span
            className={`font-mono text-xs font-bold px-1.5 py-0.2 border border-black ${
              deltaType === 'positive'
                ? 'bg-[#B8FF00] text-black'
                : deltaType === 'negative'
                ? 'bg-[#FF5376] text-white'
                : 'bg-zinc-200 text-black'
            }`}
          >
            {delta}
          </span>
        )}
      </div>

      {/* Sublabel or dynamic micro-badge */}
      <div className="mt-2 pt-2 border-t border-black/10 dark:border-white/10 flex items-center justify-between text-[10px] sm:text-[11px] font-mono">
        {activeSublabel && (
          <span className="text-neutral-500 dark:text-neutral-400 font-medium">
            {activeSublabel}
          </span>
        )}

        {badge && (
          <div className="ml-auto shrink-0 font-bold uppercase">
            {typeof badge === 'string' ? (
              <span className={`px-1.5 py-0.2 border border-black text-[10px] ${accentPillColors[activeAccent]}`}>
                {badge}
              </span>
            ) : (
              badge
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default KpiTile;
