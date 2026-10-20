import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertOctagon, AlertTriangle, Bell, CheckCheck, Info } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { cn } from '../lib/cn'
import { timeAgo } from '../lib/format'
import type { NotificationOut } from '../types'

export const SEVERITY_STYLE = {
  critical: { icon: AlertOctagon, chip: 'bg-risk/10 text-risk', dot: 'bg-risk' },
  warning: { icon: AlertTriangle, chip: 'bg-amber/10 text-amber', dot: 'bg-amber' },
  info: { icon: Info, chip: 'bg-brand/10 text-brand', dot: 'bg-brand' },
} as const

export function useNotificationActions(orgId?: string) {
  const queryClient = useQueryClient()
  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['notifications', orgId] })
    queryClient.invalidateQueries({ queryKey: ['notifications-unread', orgId] })
  }
  const markRead = useMutation({
    mutationFn: async (id: string) => api.patch(`/notifications/${id}?organization_id=${orgId}&read=true`),
    onSuccess: refresh,
  })
  const markAll = useMutation({
    mutationFn: async () => api.post(`/notifications/read-all?organization_id=${orgId}`),
    onSuccess: refresh,
  })
  return { markRead, markAll }
}

export function NotificationBell({ orgId }: { orgId?: string }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const { markRead, markAll } = useNotificationActions(orgId)

  const unread = useQuery({
    queryKey: ['notifications-unread', orgId],
    queryFn: async () => (await api.get<{ unread: number }>(`/notifications/unread-count?organization_id=${orgId}`)).data.unread,
    enabled: !!orgId,
    refetchInterval: 30_000,
  })

  const list = useQuery({
    queryKey: ['notifications', orgId],
    queryFn: async () => (await api.get<NotificationOut[]>(`/notifications?organization_id=${orgId}`)).data,
    enabled: !!orgId && open,
  })

  useEffect(() => {
    if (!open) return
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const count = unread.data ?? 0
  const items = (list.data ?? []).slice(0, 6)

  function openItem(n: NotificationOut) {
    if (!n.read) markRead.mutate(n.id)
    setOpen(false)
    if (n.link) navigate(n.link)
  }

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={count ? `Notifications, ${count} unread` : 'Notifications'}
        aria-expanded={open}
        className="relative flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate shadow-sm transition hover:text-ink"
      >
        <Bell className="h-[18px] w-[18px]" />
        {count > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-risk px-1 text-[10px] font-bold text-white ring-2 ring-white">
            {count > 9 ? '9+' : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-[22rem] max-w-[calc(100vw-2rem)] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <p className="font-display text-sm font-semibold text-ink">
              Notifications {count > 0 && <span className="ml-1 text-xs font-medium text-slate">{count} unread</span>}
            </p>
            {count > 0 && (
              <button
                type="button"
                onClick={() => markAll.mutate()}
                className="flex items-center gap-1 text-xs font-medium text-brand hover:underline"
              >
                <CheckCheck className="h-3.5 w-3.5" /> Mark all read
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto scrollbar-thin">
            {list.isLoading && <p className="px-4 py-6 text-center text-xs text-slate">Loading…</p>}
            {!list.isLoading && items.length === 0 && (
              <div className="px-4 py-8 text-center">
                <Bell className="mx-auto mb-2 h-5 w-5 text-slate" />
                <p className="text-sm text-ink">You're all caught up</p>
                <p className="text-xs text-slate">Risk alerts, approvals and imports show up here.</p>
              </div>
            )}
            {items.map((n) => {
              const style = SEVERITY_STYLE[n.severity] ?? SEVERITY_STYLE.info
              return (
                <button
                  key={n.id}
                  type="button"
                  onClick={() => openItem(n)}
                  className={cn(
                    'flex w-full gap-3 border-b border-slate-50 px-4 py-3 text-left transition hover:bg-slate-50',
                    !n.read && 'bg-brand/[0.03]',
                  )}
                >
                  <span className={cn('flex h-8 w-8 shrink-0 items-center justify-center rounded-full', style.chip)}>
                    <style.icon className="h-4 w-4" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="flex items-start justify-between gap-2">
                      <span className={cn('text-sm', n.read ? 'text-ink/80' : 'font-semibold text-ink')}>{n.title}</span>
                      {!n.read && <span className={cn('mt-1.5 h-2 w-2 shrink-0 rounded-full', style.dot)} />}
                    </span>
                    <span className="mt-0.5 line-clamp-2 block text-xs text-slate">{n.body}</span>
                    <span className="mt-1 block text-[11px] text-slate">{timeAgo(n.created_at)}</span>
                  </span>
                </button>
              )
            })}
          </div>

          <Link
            to="/notifications"
            onClick={() => setOpen(false)}
            className="block border-t border-slate-100 px-4 py-2.5 text-center text-xs font-medium text-brand hover:bg-slate-50"
          >
            View all notifications
          </Link>
        </div>
      )}
    </div>
  )
}
