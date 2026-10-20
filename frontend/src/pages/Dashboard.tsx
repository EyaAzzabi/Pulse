import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Bot,
  CalendarClock,
  Clock,
  Hourglass,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Volume2,
  VolumeX,
  Wallet,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Badge, riskTone } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { useVoice } from '../hooks/useVoice'
import { api } from '../lib/api'
import { cn } from '../lib/cn'
import { formatDate, formatMoney } from '../lib/format'
import type { CashflowPoint, FinancialSummary, OverviewOut, Recommendation } from '../types'

function greeting() {
  const h = new Date().getHours()
  return h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening'
}

const KIND_STYLE: Record<OverviewOut['upcoming'][number]['kind'], { label: string; tone: string; sign: 1 | -1 }> = {
  receivable: { label: 'Customer invoice', tone: 'text-success', sign: 1 },
  recurring_in: { label: 'Recurring income', tone: 'text-success', sign: 1 },
  payable: { label: 'Supplier bill', tone: 'text-risk', sign: -1 },
  recurring: { label: 'Recurring cost', tone: 'text-risk', sign: -1 },
}

export function Dashboard() {
  const { currentOrg, me } = useAuth()
  const orgId = currentOrg?.organization_id
  const voice = useVoice()

  const summaryQuery = useQuery({
    queryKey: ['financial-summary', orgId],
    queryFn: async () => (await api.get<FinancialSummary>(`/financial/summary?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })
  const cashflowQuery = useQuery({
    queryKey: ['cashflow', orgId],
    queryFn: async () =>
      (await api.get<CashflowPoint[]>(`/financial/cashflow?organization_id=${orgId}&history_days=60&horizon_days=60`)).data,
    enabled: !!orgId,
  })
  const overviewQuery = useQuery({
    queryKey: ['overview', orgId],
    queryFn: async () => (await api.get<OverviewOut>(`/financial/overview?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })
  const recommendationsQuery = useQuery({
    queryKey: ['recommendations', orgId],
    queryFn: async () => (await api.get<Recommendation[]>(`/recommendations?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  const summary = summaryQuery.data
  const overview = overviewQuery.data
  const currency = summary?.currency ?? 'EUR'
  const points = cashflowQuery.data ?? []
  const forecast = points.filter((p) => p.is_forecast)
  const shortfall = forecast.find((p) => Number(p.projected_cash) < 0)
  const lowest = forecast.length
    ? forecast.reduce((a, b) => (Number(b.projected_cash) < Number(a.projected_cash) ? b : a))
    : null
  const topPlan = recommendationsQuery.data?.[0]
  const today = new Date().toISOString().slice(0, 10)

  const chartData = points.map((p) => ({
    date: p.date,
    actual: p.actual_cash !== null ? Number(p.actual_cash) : undefined,
    forecast: p.projected_cash !== null ? Number(p.projected_cash) : p.date === today ? Number(p.actual_cash) : undefined,
  }))

  const insightTitle = shortfall
    ? `Cash could run short on ${formatDate(shortfall.date)}`
    : 'No cash shortfall in the next 60 days'
  const insightBody = shortfall && lowest
    ? `The forecast reaches ${formatMoney(lowest.projected_cash ?? 0, currency)} on ${formatDate(lowest.date)}.` +
      (topPlan && Number(topPlan.expected_impact) > 0
        ? ` ${topPlan.title} would lift that low point by ${formatMoney(topPlan.expected_impact, currency)} in simulation.`
        : '')
    : summary?.risk_reasons[0] ?? ''

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4 sm:p-8">
      <div>
        <h1 className="text-2xl font-semibold text-ink sm:text-3xl">
          {greeting()}, {me?.user.full_name?.split(' ')[0]}.
        </h1>
        <p className="mt-1 text-slate">
          Here's the pulse of {currentOrg?.organization_name} on{' '}
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}.
        </p>
      </div>

      {summaryQuery.isLoading && <SkeletonRow />}
      {summaryQuery.isError && <p className="text-risk">Could not load your financial summary.</p>}

      {summary && (
        <>
          <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-dark via-brand-dark to-slate-900 p-6 text-white shadow-xl sm:p-8">
            <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-blue-400/20 blur-3xl" />
            <div className="relative flex flex-wrap items-start justify-between gap-4">
              <div className="max-w-2xl">
                <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-blue-200">
                  <Sparkles className="h-3.5 w-3.5" /> PULSE insight
                </p>
                <h2 className="mt-2 text-2xl font-semibold sm:text-3xl">{insightTitle}</h2>
                <p className="mt-2 text-sm leading-relaxed text-blue-100">{insightBody}</p>
              </div>
              <span
                className={cn(
                  'rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide',
                  summary.risk_level === 'high' ? 'bg-risk text-white' : summary.risk_level === 'medium' ? 'bg-amber text-white' : 'bg-success text-white',
                )}
              >
                {summary.risk_level} risk
              </span>
            </div>
            <div className="relative mt-6 flex flex-wrap gap-3">
              <Link to="/simulator">
                <Button className="bg-white text-brand-dark shadow-none hover:bg-blue-50">
                  Explore rescue strategies <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link to="/copilot">
                <Button variant="secondary" className="border-white/20 bg-white/10 text-white hover:bg-white/20">
                  <Bot className="h-4 w-4" /> Ask the copilot
                </Button>
              </Link>
              {voice.synthSupported && (
                <Button
                  variant="secondary"
                  className="border-white/20 bg-white/10 text-white hover:bg-white/20"
                  onClick={() => (voice.isSpeaking ? voice.stopSpeaking() : voice.speak(`${insightTitle}. ${insightBody}`))}
                >
                  {voice.isSpeaking ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />} Listen
                </Button>
              )}
            </div>
          </section>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard icon={Wallet} tone="bg-blue-50 text-blue-700" label="Current cash" value={formatMoney(summary.current_cash, currency)} hint="Across all recorded transactions, as of today" />
            <KpiCard
              icon={summary.net_cash_flow_30d.startsWith('-') ? TrendingDown : TrendingUp}
              tone={summary.net_cash_flow_30d.startsWith('-') ? 'bg-red-50 text-risk' : 'bg-emerald-50 text-success'}
              label="Net cash flow (30 days)"
              value={formatMoney(summary.net_cash_flow_30d, currency)}
              hint="Money in minus money out over the last 30 days"
            />
            <KpiCard
              icon={Hourglass}
              tone="bg-violet-50 text-violet-700"
              label="Lowest point (60 days)"
              value={lowest ? formatMoney(lowest.projected_cash ?? 0, currency) : '—'}
              sub={lowest ? formatDate(lowest.date) : undefined}
              hint="Lowest projected balance in the deterministic forecast"
            />
            <KpiCard
              icon={AlertTriangle}
              tone="bg-amber-50 text-amber"
              label="Overdue receivables"
              value={formatMoney(summary.overdue_receivables_amount, currency)}
              sub={`${summary.overdue_receivables_count} invoice${summary.overdue_receivables_count === 1 ? '' : 's'}`}
              hint="Customer invoices past their due date"
            />
          </div>

          <Card>
            <CardHeader className="flex flex-wrap items-center justify-between gap-2">
              <CardTitle>Cash position: last 60 days and next 60 days</CardTitle>
              <div className="flex items-center gap-4 text-xs text-slate">
                <span className="flex items-center gap-1.5"><span className="h-0.5 w-4 bg-brand" /> Actual</span>
                <span className="flex items-center gap-1.5"><span className="h-0.5 w-4 border-t-2 border-dashed border-slate" /> Forecast</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData}>
                    <CartesianGrid stroke="#f1f5f9" vertical={false} />
                    <XAxis dataKey="date" tickFormatter={(d) => formatDate(d).replace(/, \d{4}$/, '')} stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} minTickGap={32} />
                    <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} width={72} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
                    <Tooltip
                      labelFormatter={(d) => formatDate(String(d))}
                      formatter={(v, name) => [formatMoney(Number(v), currency), name === 'actual' ? 'Actual' : 'Forecast']}
                      contentStyle={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, boxShadow: '0 8px 24px rgba(15,23,42,0.08)' }}
                      labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                    />
                    <ReferenceLine y={0} stroke="#fca5a5" strokeDasharray="4 4" />
                    <ReferenceLine x={today} stroke="#cbd5e1" label={{ value: 'Today', position: 'insideTopRight', fill: '#64748b', fontSize: 11 }} />
                    <Line type="monotone" dataKey="actual" stroke="#1d4ed8" strokeWidth={2.5} dot={false} connectNulls={false} />
                    <Line type="monotone" dataKey="forecast" stroke="#64748b" strokeWidth={2} strokeDasharray="5 4" dot={false} connectNulls={false} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
            <Card className="lg:col-span-3">
              <CardHeader className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2"><CalendarClock className="h-4 w-4" /> Next 30 days</CardTitle>
                <span className="text-xs text-slate">Scheduled bills, payroll and expected payments</span>
              </CardHeader>
              <CardContent>
                {overview && overview.upcoming.length === 0 && (
                  <p className="py-6 text-center text-sm text-slate">Nothing scheduled in the next 30 days.</p>
                )}
                <ul className="divide-y divide-slate-100">
                  {(overview?.upcoming ?? []).slice(0, 8).map((u, i) => {
                    const style = KIND_STYLE[u.kind]
                    const d = new Date(u.date)
                    return (
                      <li key={`${u.date}-${u.label}-${i}`} className="flex items-center gap-4 py-3">
                        <span className="flex w-12 shrink-0 flex-col items-center rounded-xl bg-slate-50 py-1.5">
                          <span className="text-[10px] font-semibold uppercase text-slate">{d.toLocaleDateString('en-US', { month: 'short' })}</span>
                          <span className="font-display text-lg font-semibold leading-none text-ink">{d.getDate()}</span>
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-sm font-medium text-ink">{u.label}</span>
                          <span className="block text-xs text-slate">{style.label}</span>
                        </span>
                        <span className={cn('flex items-center gap-1 text-sm font-semibold', style.tone)}>
                          {style.sign > 0 ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                          {formatMoney(u.amount, currency)}
                        </span>
                      </li>
                    )
                  })}
                </ul>
              </CardContent>
            </Card>

            <div className="space-y-6 lg:col-span-2">
              <Card>
                <CardHeader className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2"><Clock className="h-4 w-4" /> Overdue by age</CardTitle>
                  <Link to="/invoices" className="text-xs font-medium text-brand hover:underline">Invoices</Link>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(() => {
                    const aging = overview?.aging ?? []
                    const max = Math.max(1, ...aging.map((a) => Number(a.amount)))
                    return aging.map((a) => (
                      <div key={a.bucket}>
                        <div className="mb-1 flex justify-between text-xs">
                          <span className="text-slate">{a.bucket} days · {a.count} invoice{a.count === 1 ? '' : 's'}</span>
                          <span className="font-semibold text-ink">{formatMoney(a.amount, currency)}</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={cn('h-full rounded-full', a.bucket === '0-30' ? 'bg-amber' : 'bg-risk')}
                            style={{ width: `${(Number(a.amount) / max) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))
                  })()}
                </CardContent>
              </Card>

              {overview && (
                <Card>
                  <CardHeader>
                    <CardTitle>What changed vs. the previous 30 days</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-3">
                    <ChangeTile label="Money in" value={overview.changes.inflow} pct={overview.changes.inflow_change_pct} goodWhenUp currency={currency} />
                    <ChangeTile label="Money out" value={overview.changes.outflow} pct={overview.changes.outflow_change_pct} goodWhenUp={false} currency={currency} />
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          <Card>
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Recommended next actions</CardTitle>
              <Link to="/copilot" className="text-xs font-medium text-brand hover:underline">
                Ask the copilot for more <ArrowRight className="inline h-3 w-3" />
              </Link>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-3">
              {recommendationsQuery.isLoading && <p className="text-sm text-slate">Simulating strategies…</p>}
              {(recommendationsQuery.data ?? []).map((rec, i) => (
                <div key={rec.key} className={cn('flex flex-col rounded-2xl border p-4', i === 0 ? 'border-brand/30 bg-brand/5' : 'border-slate-200')}>
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-display text-sm font-semibold text-ink">{rec.title}</p>
                    {i === 0 && <Badge tone="info">Best</Badge>}
                  </div>
                  <p className="mt-1 flex-1 text-xs text-slate">{rec.rationale}</p>
                  <p className="mt-3 text-xs text-slate">Lifts the lowest point by</p>
                  <p className="font-display text-xl font-semibold text-brand">{formatMoney(rec.expected_impact, currency)}</p>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    <Badge tone={riskTone(rec.residual_risk)}>residual risk {rec.residual_risk}</Badge>
                    <Badge tone="neutral">cost {rec.cost}</Badge>
                  </div>
                </div>
              ))}
            </CardContent>
            <p className="px-5 pb-4 text-[11px] text-slate">Simulated outcomes, not guarantees. Every action still needs your approval.</p>
          </Card>
        </>
      )}
    </div>
  )
}

function KpiCard({
  icon: Icon,
  tone,
  label,
  value,
  sub,
  hint,
}: {
  icon: typeof Wallet
  tone: string
  label: string
  value: string
  sub?: string
  hint: string
}) {
  return (
    <Card>
      <CardContent className="pt-5" >
        <div className="flex items-start justify-between">
          <p className="text-xs font-medium text-slate" title={hint}>{label}</p>
          <span className={cn('flex h-9 w-9 items-center justify-center rounded-xl', tone)}>
            <Icon className="h-4 w-4" />
          </span>
        </div>
        <p className="mt-2 font-display text-2xl font-semibold text-ink">{value}</p>
        <p className="text-xs text-slate">{sub ?? hint}</p>
      </CardContent>
    </Card>
  )
}

function ChangeTile({
  label,
  value,
  pct,
  goodWhenUp,
  currency,
}: {
  label: string
  value: string
  pct: string | null
  goodWhenUp: boolean
  currency: string
}) {
  const n = pct === null ? null : Number(pct)
  const good = n === null || n === 0 ? null : goodWhenUp ? n > 0 : n < 0
  return (
    <div className="rounded-xl bg-slate-50 p-3">
      <p className="text-xs text-slate">{label}</p>
      <p className="mt-1 font-display text-lg font-semibold text-ink">{formatMoney(value, currency)}</p>
      <p className={cn('text-xs font-medium', good === null ? 'text-slate' : good ? 'text-success' : 'text-risk')}>
        {n === null ? 'No previous data' : `${n > 0 ? '+' : ''}${n}% vs previous`}
      </p>
    </div>
  )
}

function SkeletonRow() {
  return (
    <div className="space-y-4">
      <div className="h-40 animate-pulse rounded-3xl bg-slate-200/60" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200/60" />
        ))}
      </div>
    </div>
  )
}
