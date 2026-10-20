import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { formatDateTime } from '../lib/format'
import type { ActionOut } from '../types'

const STATUS_TONE: Record<string, 'neutral' | 'success' | 'warning' | 'risk' | 'info'> = {
  PENDING_APPROVAL: 'warning',
  APPROVED: 'info',
  QUEUED: 'neutral',
  SENT: 'success',
  FAILED: 'risk',
  CANCELLED: 'neutral',
}

export function Decisions() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id
  const queryClient = useQueryClient()

  const actionsQuery = useQuery({
    queryKey: ['actions', orgId],
    queryFn: async () => (await api.get<ActionOut[]>(`/actions?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  const approveMutation = useMutation({
    mutationFn: async (id: string) => (await api.post(`/actions/${id}/approve?organization_id=${orgId}`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['actions', orgId] }),
  })

  const executeMutation = useMutation({
    mutationFn: async (id: string) => (await api.post(`/actions/${id}/execute?organization_id=${orgId}`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['actions', orgId] }),
  })

  const actions = actionsQuery.data ?? []

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Decision Center</h1>
        <p className="text-slate">Propose → explain → review → approve → execute → audit. Nothing runs silently.</p>
      </div>

      {actions.length === 0 && !actionsQuery.isLoading && (
        <Card>
          <CardContent className="py-10 text-center text-slate">
            No actions proposed yet. Draft an invoice reminder from the Invoices page to see the flow.
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {actions.map((action) => (
          <Card key={action.id}>
            <CardHeader className="flex items-center justify-between">
              <CardTitle className="text-ink">{action.action_type.replace(/_/g, ' ')}</CardTitle>
              <Badge tone={STATUS_TONE[action.status] ?? 'neutral'}>{action.status}</Badge>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-ink">{action.expected_result}</p>
              <p className="text-xs text-slate">Risk: {action.risks}</p>
              <p className="text-xs text-slate">Proposed {formatDateTime(action.created_at)}</p>

              {Array.isArray((action.details as { drafts?: unknown[] })?.drafts) && (
                <details className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate">
                  <summary className="cursor-pointer text-ink">View draft content</summary>
                  <pre className="mt-2 whitespace-pre-wrap text-ink/80">
                    {JSON.stringify((action.details as { drafts?: unknown[] }).drafts, null, 2)}
                  </pre>
                </details>
              )}

              {Object.keys(action.execution_result ?? {}).length > 0 && (
                <p className="text-xs text-slate">
                  Execution result:{' '}
                  <span className="text-ink">{(action.execution_result as { detail?: string }).detail}</span>
                </p>
              )}

              <div className="flex gap-2 pt-1">
                {action.status === 'PENDING_APPROVAL' && (
                  <Button size="sm" onClick={() => approveMutation.mutate(action.id)} disabled={approveMutation.isPending}>
                    Approve
                  </Button>
                )}
                {action.status === 'APPROVED' && (
                  <Button size="sm" onClick={() => executeMutation.mutate(action.id)} disabled={executeMutation.isPending}>
                    Execute
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
