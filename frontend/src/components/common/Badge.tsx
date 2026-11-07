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
    yellow: 'bg-[#FFE600] text-black border-black dark:border-white',
    pink: 'bg-[#FF5376] text-white border-black dark:border-white',
    cyan: 'bg-[#00F0FF] text-black border-black dark:border-white',
    lime: 'bg-[#B8FF00] text-black border-black dark:border-white',
    orange: 'bg-[#FB923C] text-black border-black dark:border-white',
    purple: 'bg-[#A78BFA] text-black border-black dark:border-white',
    zinc: 'bg-zinc-200 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 border-black dark:border-zinc-500',
    white: 'bg-white dark:bg-black text-black dark:text-white border-black dark:border-white',
  };

  const dotColorClasses: Record<BadgeColor, string> = {
    yellow: 'bg-black',
    pink: 'bg-white',
    cyan: 'bg-black',
    lime: 'bg-black',
    orange: 'bg-black',
    purple: 'bg-black',
    zinc: 'bg-black dark:bg-white',
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
          className={`w-1.5 h-1.5 rounded-none border border-black ${dotColorClasses[activeColor]}`}
        />
      )}
      {children}
    </Component>
  );
};

export default Badge;
