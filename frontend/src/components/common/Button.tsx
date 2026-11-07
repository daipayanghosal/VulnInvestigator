import React from 'react';

export type ButtonVariant =
  | 'primary'   // Bold vibrant yellow
  | 'secondary' // Neutral slate/surface
  | 'accent'    // Electric cyan / azure
  | 'danger'    // Punchy coral/rose
  | 'success'   // Bright lime / emerald
  | 'purple'    // Electric violet
  | 'dark'      // Solid dark slate
  | 'ghost';    // Minimal border

export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: React.ReactNode;
  iconRight?: React.ReactNode;
  fullWidth?: boolean;
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  icon,
  iconRight,
  fullWidth = false,
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses =
    'neo-btn inline-flex items-center justify-center font-mono font-bold tracking-tight border-2 border-black dark:border-[#2D3448] transition-all select-none disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none';

  const sizeClasses: Record<ButtonSize, string> = {
    xs: 'px-2 py-0.5 text-[11px] gap-1 neo-shadow-sm',
    sm: 'px-3 py-1.5 text-xs gap-1.5 neo-shadow-sm',
    md: 'px-4 py-2 text-xs sm:text-sm gap-2 neo-shadow',
    lg: 'px-5 py-2.5 text-sm sm:text-base gap-2.5 neo-shadow-lg',
  };

  const variantClasses: Record<ButtonVariant, string> = {
    primary:
      'bg-[#FFE600] text-black hover:bg-[#FFF04D] active:bg-[#FFE600] dark:bg-[#FACC15] dark:text-black dark:hover:bg-[#FDE047]',
    secondary:
      'bg-white dark:bg-[#181D29] text-black dark:text-[#E2E8F0] hover:bg-neutral-100 dark:hover:bg-[#202737] dark:border-[#38415A]',
    accent:
      'bg-[#00F0FF] text-black hover:bg-[#38F4FF] active:bg-[#00F0FF] dark:bg-[#0284C7] dark:text-white dark:hover:bg-[#0369A1] dark:border-[#38BDF8]/60',
    danger:
      'bg-[#FF5376] text-white hover:bg-[#FF6B8B] active:bg-[#FF5376] dark:bg-[#E11D48] dark:hover:bg-[#BE123C] dark:text-white',
    success:
      'bg-[#B8FF00] text-black hover:bg-[#C9FF38] active:bg-[#B8FF00] dark:bg-[#65A30D] dark:text-white dark:hover:bg-[#4D7C0F]',
    purple:
      'bg-[#A78BFA] text-black hover:bg-[#C4B5FD] active:bg-[#A78BFA] dark:bg-[#7C3AED] dark:text-white dark:hover:bg-[#6D28D9]',
    dark:
      'bg-black text-white hover:bg-neutral-800 dark:bg-[#202636] dark:text-white dark:border-[#38415A] dark:hover:bg-[#283044]',
    ghost:
      'bg-transparent text-black dark:text-neutral-300 border-dashed hover:bg-black/5 dark:hover:bg-white/5 neo-shadow-none',
  };

  const widthClass = fullWidth ? 'w-full' : '';

  return (
    <button
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${widthClass} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="inline-block w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        icon && <span className="inline-flex shrink-0">{icon}</span>
      )}
      {children && <span>{children}</span>}
      {!isLoading && iconRight && <span className="inline-flex shrink-0">{iconRight}</span>}
    </button>
  );
};

export default Button;
