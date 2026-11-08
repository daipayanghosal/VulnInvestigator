import React from 'react';

export interface TabItem<T extends string> {
  id: T;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
}

export interface TabsProps<T extends string> {
  items: TabItem<T>[];
  activeId: T;
  onChange: (id: T) => void;
  accent?: 'yellow' | 'cyan' | 'pink' | 'lime' | 'purple';
  size?: 'sm' | 'md';
  className?: string;
}

export function Tabs<T extends string>({
  items,
  activeId,
  onChange,
  accent = 'yellow',
  size = 'md',
  className = '',
}: TabsProps<T>) {
  const accentActiveClasses = {
    yellow:
      'bg-[#C4A1FF] text-black shadow-[2px_2px_0px_#000] dark:bg-[#202738] dark:text-[#FACC15] dark:border-[#38425C]',
    cyan:
      'bg-[#00F0FF] text-black shadow-[2px_2px_0px_#000] dark:bg-[#1A2638] dark:text-[#38BDF8] dark:border-[#234E70]',
    pink:
      'bg-[#FF5376] text-white shadow-[2px_2px_0px_#000] dark:bg-[#2E1A24] dark:text-[#FB7185] dark:border-[#6B2135]',
    lime:
      'bg-[#B8FF00] text-black shadow-[2px_2px_0px_#000] dark:bg-[#1F2B18] dark:text-[#A3E635] dark:border-[#3B5A24]',
    purple:
      'bg-[#A78BFA] text-black shadow-[2px_2px_0px_#000] dark:bg-[#251D38] dark:text-[#C4B5FD] dark:border-[#523B7C]',
  };

  const sizeClasses = {
    sm: 'text-xs py-1 px-2.5 gap-1.5',
    md: 'text-xs sm:text-sm py-1.5 px-3.5 gap-2',
  };

  return (
    <div
      className={`inline-flex flex-wrap p-1 border-2 border-black dark:border-[#2D3448] bg-neutral-100 dark:bg-[#121622] gap-1 neo-shadow-sm ${className}`}
    >
      {items.map((item) => {
        const isActive = item.id === activeId;
        return (
          <button
            key={item.id}
            type="button"
            onClick={() => onChange(item.id)}
            className={`neo-btn inline-flex items-center font-mono font-bold tracking-tight select-none border-2 transition-all ${
              sizeClasses[size]
            } ${
              isActive
                ? `border-black ${accentActiveClasses[accent]}`
                : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white hover:border-black/30 dark:hover:border-[#38415A]'
            }`}
          >
            {item.icon && <span className="inline-flex shrink-0">{item.icon}</span>}
            <span>{item.label}</span>
            {item.badge !== undefined && (
              <span
                className={`ml-1 px-1.5 py-0.2 text-[10px] border border-black dark:border-[#2D3448] ${
                  isActive
                    ? 'bg-black text-white dark:bg-[#161B28] dark:text-white'
                    : 'bg-white dark:bg-[#161B28] text-black dark:text-neutral-300'
                }`}
              >
                {item.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export default Tabs;
