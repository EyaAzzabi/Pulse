import { cn } from '../lib/cn'

interface LogoProps {
  size?: number
  withWordmark?: boolean
  wordmarkClassName?: string
  className?: string
}

export function Logo({ size = 32, withWordmark = false, wordmarkClassName, className }: LogoProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div
        className="flex shrink-0 items-center justify-center rounded-xl bg-white p-1 shadow-sm ring-1 ring-slate-200"
        style={{ width: size, height: size }}
      >
        <img src="/logo-icon.png" alt="Pulse AI" className="h-full w-full object-contain" />
      </div>
      {withWordmark && (
        <span className={cn('font-display text-lg font-semibold tracking-tight text-ink', wordmarkClassName)}>
          Pulse <span className="text-brand">AI</span>
        </span>
      )}
    </div>
  )
}
