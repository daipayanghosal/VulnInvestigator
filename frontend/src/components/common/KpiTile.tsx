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
    yellow: 'hover:border-[#C4A1FF] dark:hover:border-[#EAB308]',
    pink: 'hover:border-[#FF5376] dark:hover:border-[#E11D48]',
    cyan: 'hover:border-[#00F0FF] dark:hover:border-[#0284C7]',
    lime: 'hover:border-[#B8FF00] dark:hover:border-[#65A30D]',
    orange: 'hover:border-[#FB923C] dark:hover:border-[#EA580C]',
    purple: 'hover:border-[#A78BFA] dark:hover:border-[#7C3AED]',
    zinc: 'hover:border-zinc-400 dark:hover:border-zinc-500',
  };

  const accentPillColors: Record<KpiAccent, string> = {
    yellow: 'bg-[#C4A1FF] text-black dark:bg-[#FACC15] dark:text-black',
    pink: 'bg-[#FF5376] text-white dark:bg-[#E11D48] dark:text-white',
    cyan: 'bg-[#00F0FF] text-black dark:bg-[#0284C7] dark:text-white',
    lime: 'bg-[#B8FF00] text-black dark:bg-[#65A30D] dark:text-white',
    orange: 'bg-[#FB923C] text-black dark:bg-[#EA580C] dark:text-white',
    purple: 'bg-[#A78BFA] text-black dark:bg-[#7C3AED] dark:text-white',
    zinc: 'bg-zinc-200 text-black dark:bg-[#202636] dark:text-zinc-200',
  };

  return (
    <div
      onClick={onClick}
      className={`border-2 sm:border-[2.5px] border-black dark:border-[#2D3448] bg-white dark:bg-[#141824] p-4 neo-shadow transition-all ${
        onClick ? 'cursor-pointer hover:-translate-y-0.5' : ''
      } ${accentBorderColors[activeAccent]} ${className}`}
    >
      {/* Top row: Label and optional Badge / Icon */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="font-mono text-[10px] sm:text-[11px] font-bold uppercase tracking-wider text-neutral-600 dark:text-neutral-400 line-clamp-1">
          {activeLabel}
        </span>
        {icon && (
          <div className={`p-1 border border-black dark:border-[#2D3448] ${accentPillColors[activeAccent]}`}>
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
            className={`font-mono text-xs font-bold px-1.5 py-0.2 border border-black dark:border-transparent ${
              deltaType === 'positive'
                ? 'bg-[#B8FF00] text-black dark:bg-[#65A30D]/30 dark:text-[#BEF264]'
                : deltaType === 'negative'
                ? 'bg-[#FF5376] text-white dark:bg-[#E11D48]/30 dark:text-[#FDA4AF]'
                : 'bg-zinc-200 text-black dark:bg-[#1E2434] dark:text-zinc-300'
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
              <span className={`px-1.5 py-0.2 border border-black dark:border-transparent text-[10px] ${accentPillColors[activeAccent]}`}>
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
