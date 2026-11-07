import React from 'react';

export type PanelAccent =
  | 'none'
  | 'yellow'
  | 'cyan'
  | 'pink'
  | 'lime'
  | 'purple'
  | 'orange'
  | 'dark'
  | 'zinc';

export interface PanelProps {
  title?: React.ReactNode;
  subtitle?: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  accent?: PanelAccent;
  accentColor?: PanelAccent;
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'yellow' | 'cyan' | 'pink' | 'lime';
  noPadding?: boolean;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}

export const Panel: React.FC<PanelProps> = ({
  title,
  subtitle,
  icon,
  badge,
  actions,
  accent,
  accentColor,
  shadow = 'md',
  noPadding = false,
  children,
  footer,
  className = '',
}) => {
  const activeAccent: PanelAccent = accentColor || accent || 'none';

  const shadowClasses = {
    none: '',
    sm: 'neo-shadow-sm',
    md: 'neo-shadow',
    lg: 'neo-shadow-lg',
    yellow: 'neo-shadow-yellow',
    cyan: 'neo-shadow-cyan',
    pink: 'neo-shadow-pink',
    lime: 'neo-shadow-lime',
  };

  const accentTopBorders: Record<PanelAccent, string> = {
    none: '',
    yellow: 'border-t-8 border-t-[#FFE600]',
    cyan: 'border-t-8 border-t-[#00F0FF]',
    pink: 'border-t-8 border-t-[#FF5376]',
    lime: 'border-t-8 border-t-[#B8FF00]',
    purple: 'border-t-8 border-t-[#A78BFA]',
    orange: 'border-t-8 border-t-[#FB923C]',
    dark: 'border-t-8 border-t-black dark:border-t-white',
    zinc: 'border-t-8 border-t-zinc-400',
  };

  const accentPills: Record<PanelAccent, string> = {
    none: 'bg-black text-white dark:bg-white dark:text-black',
    yellow: 'bg-[#FFE600] text-black',
    cyan: 'bg-[#00F0FF] text-black',
    pink: 'bg-[#FF5376] text-white',
    lime: 'bg-[#B8FF00] text-black',
    purple: 'bg-[#A78BFA] text-black',
    orange: 'bg-[#FB923C] text-black',
    dark: 'bg-black text-white dark:bg-white dark:text-black',
    zinc: 'bg-zinc-300 text-black',
  };

  const hasHeader = Boolean(title || subtitle || icon || badge || actions);

  return (
    <div
      className={`border-2 sm:border-[2.5px] border-black dark:border-white bg-white dark:bg-[#141418] text-black dark:text-neutral-100 ${
        shadowClasses[shadow]
      } ${accentTopBorders[activeAccent]} ${className}`}
    >
      {/* Neobrutalist Header Bar */}
      {hasHeader && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 px-4 sm:px-5 py-3 border-b-2 border-black dark:border-white bg-[#FDFBF7] dark:bg-[#1A1A22]">
          <div className="flex items-center space-x-2.5 min-w-0">
            {icon && (
              <div
                className={`p-1.5 border border-black dark:border-white ${accentPills[activeAccent]} shrink-0`}
              >
                {icon}
              </div>
            )}
            <div className="min-w-0">
              {title && (
                <div className="font-mono font-black text-xs sm:text-sm uppercase tracking-tight text-black dark:text-white flex items-center space-x-2 truncate">
                  <span className="truncate">{title}</span>
                  {badge && <span className="shrink-0">{badge}</span>}
                </div>
              )}
              {subtitle && (
                <p className="text-[11px] font-mono text-neutral-600 dark:text-neutral-400 truncate mt-0.5">
                  {subtitle}
                </p>
              )}
            </div>
          </div>

          {actions && <div className="shrink-0 flex items-center space-x-2">{actions}</div>}
        </div>
      )}

      {/* Main Content Area */}
      <div className={noPadding ? '' : 'p-4 sm:p-5'}>{children}</div>

      {/* Optional Footer Bar */}
      {footer && (
        <div className="px-4 sm:px-5 py-2.5 border-t-2 border-black dark:border-white bg-[#F4F4F5] dark:bg-[#181820] text-xs font-mono">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Panel;
