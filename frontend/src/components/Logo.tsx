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
        className="relative flex shrink-0 items-center justify-center rounded-2xl bg-white p-1 shadow-[0_8px_24px_rgba(29,78,216,0.22)] ring-1 ring-blue-200/70"
        style={{ width: size, height: size }}
      >
        <img src="/logo-icon.png" alt="Pulse AI" className="h-full w-full object-contain" />
      </div>
      {withWordmark && (
        <span className={cn('font-display text-lg font-bold tracking-[-0.04em] text-ink', wordmarkClassName)}>
          PULSE <span className="text-blue-400">AI</span>
        </span>
      )}
    </div>
  )
}
