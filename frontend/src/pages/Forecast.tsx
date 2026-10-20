import { useMutation, useQuery } from '@tanstack/react-query'
import { PlayCircle } from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { formatDate, formatMoney } from '../lib/format'
import type { ForecastRunOut } from '../types'

export function Forecast() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id

  const latestQuery = useQuery({
    queryKey: ['forecast-latest', orgId],
    queryFn: async () => (await api.get<ForecastRunOut>(`/forecast/latest?organization_id=${orgId}`)).data,
    enabled: !!orgId,
    retry: false,
  })

  const runMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<ForecastRunOut>(`/forecast/run?organization_id=${orgId}`, { horizon_days: 90 })
      ).data,
    onSuccess: () => latestQuery.refetch(),
  })

  const run = runMutation.data ?? latestQuery.data

  const chartData = (run?.points ?? []).map((p) => ({
    date: formatDate(p.date),
    cash: Number(p.projected_cash),
    confidence: p.confidence,
  }))

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Cash-Flow Forecast</h1>
          <p className="text-slate">Deterministic 90-day baseline: known obligations vs. historical average.</p>
        </div>
        <Button onClick={() => runMutation.mutate()} disabled={runMutation.isPending}>
          <PlayCircle className="h-4 w-4" />
          {runMutation.isPending ? 'Running…' : 'Run forecast'}
        </Button>
      </div>

      {!run && !latestQuery.isLoading && (
        <Card>
          <CardContent className="py-10 text-center text-slate">
            No forecast has been run yet. Click "Run forecast" to compute one from your current data.
          </CardContent>
        </Card>
      )}

      {run && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Card>
              <CardContent className="pt-5">
                <p className="text-xs text-slate">Horizon</p>
                <p className="text-xl font-semibold text-ink">{run.horizon_days} days</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-5">
                <p className="text-xs text-slate">Starting cash</p>
                <p className="text-xl font-semibold text-ink">{formatMoney(run.starting_cash)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-5">
                <p className="text-xs text-slate">Shortfall date</p>
                <p className="text-xl font-semibold text-ink">
                  {run.shortfall_date ? formatDate(run.shortfall_date) : 'None detected'}
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Projected cash position</CardTitle>
              <Badge tone="info">method: {run.method}</Badge>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} minTickGap={32} />
                    <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} width={70} />
                    <Tooltip
                      contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, boxShadow: '0 4px 12px rgba(15,23,42,0.08)' }}
                      labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                      itemStyle={{ color: '#334155' }}
                    />
                    <Line type="monotone" dataKey="cash" name="Projected cash" stroke="#64748b" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="mt-3 text-xs text-slate">
                Each day's movement separates a <span className="text-ink">known</span> component (recurring
                obligations and invoice due dates already on record) from an <span className="text-ink">uncertain</span>{' '}
                component (historical average). Confidence degrades the further out the forecast goes.
              </p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
