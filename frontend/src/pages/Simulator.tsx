import { useMutation } from '@tanstack/react-query'
import { Sliders } from 'lucide-react'
import { useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { formatDate, formatMoney } from '../lib/format'
import type { SimulationCreateRequest, SimulationResultOut } from '../types'

const DEFAULT_ASSUMPTIONS: SimulationCreateRequest = {
  name: 'My scenario',
  horizon_days: 90,
  customer_payment_delay_days: 0,
  supplier_payment_delay_days: 0,
  revenue_change_pct: 0,
  expense_change_pct: 0,
  inventory_purchase_amount: 0,
  financing_amount: 0,
  financing_monthly_cost: 0,
  one_time_cash_injection: 0,
}

const FIELDS: { key: keyof SimulationCreateRequest; label: string; step: number; suffix?: string }[] = [
  { key: 'customer_payment_delay_days', label: 'Customer payment delay', step: 1, suffix: 'days' },
  { key: 'supplier_payment_delay_days', label: 'Supplier payment delay', step: 1, suffix: 'days' },
  { key: 'revenue_change_pct', label: 'Revenue change', step: 1, suffix: '%' },
  { key: 'expense_change_pct', label: 'Expense change', step: 1, suffix: '%' },
  { key: 'inventory_purchase_amount', label: 'Inventory purchase', step: 100, suffix: '€' },
  { key: 'financing_amount', label: 'Financing amount', step: 500, suffix: '€' },
  { key: 'financing_monthly_cost', label: 'Financing monthly cost', step: 50, suffix: '€' },
  { key: 'one_time_cash_injection', label: 'One-time cash injection', step: 500, suffix: '€' },
]

export function Simulator() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id
  const [assumptions, setAssumptions] = useState<SimulationCreateRequest>(DEFAULT_ASSUMPTIONS)

  const mutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<SimulationResultOut>(`/simulations?organization_id=${orgId}`, assumptions)
      ).data,
  })

  const result = mutation.data

  const chartData = result
    ? result.baseline_points.map((b, i) => ({
        date: formatDate(b.date),
        baseline: Number(b.projected_cash),
        simulated: Number(result.simulated_points[i]?.projected_cash ?? b.projected_cash),
      }))
    : []

  function update(key: keyof SimulationCreateRequest, value: number) {
    setAssumptions((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Financial Digital Twin</h1>
        <p className="text-slate">Stress-test a decision before you make it. Nothing here touches real records.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sliders className="h-4 w-4" /> Scenario assumptions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {FIELDS.map((f) => (
              <div key={f.key}>
                <label className="mb-1 flex justify-between text-xs text-slate">
                  <span>{f.label}</span>
                  <span className="text-ink">
                    {assumptions[f.key]} {f.suffix}
                  </span>
                </label>
                <input
                  type="number"
                  step={f.step}
                  value={assumptions[f.key] as number}
                  onChange={(e) => update(f.key, Number(e.target.value))}
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-ink outline-none focus:border-brand/50"
                />
              </div>
            ))}
            <Button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="w-full">
              {mutation.isPending ? 'Simulating…' : 'Run simulation'}
            </Button>
            {mutation.isError && <p className="text-xs text-risk">Could not run simulation.</p>}
          </CardContent>
        </Card>

        <div className="space-y-6 lg:col-span-2">
          {result && (
            <>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <StatCard label="Lowest cash point" value={formatMoney(result.lowest_cash_point)} />
                <StatCard
                  label="Runway"
                  value={result.runway_days !== null ? `${result.runway_days} days` : 'No shortfall'}
                />
                <StatCard label="Days below zero" value={String(result.days_below_zero)} />
                <StatCard
                  label="Impact vs. baseline"
                  value={formatMoney(result.impact_vs_baseline)}
                  positive={!result.impact_vs_baseline.startsWith('-')}
                />
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Baseline vs. simulated forecast</CardTitle>
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
                        <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                        <Line type="monotone" dataKey="baseline" name="Baseline" stroke="#94a3b8" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="simulated" name="Simulated" stroke="#1d4ed8" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {!result && (
            <Card>
              <CardContent className="py-16 text-center text-slate">
                Adjust assumptions on the left and run a simulation to see baseline vs. simulated outcomes.
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, positive }: { label: string; value: string; positive?: boolean }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <p className="text-xs text-slate">{label}</p>
        <p className={`mt-1 text-lg font-semibold ${positive === undefined ? 'text-ink' : positive ? 'text-success' : 'text-risk'}`}>
          {value}
        </p>
      </CardContent>
    </Card>
  )
}
