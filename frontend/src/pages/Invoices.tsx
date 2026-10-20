import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Mail } from 'lucide-react'
import { useState } from 'react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card, CardContent } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { formatDate, formatMoney } from '../lib/format'
import type { InvoiceOut } from '../types'

const STATUS_TONE: Record<string, 'neutral' | 'success' | 'warning' | 'risk' | 'info'> = {
  paid: 'success',
  unpaid: 'neutral',
  overdue: 'risk',
  partial: 'warning',
}

export function Invoices() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id
  const queryClient = useQueryClient()
  const [directionFilter, setDirectionFilter] = useState<'ALL' | 'RECEIVABLE' | 'PAYABLE'>('ALL')
  const [proposedId, setProposedId] = useState<string | null>(null)

  const invoicesQuery = useQuery({
    queryKey: ['invoices', orgId],
    queryFn: async () => (await api.get<InvoiceOut[]>(`/invoices?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  const proposeMutation = useMutation({
    mutationFn: async (invoiceId: string) =>
      (
        await api.post(`/actions/propose?organization_id=${orgId}`, {
          action_type: 'send_invoice_reminder',
          target: { invoice_ids: [invoiceId] },
        })
      ).data,
    onSuccess: (data) => {
      setProposedId(data.id)
      queryClient.invalidateQueries({ queryKey: ['actions', orgId] })
    },
  })

  const invoices = (invoicesQuery.data ?? []).filter(
    (i) => directionFilter === 'ALL' || i.direction === directionFilter,
  )

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Invoices</h1>
        <p className="text-slate">Receivables and payables. Nothing is sent without your approval.</p>
      </div>

      <div className="flex gap-2">
        {(['ALL', 'RECEIVABLE', 'PAYABLE'] as const).map((d) => (
          <button
            key={d}
            onClick={() => setDirectionFilter(d)}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              directionFilter === d ? 'bg-brand/15 text-brand' : 'text-slate hover:text-ink'
            }`}
          >
            {d === 'ALL' ? 'All' : d === 'RECEIVABLE' ? 'Receivables' : 'Payables'}
          </button>
        ))}
      </div>

      {proposedId && (
        <Card className="border-brand/30 bg-brand/5">
          <CardContent className="py-3 text-sm text-ink">
            Reminder drafted and sent to the Decision Center for approval.{' '}
            <a href="/decisions" className="text-brand hover:underline">
              Review it there
            </a>
            .
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate">
                <th className="px-4 py-3">Counterparty</th>
                <th className="px-4 py-3">Direction</th>
                <th className="px-4 py-3">Amount outstanding</th>
                <th className="px-4 py-3">Due date</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id} className="border-b border-slate-100">
                  <td className="px-4 py-3 text-ink">{inv.counterparty_name}</td>
                  <td className="px-4 py-3 text-slate">{inv.direction}</td>
                  <td className="px-4 py-3 text-ink">
                    {formatMoney(Number(inv.amount) - Number(inv.amount_paid), inv.currency)}
                  </td>
                  <td className="px-4 py-3 text-slate">{formatDate(inv.due_date)}</td>
                  <td className="px-4 py-3">
                    <Badge tone={STATUS_TONE[inv.status] ?? 'neutral'}>{inv.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {inv.direction === 'RECEIVABLE' && inv.status !== 'paid' && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => proposeMutation.mutate(inv.id)}
                        disabled={proposeMutation.isPending}
                      >
                        <Mail className="h-3.5 w-3.5" /> Draft reminder
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
              {invoices.length === 0 && !invoicesQuery.isLoading && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate">
                    No invoices found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
