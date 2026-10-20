import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Bell, CheckCheck } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SEVERITY_STYLE, useNotificationActions } from '../components/NotificationBell'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { cn } from '../lib/cn'
import { formatDateTime, timeAgo } from '../lib/format'
import type { NotificationOut } from '../types'

const CATEGORY_LABEL: Record<string, string> = {
  liquidity_risk: 'Liquidity risk',
  overdue_invoices: 'Overdue invoices',
  approval_request: 'Approval request',
  workflow_result: 'Workflow result',
  data_import: 'Data import',
}

type Filter = 'all' | 'unread' | 'critical'

export function Notifications() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id
  const navigate = useNavigate()
  const [filter, setFilter] = useState<Filter>('all')
  const { markRead, markAll } = useNotificationActions(orgId)

  const query = useQuery({
    queryKey: ['notifications', orgId],
    queryFn: async () => (await api.get<NotificationOut[]>(`/notifications?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  const all = query.data ?? []
  const unreadCount = all.filter((n) => !n.read).length
  const shown = all.filter((n) => (filter === 'unread' ? !n.read : filter === 'critical' ? n.severity === 'critical' : true))

  function open(n: NotificationOut) {
    if (!n.read) markRead.mutate(n.id)
    if (n.link) navigate(n.link)
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-4 sm:p-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Notifications</h1>
          <p className="text-sm text-slate">Created by real events: risk alerts, approvals, imports and workflow results.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => markAll.mutate()} disabled={!unreadCount || markAll.isPending}>
          <CheckCheck className="h-4 w-4" /> Mark all as read
        </Button>
      </div>

      <div className="flex gap-2">
        {(
          [
            ['all', `All (${all.length})`],
            ['unread', `Unread (${unreadCount})`],
            ['critical', 'Critical'],
          ] as [Filter, string][]
        ).map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setFilter(key)}
            className={cn(
              'rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors',
              filter === key ? 'border-brand bg-brand text-white' : 'border-slate-200 bg-white text-slate hover:text-ink',
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {query.isLoading && <p className="text-sm text-slate">Loading notifications…</p>}

      {!query.isLoading && shown.length === 0 && (
        <Card>
          <div className="px-6 py-12 text-center">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
              <Bell className="h-5 w-5 text-slate" />
            </div>
            <p className="font-medium text-ink">{filter === 'all' ? 'No notifications yet' : 'Nothing here'}</p>
            <p className="mt-1 text-sm text-slate">
              PULSE notifies you when a forecast shows a shortfall, an invoice goes overdue or an action needs approval.
            </p>
          </div>
        </Card>
      )}

      <div className="space-y-2">
        {shown.map((n) => {
          const style = SEVERITY_STYLE[n.severity] ?? SEVERITY_STYLE.info
          return (
            <button
              key={n.id}
              type="button"
              onClick={() => open(n)}
              className={cn(
                'group flex w-full gap-4 rounded-2xl border bg-white p-4 text-left shadow-sm transition hover:border-slate-300',
                n.read ? 'border-slate-200' : 'border-brand/30 ring-1 ring-brand/10',
              )}
            >
              <span className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl', style.chip)}>
                <style.icon className="h-5 w-5" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="flex flex-wrap items-center gap-2">
                  <span className={cn('text-sm', n.read ? 'font-medium text-ink/80' : 'font-semibold text-ink')}>{n.title}</span>
                  {!n.read && <span className={cn('h-2 w-2 rounded-full', style.dot)} />}
                </span>
                <span className="mt-1 block text-sm text-slate">{n.body}</span>
                <span className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate">
                  <span className="rounded-full bg-slate-100 px-2 py-0.5">{CATEGORY_LABEL[n.category] ?? n.category}</span>
                  <span title={formatDateTime(n.created_at)}>{timeAgo(n.created_at)}</span>
                </span>
              </span>
              {n.link && <ArrowRight className="mt-1 h-4 w-4 shrink-0 text-slate opacity-0 transition group-hover:opacity-100" />}
            </button>
          )
        })}
      </div>
    </div>
  )
}
