import React from 'react';

export type BadgeColor =
  | 'yellow'
  | 'pink'
  | 'cyan'
  | 'lime'
  | 'orange'
  | 'purple'
  | 'zinc'
  | 'white';

export interface BadgeProps {
  children: React.ReactNode;
  color?: BadgeColor;
  variant?: BadgeColor;
  size?: 'xs' | 'sm' | 'md';
  dot?: boolean;
  className?: string;
  onClick?: () => void;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  color,
  variant,
  size = 'sm',
  dot = false,
  className = '',
  onClick,
}) => {
  const activeColor: BadgeColor = variant || color || 'yellow';

  const sizeClasses = {
    xs: 'px-1.5 py-0.2 text-[10px] gap-1',
    sm: 'px-2 py-0.5 text-[11px] gap-1.5',
    md: 'px-2.5 py-1 text-xs gap-1.5',
  };

  const colorClasses: Record<BadgeColor, string> = {
    yellow: 'bg-[#C4A1FF] text-black border-black dark:bg-[#EAB308]/20 dark:text-[#FDE047] dark:border-[#EAB308]/60',
    pink: 'bg-[#FF5376] text-white border-black dark:bg-[#E11D48]/25 dark:text-[#FDA4AF] dark:border-[#FB7185]/60',
    cyan: 'bg-[#00F0FF] text-black border-black dark:bg-[#0284C7]/25 dark:text-[#7DD3FC] dark:border-[#38BDF8]/60',
    lime: 'bg-[#B8FF00] text-black border-black dark:bg-[#65A30D]/25 dark:text-[#BEF264] dark:border-[#A3E635]/60',
    orange: 'bg-[#FB923C] text-black border-black dark:bg-[#EA580C]/25 dark:text-[#FDBA74] dark:border-[#FB923C]/60',
    purple: 'bg-[#A78BFA] text-black border-black dark:bg-[#7C3AED]/25 dark:text-[#DDD6FE] dark:border-[#A78BFA]/60',
    zinc: 'bg-zinc-200 text-zinc-900 border-black dark:bg-[#1E2434] dark:text-zinc-200 dark:border-[#333C52]',
    white: 'bg-white text-black border-black dark:bg-[#1A202E] dark:text-white dark:border-[#333C52]',
  };

  const dotColorClasses: Record<BadgeColor, string> = {
    yellow: 'bg-black dark:bg-[#FDE047]',
    pink: 'bg-white dark:bg-[#FDA4AF]',
    cyan: 'bg-black dark:bg-[#7DD3FC]',
    lime: 'bg-black dark:bg-[#BEF264]',
    orange: 'bg-black dark:bg-[#FDBA74]',
    purple: 'bg-black dark:bg-[#DDD6FE]',
    zinc: 'bg-black dark:bg-zinc-200',
    white: 'bg-black dark:bg-white',
  };

  const Component = onClick ? 'button' : 'span';

  return (
    <Component
      onClick={onClick}
      className={`inline-flex items-center font-mono font-bold uppercase tracking-wider border-2 ${
        onClick ? 'cursor-pointer hover:translate-x-0.5 hover:translate-y-0.5' : ''
      } ${sizeClasses[size]} ${colorClasses[activeColor]} ${className}`}
    >
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-none border border-black/40 dark:border-white/30 ${dotColorClasses[activeColor]}`}
        />
      )}
      {children}
    </Component>
  );
};

export default Badge;
