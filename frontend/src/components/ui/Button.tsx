import type { ButtonHTMLAttributes } from 'react'
import { cn } from '../../lib/cn'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md'
}

const variants: Record<string, string> = {
  primary: 'bg-brand text-white hover:bg-brand/90 shadow-sm shadow-brand/20',
  secondary: 'bg-slate-50 text-ink border border-slate-200 hover:bg-slate-100',
  ghost: 'text-slate hover:text-ink hover:bg-slate-50',
  danger: 'bg-risk/15 text-risk border border-risk/30 hover:bg-risk/25',
}

const sizes: Record<string, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
}

export function Button({ className, variant = 'primary', size = 'md', ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  )
}
