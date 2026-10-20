import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '../components/ui/Badge'
import { Card, CardContent } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { formatDateTime } from '../lib/format'
import type { NotificationOut } from '../types'

const SEVERITY_TONE = { info: 'info', warning: 'warning', critical: 'risk' } as const

export function Notifications() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id
  const queryClient = useQueryClient()

  const notificationsQuery = useQuery({
    queryKey: ['notifications', orgId],
    queryFn: async () => (await api.get<NotificationOut[]>(`/notifications?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  const markRead = useMutation({
    mutationFn: async (id: string) => (await api.patch(`/notifications/${id}?organization_id=${orgId}&read=true`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications', orgId] }),
  })

  const notifications = notificationsQuery.data ?? []

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Notifications</h1>
        <p className="text-slate">Generated only by real application events. No fabricated "live" alerts.</p>
      </div>

      {notifications.length === 0 && !notificationsQuery.isLoading && (
        <Card>
          <CardContent className="py-10 text-center text-slate">No notifications yet.</CardContent>
        </Card>
      )}

      <div className="space-y-2">
        {notifications.map((n) => (
          <Card
            key={n.id}
            className={!n.read ? 'border-brand/30' : undefined}
            onClick={() => !n.read && markRead.mutate(n.id)}
          >
            <CardContent className="flex cursor-pointer items-start justify-between gap-4 py-4">
              <div>
                <p className="font-medium text-ink">{n.title}</p>
                <p className="text-sm text-slate">{n.body}</p>
                <p className="mt-1 text-xs text-slate">{formatDateTime(n.created_at)}</p>
              </div>
              <Badge tone={SEVERITY_TONE[n.severity] ?? 'neutral'}>{n.severity}</Badge>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
