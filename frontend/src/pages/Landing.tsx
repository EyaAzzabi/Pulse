import { useState } from 'react'
import './Landing.css'
import { motion } from 'framer-motion'
import {
  AlertTriangle,
  ArrowRight,
  ArrowUpRight,
  Activity,
  Bot,
  Check,
  Clock,
  FileCheck2,
  LineChart,
  Lock,
  MessageSquareText,
  ScrollText,
  ShieldCheck,
  Sliders,
  Sparkles,
  TrendingUp,
  Volume2,
  Wallet,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/Button'
import { Card, CardContent } from '../components/ui/Card'
import { Logo } from '../components/Logo'

const NAV_LINKS = [
  { label: 'Platform', href: '#platform' },
  { label: 'Digital Twin', href: '#digital-twin' },
  { label: 'AI agents', href: '#agents' },
  { label: 'Security', href: '#security' },
]

const TRUST_BADGES = [
  'Decimal-safe financial engine',
  'Deterministic forecasting',
  'Human approval on every action',
  'Works with zero LLM key',
]

const EXAMPLE_QUESTIONS = [
  'Will I have enough cash to pay my employees next month?',
  'What happens if my largest customer pays 15 days late?',
  'Can I afford to purchase €8,000 of inventory?',
  'Prepare a reminder email for my three overdue invoices.',
]

const AGENTS = [
  { title: 'Financial Analyst', desc: 'Selects the right data and calls real financial-engine tools to answer your question.' },
  { title: 'Forecast Analyst', desc: 'Explains critical dates, risk drivers and uncertainty in the cash-flow baseline.' },
  { title: 'Strategic Planner', desc: 'Runs simulations for candidate interventions and ranks them by real outcome.' },
  { title: 'Risk Guardian', desc: 'Enforces tool permissions and blocks unsupported claims before you ever see them.' },
]

const STATS = [
  { value: '90', label: 'day forecast horizon, known vs. uncertain' },
  { value: '4', label: 'specialist AI agents behind every answer' },
  { value: '100%', label: 'of consequential actions need human approval' },
  { value: '0', label: 'numbers ever invented by the LLM' },
]

const ACTION_STEPS = [
  { icon: Sparkles, label: 'Propose', desc: 'PULSE drafts a concrete action with evidence.' },
  { icon: ScrollText, label: 'Explain', desc: 'Expected result, risk level and sources shown in full.' },
  { icon: Check, label: 'Approve', desc: 'A human explicitly approves or rejects it, every time.' },
  { icon: FileCheck2, label: 'Audit', desc: 'Execution status and history are permanently recorded.' },
]

export function Landing() {
  return (
    <div className="pulse-landing min-h-screen bg-midnight text-ink">
      {/* Dark hero band, the one deliberately "heavy" section; everything below is light. */}
      <div className="relative overflow-hidden bg-slate-900 text-white">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(29,78,216,0.25),_transparent_60%)]" />

        <header className="relative mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <Logo size={32} withWordmark wordmarkClassName="text-white" />
          <nav className="hidden items-center gap-8 text-sm text-slate-300 sm:flex">
            {NAV_LINKS.map((l) => (
              <a key={l.href} href={l.href} className="hover:text-white">
                {l.label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <Link to="/login" className="text-sm text-slate-300 hover:text-white">
              Sign in
            </Link>
            <Link to="/signup">
              <Button size="sm">Get started</Button>
            </Link>
          </div>
        </header>

        <section className="relative mx-auto max-w-7xl px-6 py-14 sm:py-20">
          <div className="grid grid-cols-1 items-center gap-16 lg:grid-cols-2">
            <div className="text-center lg:text-left">
              <motion.h1
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-4xl font-semibold tracking-tight sm:text-5xl"
              >
                Your business has a <span className="text-blue-400">heartbeat</span>. We help you see where
                it's headed.
              </motion.h1>
              <p className="mx-auto mt-5 max-w-lg text-lg text-slate-300 lg:mx-0">
                PULSE reads your real transactions and invoices, forecasts a 90-day cash position, lets you
                stress-test decisions before you make them, and only acts once you say so.
              </p>

              <div className="mt-6 flex flex-wrap items-center justify-center gap-2 lg:justify-start">
                {TRUST_BADGES.map((b) => (
                  <span
                    key={b}
                    className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs font-medium text-slate-200"
                  >
                    {b}
                  </span>
                ))}
              </div>

              <div className="mt-8 flex items-center justify-center gap-3 lg:justify-start">
                <Link to="/signup">
                  <Button>
                    Start your financial journey <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/login">
                  <Button variant="secondary" className="border-white/15 bg-white/10 text-white hover:bg-white/15">
                    Explore interactive demo
                  </Button>
                </Link>
              </div>
            </div>

            {/* Dynamic hero visual: a grounded explanation card with two floating,
                gently-animating evidence badges: the "moving" composition. */}
            <div className="relative mx-auto w-full max-w-md pb-10 pr-6 pt-6 lg:pb-14 lg:pr-10 lg:pt-10">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-brand-dark to-slate-900 shadow-2xl"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 px-5 py-4">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-blue-300">Northstar Studio</p>
                    <p className="text-sm font-medium text-white">90-day cash-flow risk detected</p>
                  </div>
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-2.5 py-1 text-xs text-slate-200">
                    <Volume2 className="h-3 w-3" /> Listen
                  </span>
                </div>
                <div className="px-5 py-4 text-sm leading-relaxed text-slate-200">
                  PULSE projects cash going below zero on November 7, with three customer invoices already
                  overdue. Extending supplier terms by 15 days removes the shortfall entirely in simulation.
                </div>
                <div className="grid grid-cols-2 gap-px bg-white/10">
                  <MiniStat label="Current cash" value="€7,020" />
                  <MiniStat label="Lowest projected" value="−€2,308" tone="risk" />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1, y: [0, -10, 0] }}
                transition={{
                  opacity: { duration: 0.5, delay: 0.6 },
                  scale: { duration: 0.5, delay: 0.6 },
                  y: { duration: 4.5, repeat: Infinity, ease: 'easeInOut', delay: 1 },
                }}
                className="absolute right-0 top-0 w-48 rounded-xl border border-white/10 bg-white p-3 text-left shadow-xl"
              >
                <div className="flex items-center gap-1.5 text-amber-600">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  <span className="text-[11px] font-semibold uppercase tracking-wide">Medium risk</span>
                </div>
                <p className="mt-1 text-xs text-slate-600">Shortfall projected in 18 days without intervention</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1, y: [0, 10, 0] }}
                transition={{
                  opacity: { duration: 0.5, delay: 0.8 },
                  scale: { duration: 0.5, delay: 0.8 },
                  y: { duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1.2 },
                }}
                className="absolute bottom-0 left-0 w-52 rounded-xl border border-white/10 bg-white p-3 text-left shadow-xl"
              >
                <div className="flex items-center gap-1.5 text-brand">
                  <Check className="h-3.5 w-3.5" />
                  <span className="text-[11px] font-semibold uppercase tracking-wide">Rescue simulated</span>
                </div>
                <p className="mt-1 text-xs text-slate-600">
                  Extend supplier terms 15d → <span className="font-medium text-brand">+€4,372</span> lowest
                  point
                </p>
              </motion.div>
            </div>
          </div>
          <p className="mt-6 text-center text-xs text-slate-400 lg:text-right">
            Illustrative preview from Northstar Studio. The real dashboard computes these numbers live
            from your data, every time.
          </p>
        </section>

        <div className="relative grid grid-cols-2 divide-x divide-white/10 border-t border-white/10 sm:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.label} className="px-4 py-6 text-center sm:px-6">
              <p className="text-2xl font-semibold text-blue-400 sm:text-3xl">{s.value}</p>
              <p className="mt-1 text-xs text-slate-400">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="relative border-t border-white/10 px-6 py-10 sm:py-14">
          <div className="mx-auto grid max-w-7xl items-center gap-8 lg:grid-cols-[1fr_1.1fr]">
            <div>
              <div className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-blue-300">
                <Activity className="h-4 w-4" /> Your next decision, clearer
              </div>
              <h2 className="max-w-xl text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                From scattered numbers to one calm, confident view.
              </h2>
              <p className="mt-3 max-w-lg text-sm leading-6 text-slate-300">
                PULSE turns your everyday financial signals into a simple conversation about what to do next —
                before a risk becomes a crisis.
              </p>
              <a href="#how-it-works" className="mt-5 inline-flex items-center gap-1 text-sm font-semibold text-blue-300 hover:text-white">
                See how it works <ArrowUpRight className="h-4 w-4" />
              </a>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 shadow-2xl backdrop-blur-sm sm:p-5">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Cash position · next 30 days</span>
                <span className="rounded-full bg-emerald-400/10 px-2 py-1 font-medium text-emerald-300">Healthy trend</span>
              </div>
              <div className="mt-5 flex h-28 items-end gap-2 sm:gap-3">
                {[34, 42, 38, 52, 48, 64, 60, 76, 72, 88, 84, 96].map((height, index) => (
                  <div key={index} className="group relative flex h-full flex-1 items-end">
                    <div
                      className="w-full rounded-t-md bg-gradient-to-t from-blue-700 to-cyan-300 opacity-80 transition-all duration-300 group-hover:opacity-100"
                      style={{ height: `${height}%` }}
                    />
                  </div>
                ))}
              </div>
              <div className="mt-3 flex justify-between border-t border-white/10 pt-3 text-[11px] text-slate-500">
                <span>Today</span><span>+15 days</span><span>+30 days</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <main className="landing-story">
        <section id="platform" className="story-section problem-section">
          <div className="section-heading split-heading">
            <div><span className="eyebrow">01 / A clearer perspective</span><h2>Cash surprises.<br /><span>You shouldn't have to.</span></h2></div>
            <p>SMEs rarely have a CFO. Owners often discover a cash shortfall after it happens. PULSE helps you see the signals sooner.</p>
          </div>
          <div className="problem-grid">
            <ProblemCard icon={Clock} title="Too late to act" desc="Spreadsheets show what already happened, not what's coming." />
            <ProblemCard icon={AlertTriangle} title="Hidden risk" desc="A single late-paying customer or one large purchase can quietly tip the balance." />
            <ProblemCard icon={MessageSquareText} title="No one to ask" desc="Owners need answers grounded in their real numbers, with evidence they can inspect." />
          </div>
        </section>

        <section id="how-it-works" className="story-section workflow-section">
          <div className="section-heading"><span className="eyebrow">02 / From insight to action</span><h2>Four steps ahead.<br /><span>Always in your hands.</span></h2><p>A continuous loop of understanding, foresight, and better decisions.</p></div>
          <div className="workflow-grid">
            <FeatureCard icon={Wallet} title="Understand" desc="Real liquidity, burn rate and risk, calculated from your actual financial data." />
            <FeatureCard icon={LineChart} title="Anticipate" desc="A 90-day baseline separates known obligations from uncertain everyday flow." />
            <FeatureCard icon={Sliders} title="Simulate" desc="Stress-test a decision in your Financial Digital Twin before committing." />
            <FeatureCard icon={ShieldCheck} title="Act, with approval" desc="Review the evidence. Approve the action. Keep a complete audit trail." />
          </div>
        </section>

        <section id="digital-twin" className="story-section twin-section">
          <div className="twin-copy"><span className="eyebrow">03 / The Financial Digital Twin</span><h2>One business.<br /><span>More possible futures.</span></h2><p>What if your biggest customer pays late? What if you invest in new inventory? Explore the impact on a full 90-day forecast before you decide.</p>
            <ul>{['Customer & supplier payment delays', 'Revenue and expense shocks', 'One-time purchases or financing', 'Rescue strategies ranked by outcome'].map(item => <li key={item}><Check size={16} />{item}</li>)}</ul>
            <div className="sandbox-note"><Lock size={16} /><span>A safe space to experiment.<br /><strong>Your real records stay untouched.</strong></span></div>
          </div>
          <InteractiveTwin />
        </section>

        <section id="agents" className="story-section agents-section">
          <div className="section-heading"><span className="eyebrow">04 / Specialist intelligence</span><h2>Four specialists.<br /><span>One clear answer.</span></h2><p>An orchestrator connects your question to the right tools, financial evidence, and safeguards.</p></div>
          <div className="orchestrator"><div className="orchestrator-core"><Activity size={25} /><span>PULSE orchestrator</span><span className="live-dot" /></div><span className="connection-label">Your question &rarr; the right expertise</span></div>
          <div className="agent-grid">{AGENTS.map((agent, i) => { const Icon = [Wallet, LineChart, Sliders, ShieldCheck][i]; return <article className="agent-card" key={agent.title}><span className="agent-number">AGENT / 0{i + 1}</span><div className="agent-icon"><Icon size={24} /></div><h3>{agent.title}</h3><p>{agent.desc}</p><span className="agent-capability">{['Analyze the evidence', 'Map the horizon', 'Explore the alternatives', 'Verify the answer'][i]}<ArrowUpRight size={14} /></span></article> })}</div>
          <CopilotPreview />
        </section>

        <section className="story-section approval-section">
          <div><span className="eyebrow">05 / Human-controlled actions</span><h2>Intelligence on your side.<br /><span>Control in your hands.</span></h2><p>Every consequential action starts as a proposal. You see the evidence and expected impact, then decide what happens next.</p><div className="approval-steps">{ACTION_STEPS.map((step, i) => <div key={step.label}><span>0{i+1}</span><step.icon size={18} /><strong>{step.label}</strong><p>{step.desc}</p></div>)}</div></div>
          <div className="approval-preview"><div className="preview-top"><span><FileCheck2 size={16} /> Action proposal</span><span className="pending-badge">Awaiting your review</span></div><div className="proposal-body"><span className="eyebrow">Illustrative workflow</span><h3>A gentle nudge.<br />A healthier cash flow.</h3><p>Prepare payment reminders for three overdue invoices.</p><div className="evidence-row"><Check size={16} />Invoice evidence attached</div><div className="evidence-row"><Check size={16} />Draft and recipients ready for review</div><div className="evidence-row"><Lock size={16} />Nothing sent without your approval</div><Link to="/signup" className="proposal-link">Explore the approval workflow <ArrowRight size={16} /></Link></div><div className="audit-strip"><ShieldCheck size={15} />Propose &rarr; Explain &rarr; Review &rarr; Approve &rarr; Execute &rarr; Audit</div></div>
        </section>

        <section id="features" className="story-section confidence-section"><article><Bot size={25} /><h3>Grounded. Every time.</h3><p>Every figure comes from the deterministic financial engine. Your copilot explains the numbers, with or without an LLM configured.</p></article><article><TrendingUp size={25} /><h3>Clarity includes uncertainty.</h3><p>Known commitments and estimated flows stay distinct. Forecasts support your judgment and are never presented as guarantees.</p><div className="confidence-key"><span>Solid: known commitments</span><span>Dashed: estimated flow</span></div></article></section>

        <section id="security" className="story-section security-section"><div className="security-title"><div className="security-emblem"><ShieldCheck size={32} /></div><span className="eyebrow">Built on trust</span><h2>Your numbers.<br />Your business.</h2><p>PULSE is decision support, not a regulated financial adviser, and never moves real money.</p></div><div className="security-list"><SecurityItem icon={Lock} label="Tenant-isolated data & bcrypt-hashed passwords" /><SecurityItem icon={ShieldCheck} label="Server-side authorization on every endpoint" /><SecurityItem icon={FileCheck2} label="Full audit trail on every approved action" /></div></section>

        <section className="story-section closing-section"><div className="closing-orbit" aria-hidden="true"><Activity /></div><span className="eyebrow">A little foresight changes everything</span><h2>Meet your business's<br /><span>next chapter.</span></h2><p>Understand today. Explore tomorrow. Decide with confidence.</p><Link to="/signup" className="closing-button">Start your financial journey <ArrowUpRight size={19} /></Link><span className="closing-footnote">Real numbers. Clearer decisions. You're in control.</span></section>
      </main>

      <footer className="bg-slate-900 px-6 pb-8 pt-14 text-slate-300">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
            <div className="sm:col-span-2 lg:col-span-1">
              <Logo size={30} withWordmark wordmarkClassName="text-white" />
              <p className="mt-4 max-w-xs text-sm text-slate-400">
                An AI financial copilot for SMEs: a deterministic cash-flow engine, a Digital Twin to simulate
                decisions, and human-approved action on top.
              </p>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Product</p>
              <ul className="mt-4 space-y-2.5 text-sm">
                {NAV_LINKS.map((l) => (
                  <li key={l.href}>
                    <a href={l.href} className="hover:text-white">
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Account</p>
              <ul className="mt-4 space-y-2.5 text-sm">
                <li>
                  <Link to="/login" className="hover:text-white">
                    Sign in
                  </Link>
                </li>
                <li>
                  <Link to="/signup" className="hover:text-white">
                    Get started
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Competition</p>
              <ul className="mt-4 space-y-2.5 text-sm text-slate-400">
                <li>Shenzhen International FinTech Competition 2026</li>
                <li>Topic E: SME Finance Copilot</li>
              </ul>
            </div>
          </div>

          <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-6 text-xs text-slate-500 sm:flex-row">
            <p>© 2026 Pulse AI. Decision support, not a regulated financial adviser.</p>
            <p>Built for FinTechathon, International Track.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function MiniStat({ label, value, tone }: { label: string; value: string; tone?: 'risk' | 'brand' }) {
  return (
    <div className="bg-slate-900 px-4 py-3">
      <p className="text-[11px] text-slate-400">{label}</p>
      <p className={`mt-0.5 text-sm font-semibold ${tone === 'risk' ? 'text-risk' : tone === 'brand' ? 'text-blue-400' : 'text-white'}`}>
        {value}
      </p>
    </div>
  )
}

function ProblemCard({ icon: Icon, title, desc }: { icon: typeof Clock; title: string; desc: string }) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-risk/10">
          <Icon className="h-4 w-4 text-risk" />
        </div>
        <h3 className="mb-1 text-sm font-medium text-ink">{title}</h3>
        <p className="text-xs text-slate">{desc}</p>
      </CardContent>
    </Card>
  )
}

function FeatureCard({ icon: Icon, title, desc }: { icon: typeof Wallet; title: string; desc: string }) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10">
          <Icon className="h-4 w-4 text-brand" />
        </div>
        <h3 className="mb-1 text-sm font-medium text-ink">{title}</h3>
        <p className="text-xs text-slate">{desc}</p>
      </CardContent>
    </Card>
  )
}

