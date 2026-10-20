import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, ArrowRight, Clock, TrendingDown, TrendingUp, Wallet } from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  CartesianGrid,
  Line,
  ComposedChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Badge, riskTone } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { formatDate, formatMoney } from '../lib/format'
import type { CashflowPoint, FinancialSummary, Recommendation } from '../types'

export function Dashboard() {
  const { currentOrg, me } = useAuth()
  const orgId = currentOrg?.organization_id

  const summaryQuery = useQuery({
    queryKey: ['financial-summary', orgId],
    queryFn: async () => (await api.get<FinancialSummary>(`/financial/summary?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  const cashflowQuery = useQuery({
    queryKey: ['cashflow', orgId],
    queryFn: async () =>
      (
        await api.get<CashflowPoint[]>(
          `/financial/cashflow?organization_id=${orgId}&history_days=60&horizon_days=60`,
        )
      ).data,
    enabled: !!orgId,
  })

  const recommendationsQuery = useQuery({
    queryKey: ['recommendations', orgId],
    queryFn: async () => (await api.get<Recommendation[]>(`/recommendations?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  const summary = summaryQuery.data
  const currency = summary?.currency ?? 'EUR'

  const chartData = (cashflowQuery.data ?? []).map((p) => ({
    date: formatDate(p.date),
    actual: p.actual_cash ? Number(p.actual_cash) : undefined,
    forecast: p.projected_cash ? Number(p.projected_cash) : undefined,
  }))

  const shortfall = (cashflowQuery.data ?? []).find((p) => p.is_forecast && Number(p.projected_cash) < 0)

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Good day, {me?.user.full_name?.split(' ')[0]}.</h1>
        <p className="text-slate">Here's your business pulse.</p>
      </div>

      {summaryQuery.isLoading && <p className="text-slate">Loading financial summary…</p>}
      {summaryQuery.isError && <p className="text-risk">Could not load financial summary.</p>}

      {summary && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard
              icon={Wallet}
              label="Current cash"
              value={formatMoney(summary.current_cash, currency)}
            />
            <KpiCard
              icon={summary.net_cash_flow_30d.startsWith('-') ? TrendingDown : TrendingUp}
              label="Net cash flow (30d)"
              value={formatMoney(summary.net_cash_flow_30d, currency)}
            />
            <KpiCard
              icon={Clock}
              label="Cash runway"
              value={summary.cash_runway_days !== null ? `${summary.cash_runway_days} days` : 'Not burning'}
            />
            <KpiCard
              icon={AlertTriangle}
              label="Overdue receivables"
              value={formatMoney(summary.overdue_receivables_amount, currency)}
              sub={`${summary.overdue_receivables_count} invoice(s)`}
            />
          </div>

          <Card>
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Cash flow: actual &amp; forecast</CardTitle>
              <Badge tone={riskTone(summary.risk_level)}>{summary.risk_level} risk</Badge>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData}>
                    <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} minTickGap={24} />
                    <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} width={70} />
                    <Tooltip
                      contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, boxShadow: '0 4px 12px rgba(15,23,42,0.08)' }}
                      labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                      itemStyle={{ color: '#334155' }}
                    />
                    <Line type="monotone" dataKey="actual" name="Actual" stroke="#1d4ed8" strokeWidth={2} dot={false} />
                    <Line
                      type="monotone"
                      dataKey="forecast"
                      name="Forecast"
                      stroke="#64748b"
                      strokeWidth={2}
                      strokeDasharray="5 4"
                      dot={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {shortfall && (
            <Card className="border-amber/30 bg-amber/5">
              <CardContent className="flex items-center justify-between py-5">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-5 w-5 text-amber" />
                  <div>
                    <p className="font-medium text-ink">
                      PULSE detected a potential cash shortfall around {formatDate(shortfall.date)}.
                    </p>
                    <p className="text-sm text-slate">Based on the current 60-day deterministic forecast.</p>
                  </div>
                </div>
                <Link to="/simulator">
                  <Button variant="secondary">
                    Explore rescue strategies <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Why this risk level?</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {summary.risk_reasons.map((reason, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-ink/90">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate" />
                    {reason}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Recommended next actions</CardTitle>
              <Link to="/copilot" className="text-xs text-brand hover:underline">
                Ask the copilot for more <ArrowRight className="inline h-3 w-3" />
              </Link>
            </CardHeader>
            <CardContent className="space-y-3">
              {recommendationsQuery.isLoading && <p className="text-sm text-slate">Computing strategies…</p>}
              {(recommendationsQuery.data ?? []).map((rec) => (
                <div
                  key={rec.key}
                  className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4"
                >
                  <div>
                    <p className="font-medium text-ink">{rec.title}</p>
                    <p className="text-sm text-slate">{rec.rationale}</p>
                    <p className="mt-1 text-xs text-slate">
                      Estimated liquidity benefit:{' '}
                      <span className="text-brand">{formatMoney(rec.expected_impact, currency)}</span> · feasibility{' '}
                      {rec.feasibility} · residual risk {rec.residual_risk}
                    </p>
                  </div>
                  <Badge tone={riskTone(rec.residual_risk)}>approval required</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

function KpiCard({
  icon: Icon,
  label,
  value,
  sub,
}: {
  icon: typeof Wallet
  label: string
  value: string
  sub?: string
}) {
  return (
    <Card>
      <CardContent className="pt-5">
        <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg bg-slate-50">
          <Icon className="h-4 w-4 text-brand" />
        </div>
        <p className="text-xs text-slate">{label}</p>
        <p className="mt-1 text-xl font-semibold text-ink">{value}</p>
        {sub && <p className="text-xs text-slate">{sub}</p>}
      </CardContent>
    </Card>
  )
}
