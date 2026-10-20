import { BarChart3, Briefcase, ChevronDown, LineChart, Mail, ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Area, AreaChart, ResponsiveContainer, Tooltip, YAxis } from 'recharts'
import { cn } from '../lib/cn'
import { formatDate, formatMoney } from '../lib/format'
import type { AgentStep, ChatResponse } from '../types'

const AGENT_STYLE: Record<string, { icon: typeof LineChart; tone: string }> = {
  'Financial Analyst': { icon: BarChart3, tone: 'bg-blue-50 text-blue-700' },
  'Forecast Analyst': { icon: LineChart, tone: 'bg-cyan-50 text-cyan-700' },
  'Strategic Planner': { icon: Briefcase, tone: 'bg-violet-50 text-violet-700' },
  'Workflow Coordinator': { icon: Mail, tone: 'bg-amber-50 text-amber-700' },
  'Risk Guardian': { icon: ShieldCheck, tone: 'bg-emerald-50 text-emerald-700' },
}

export function AgentTrace({ steps, compact = false }: { steps: AgentStep[]; compact?: boolean }) {
  const [open, setOpen] = useState(false)
  if (!steps.length) return null
  const agents = Array.from(new Set(steps.map((s) => s.agent)))

  return (
    <div className="mt-3 border-t border-slate-100 pt-2">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-1.5 text-left text-[11px] font-medium text-slate hover:text-ink"
      >
        <span className="flex -space-x-1">
          {agents.slice(0, 4).map((a) => {
            const style = AGENT_STYLE[a] ?? AGENT_STYLE['Financial Analyst']
            return (
              <span key={a} className={cn('flex h-5 w-5 items-center justify-center rounded-full ring-2 ring-white', style.tone)}>
                <style.icon className="h-2.5 w-2.5" />
              </span>
            )
          })}
        </span>
        <span className="ml-1">
          {compact ? `${agents.length} agent${agents.length > 1 ? 's' : ''}` : `How PULSE answered: ${agents.join(', ')}`}
        </span>
        <ChevronDown className={cn('ml-auto h-3 w-3 transition-transform', open && 'rotate-180')} />
      </button>
      {open && (
        <ol className="mt-2 space-y-1.5">
          {steps.map((s, i) => {
            const style = AGENT_STYLE[s.agent] ?? AGENT_STYLE['Financial Analyst']
            return (
              <li key={i} className="flex items-start gap-2 text-[11px]">
                <span className={cn('flex h-5 w-5 shrink-0 items-center justify-center rounded-full', style.tone)}>
                  <style.icon className="h-2.5 w-2.5" />
                </span>
                <span>
                  <span className="font-semibold text-ink">{s.agent}</span>
                  {s.tool !== 'review' && <code className="ml-1 text-slate">{s.tool}</code>}
                  <span className="block text-slate">{s.summary}</span>
                </span>
              </li>
            )
          })}
        </ol>
      )}
    </div>
  )
}

export function AnswerChart({ points, currency = 'EUR' }: { points: ChatResponse['chart_points']; currency?: string }) {
  if (!points.length) return null
  const data = points.map((p) => ({ date: p.date, cash: Number(p.projected_cash) }))
  const low = Math.min(...data.map((d) => d.cash))
  return (
    <div className="mt-3 h-28 rounded-lg bg-slate-50 p-2">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="answer-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#1d4ed8" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#1d4ed8" stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis hide domain={[Math.min(low, 0), 'auto']} />
          <Tooltip
            contentStyle={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 11 }}
            labelFormatter={(l) => formatDate(String(l))}
            formatter={(v) => [formatMoney(Number(v), currency), 'Projected cash']}
            labelStyle={{ color: '#0f172a' }}
          />
          <Area dataKey="cash" type="monotone" stroke="#1d4ed8" strokeWidth={2} fill="url(#answer-fill)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function ActionCards({ actions }: { actions: ChatResponse['actions'] }) {
  if (!actions.length) return null
  return (
    <div className="mt-3 space-y-2">
      {actions.map((a) => (
        <Link
          key={a.id}
          to="/decisions"
          className="flex items-center justify-between gap-3 rounded-lg border border-amber/30 bg-amber/5 px-3 py-2 text-xs hover:bg-amber/10"
        >
          <span className="text-ink">
            <span className="font-semibold">{a.count} reminder draft{a.count > 1 ? 's' : ''}</span> waiting for your approval
          </span>
          <span className="font-medium text-amber">Review</span>
        </Link>
      ))}
    </div>
  )
}