const TWIN_BASELINE = [40, 32, 20, 8, -5, -15, -20, -12, 0, 15, 28, 38, 45, 50]
const TWIN_SIMULATED = [40, 35, 28, 22, 18, 15, 18, 25, 35, 45, 52, 58, 62, 65]

function scenarioValues(scenario: number) {
  return TWIN_SIMULATED.map((v, i) => v - (scenario === 1 ? Math.sin(i / 13 * Math.PI) * 40 : scenario === 2 ? (i > 2 ? 25 : 0) : 0))
}

function TwinChartPreview({ scenario = 0 }: { scenario?: number }) {
  const simulated = scenarioValues(scenario)
  const width = 300
  const height = 130
  const padY = 10
  const min = Math.min(...TWIN_BASELINE, ...simulated)
  const max = Math.max(...TWIN_BASELINE, ...simulated)
  const range = max - min || 1

  const toXY = (value: number, i: number, count: number) => {
    const x = (i / (count - 1)) * width
    const y = height - padY - ((value - min) / range) * (height - padY * 2)
    return [x, y] as const
  }

  const toPath = (values: number[]) =>
    values.map((v, i) => toXY(v, i, values.length)).map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ')

  const simulatedPath = toPath(simulated)
  const baselinePath = toPath(TWIN_BASELINE)
  const [lastX] = toXY(0, TWIN_SIMULATED.length - 1, TWIN_SIMULATED.length)
  const [firstX] = toXY(0, 0, TWIN_SIMULATED.length)
  const areaPath = `${simulatedPath} L${lastX.toFixed(1)},${height} L${firstX.toFixed(1)},${height} Z`
  const [, zeroY] = toXY(0, 0, TWIN_SIMULATED.length)

  return (
    <svg role="img" aria-label="Illustrative 90-day baseline and scenario cash forecast" viewBox={`0 0 ${width} ${height}`} className="h-40 w-full" preserveAspectRatio="none">
      <defs>
        <linearGradient id="twin-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1d4ed8" stopOpacity="0.18" />
          <stop offset="100%" stopColor="#1d4ed8" stopOpacity="0" />
        </linearGradient>
      </defs>
      <line x1="0" y1={zeroY} x2={width} y2={zeroY} stroke="#cbd5e1" strokeWidth="1" strokeDasharray="3 3" />
      <path d={areaPath} fill="url(#twin-fill)" stroke="none" />
      <path d={baselinePath} fill="none" stroke="#cbd5e1" strokeWidth="2" />
      <path d={simulatedPath} fill="none" stroke="#1d4ed8" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function SecurityItem({ icon: Icon, label }: { icon: typeof Lock; label: string }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 text-left">
      <Icon className="h-4 w-4 shrink-0 text-brand" />
      <p className="text-xs text-ink">{label}</p>
    </div>
  )
}

function InteractiveTwin() {
  const [scenario, setScenario] = useState(0)
  const values = scenarioValues(scenario)
  const lowestCash = Math.min(...values) * (4735 / 15)
  const daysBelow = Math.round(values.filter(value => value < 0).length / values.length * 90)
  return <div className="twin-console"><div className="preview-top"><span><Activity size={17} /> Scenario studio</span><span className="demo-badge">Interactive illustration</span></div><div className="console-body"><div className="scenario-heading"><span>EXPLORE A WHAT-IF</span><span>90-day horizon</span></div><div className="scenario-tabs" role="group" aria-label="Illustrative scenarios">{['Extend supplier terms', 'Customer pays late', 'Buy inventory'].map((label, i) => <button key={label} type="button" aria-pressed={scenario === i} onClick={() => setScenario(i)}>{label}</button>)}</div><div className="scenario-detail"><Sliders size={16} /><span>{['Supplier payment delayed by 15 days', 'Customer payment delayed by 15 days', 'One-time inventory purchase'][scenario]}</span></div><div className="chart-legend"><span><i />Baseline</span><span><i />Simulated</span></div><div className="twin-chart"><TwinChartPreview scenario={scenario} /></div><div className="chart-axis"><span>Today</span><span>Day 30</span><span>Day 60</span><span>Day 90</span></div><div className="scenario-metrics" aria-live="polite"><div><span>Lowest cash point</span><strong>{new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0, signDisplay: 'always' }).format(lowestCash)}</strong></div><div><span>Days below zero</span><strong>{daysBelow} <small>days</small></strong></div><div><span>Horizon covered</span><strong>90 <small>days</small></strong></div></div></div><p className="console-disclaimer">Illustrative data only. Your dashboard uses the real financial engine.</p></div>
}

