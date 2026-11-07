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
    yellow: 'border-t-8 border-t-[#FFE600] dark:border-t-[#EAB308]',
    cyan: 'border-t-8 border-t-[#00F0FF] dark:border-t-[#0284C7]',
    pink: 'border-t-8 border-t-[#FF5376] dark:border-t-[#E11D48]',
    lime: 'border-t-8 border-t-[#B8FF00] dark:border-t-[#65A30D]',
    purple: 'border-t-8 border-t-[#A78BFA] dark:border-t-[#7C3AED]',
    orange: 'border-t-8 border-t-[#FB923C] dark:border-t-[#EA580C]',
    dark: 'border-t-8 border-t-black dark:border-t-[#38415A]',
    zinc: 'border-t-8 border-t-zinc-400 dark:border-t-zinc-600',
  };

  const accentPills: Record<PanelAccent, string> = {
    none: 'bg-black text-white dark:bg-[#202636] dark:text-white',
    yellow: 'bg-[#FFE600] text-black dark:bg-[#FACC15] dark:text-black',
    cyan: 'bg-[#00F0FF] text-black dark:bg-[#0284C7] dark:text-white',
    pink: 'bg-[#FF5376] text-white dark:bg-[#E11D48] dark:text-white',
    lime: 'bg-[#B8FF00] text-black dark:bg-[#65A30D] dark:text-white',
    purple: 'bg-[#A78BFA] text-black dark:bg-[#7C3AED] dark:text-white',
    orange: 'bg-[#FB923C] text-black dark:bg-[#EA580C] dark:text-white',
    dark: 'bg-black text-white dark:bg-[#202636] dark:text-white',
    zinc: 'bg-zinc-300 text-black dark:bg-[#202636] dark:text-zinc-200',
  };

  const hasHeader = Boolean(title || subtitle || icon || badge || actions);

  return (
    <div
      className={`border-2 sm:border-[2.5px] border-black dark:border-[#2D3448] bg-white dark:bg-[#141824] text-black dark:text-[#E2E8F0] ${
        shadowClasses[shadow]
      } ${accentTopBorders[activeAccent]} ${className}`}
    >
      {/* Neobrutalist Header Bar */}
      {hasHeader && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 px-4 sm:px-5 py-3 border-b-2 border-black dark:border-[#2D3448] bg-[#FDFBF7] dark:bg-[#181D2A]">
          <div className="flex items-center space-x-2.5 min-w-0">
            {icon && (
              <div
                className={`p-1.5 border border-black dark:border-[#2D3448] ${accentPills[activeAccent]} shrink-0`}
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
        <div className="px-4 sm:px-5 py-2.5 border-t-2 border-black dark:border-[#2D3448] bg-[#F4F4F5] dark:bg-[#111520] text-xs font-mono">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Panel;
