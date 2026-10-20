import type { HTMLAttributes } from 'react'
import { cn } from '../../lib/cn'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: 'neutral' | 'success' | 'warning' | 'risk' | 'info'
}

const tones: Record<string, string> = {
  neutral: 'bg-slate-100 text-slate',
  success: 'bg-success/15 text-success',
  warning: 'bg-amber/15 text-amber',
  risk: 'bg-risk/15 text-risk',
  info: 'bg-brand/15 text-brand',
}

export function Badge({ className, tone = 'neutral', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        tones[tone],
        className,
      )}
      {...props}
    />
  )
}

export function riskTone(level: string): BadgeProps['tone'] {
  if (level === 'high') return 'risk'
  if (level === 'medium') return 'warning'
  return 'success'
}