function CopilotPreview() {
  const [question, setQuestion] = useState(0)
  const responses = ['PULSE checks your cash position against scheduled payroll and other obligations, then highlights projected gaps and the assumptions behind them.', 'The Digital Twin shifts the payment date and compares the resulting forecast with your baseline, including the lowest cash point and days below zero.', 'PULSE models the purchase against your baseline so you can review its effect on liquidity before making a commitment.', 'PULSE prepares a draft with invoice evidence and recipients for your review. Sending requires your explicit approval.']
  return <div className="copilot-preview"><div className="copilot-intro"><span className="eyebrow">A conversation with your numbers</span><h3>Ask the question<br />on your mind.</h3><p>Choose an example to explore how PULSE approaches it.</p><div className="grounded-badge"><ShieldCheck size={15} /> Engine-grounded answers</div></div><div className="copilot-conversation"><div className="question-options">{EXAMPLE_QUESTIONS.map((q, i) => <button type="button" aria-pressed={question === i} onClick={() => setQuestion(i)} key={q}>{q}<ArrowUpRight size={15} /></button>)}</div><div className="copilot-answer" aria-live="polite"><div className="answer-avatar"><Activity size={18} /></div><div><strong>How PULSE answers</strong><p>{responses[question]}</p><span>Workflow preview / no live financial data</span></div></div></div></div>
}
