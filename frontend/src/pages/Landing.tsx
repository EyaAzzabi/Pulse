import { motion } from 'framer-motion'
import {
  AlertTriangle,
  ArrowRight,
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
    <div className="min-h-screen bg-midnight text-ink">
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
                    <p className="text-xs font-medium uppercase tracking-wider text-blue-300">Northstar Studio · demo</p>
                    <p className="text-sm font-medium text-white">90-day cash-flow risk detected</p>
                  </div>
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-2.5 py-1 text-xs text-slate-200">
                    <Volume2 className="h-3 w-3" /> Listen
                  </span>
                </div>
                <div className="px-5 py-4 text-sm leading-relaxed text-slate-200">
                  PULSE detected a potential cash dip around day 18, driven by a scheduled inventory payment
                  landing before three customer invoices are due. Extending supplier terms by 15 days removes
                  the shortfall entirely in simulation.
                </div>
                <div className="grid grid-cols-2 gap-px bg-white/10">
                  <MiniStat label="Current cash" value="€22,520" />
                  <MiniStat label="Lowest projected" value="−€3,128" tone="risk" />
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
                  Extend supplier terms 15d → <span className="font-medium text-brand">+€4,735</span> lowest
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
      </div>

      {/* Problem */}
      <section id="platform" className="mx-auto max-w-7xl px-6 py-16">
        <h2 className="text-center text-sm font-medium uppercase tracking-wider text-brand">The problem</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-2xl font-medium text-ink">
          SMEs rarely have a CFO. Owners find out about a cash shortfall when it has already happened.
        </p>
        <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
          <ProblemCard
            icon={Clock}
            title="Too late to act"
            desc="Spreadsheets show what already happened, not what's coming."
          />
          <ProblemCard
            icon={AlertTriangle}
            title="Hidden risk"
            desc="A single late-paying customer or one large purchase can quietly tip the balance."
          />
          <ProblemCard
            icon={MessageSquareText}
            title="No one to ask"
            desc="Generic chatbots guess. Owners need answers grounded in their real numbers."
          />
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="bg-slate-50 px-6 py-16">
        <div className="mx-auto max-w-7xl">
          <h2 className="mb-10 text-center text-2xl font-semibold text-ink">How Pulse works</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
            <FeatureCard icon={Wallet} title="Understand" desc="A deterministic financial engine computes real liquidity, burn rate and risk from your data." />
            <FeatureCard icon={LineChart} title="Anticipate" desc="A baseline forecast separates known obligations from uncertain day-to-day flow." />
            <FeatureCard icon={Sliders} title="Simulate" desc="The Financial Digital Twin stress-tests decisions without touching real records." />
            <FeatureCard icon={ShieldCheck} title="Act, with approval" desc="Every consequential action is proposed, explained, and only runs after you approve it." />
          </div>
        </div>
      </section>

      {/* Digital Twin */}
      <section id="digital-twin" className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid grid-cols-1 items-center gap-10 sm:grid-cols-2">
          <div>
            <h2 className="text-sm font-medium uppercase tracking-wider text-brand">The Financial Digital Twin</h2>
            <p className="mt-3 text-2xl font-medium text-ink">
              Test a decision before you make it. Nothing here touches your real records.
            </p>
            <p className="mt-4 text-sm text-slate">
              Change a customer's payment delay, add a large purchase, or model financing, and PULSE recomputes a
              full 90-day forecast against the exact same engine that powers your dashboard. Compare the baseline
              and simulated outcome side by side: lowest cash point, runway, and days below zero.
            </p>
            <ul className="mt-5 space-y-2 text-sm text-ink">
              {['Customer & supplier payment delay', 'Revenue and expense shocks', 'One-time purchases or financing', 'Ranked rescue strategies, not guesses'].map((item) => (
                <li key={item} className="flex items-center gap-2">
                  <Check className="h-4 w-4 shrink-0 text-brand" /> {item}
                </li>
              ))}
            </ul>
          </div>
          <Card>
            <CardContent className="p-6">
              <TwinChartPreview />
              <div className="mt-4 flex items-center justify-between text-xs text-slate">
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-slate-300" /> Baseline
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-brand" /> Simulated
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* AI agents */}
      <section id="agents" className="bg-slate-50 px-6 py-16">
        <div className="mx-auto max-w-7xl">
          <h2 className="text-center text-sm font-medium uppercase tracking-wider text-brand">Multi-agent architecture</h2>
          <p className="mx-auto mt-3 max-w-2xl text-center text-2xl font-medium text-ink">
            An orchestrator, not a single giant prompt.
          </p>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-4">
            {AGENTS.map((a) => (
              <Card key={a.title}>
                <CardContent className="p-5">
                  <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10">
                    <Bot className="h-4 w-4 text-brand" />
                  </div>
                  <h3 className="mb-1 text-sm font-medium text-ink">{a.title}</h3>
                  <p className="text-xs text-slate">{a.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-10 rounded-2xl border border-slate-200 bg-white p-6">
            <p className="mb-4 text-xs font-medium uppercase tracking-wider text-slate">Ask PULSE anything</p>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {EXAMPLE_QUESTIONS.map((q) => (
                <div key={q} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-ink">
                  "{q}"
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-slate">
              Every answer is grounded in the deterministic engine, with or without an LLM key configured.
            </p>
          </div>
        </div>
      </section>

      {/* Human-controlled actions */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <h2 className="text-center text-sm font-medium uppercase tracking-wider text-brand">Human-controlled actions</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-2xl font-medium text-ink">
          Propose → Explain → Review → Approve → Execute → Audit.
        </p>
        <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-4">
          {ACTION_STEPS.map((s, i) => (
            <div key={s.label} className="relative">
              <Card>
                <CardContent className="p-5">
                  <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10">
                    <s.icon className="h-4 w-4 text-brand" />
                  </div>
                  <h3 className="mb-1 text-sm font-medium text-ink">
                    {i + 1}. {s.label}
                  </h3>
                  <p className="text-xs text-slate">{s.desc}</p>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="bg-slate-50 px-6 py-16">
        <div className="mx-auto max-w-7xl grid grid-cols-1 gap-6 sm:grid-cols-2">
          <Card>
            <CardContent className="p-6">
              <Bot className="mb-3 h-6 w-6 text-brand" />
              <h3 className="mb-1 text-lg font-medium text-ink">AI Copilot, grounded in your data</h3>
              <p className="text-sm text-slate">
                Ask about your cash runway, risks, or a what-if scenario. Every figure it states comes from the
                deterministic engine. Nothing is invented, with or without an LLM configured.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <TrendingUp className="mb-3 h-6 w-6 text-amber" />
              <h3 className="mb-1 text-lg font-medium text-ink">Honest about uncertainty</h3>
              <p className="text-sm text-slate">
                Forecasts distinguish known scheduled commitments from uncertain estimates, and are never
                presented as guarantees.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Security */}
      <section id="security" className="mx-auto max-w-7xl px-6 py-16">
        <h2 className="mb-6 text-center text-2xl font-semibold text-ink">Security &amp; transparency</h2>
        <p className="mx-auto max-w-2xl text-center text-slate">
          Pulse AI is decision support, not a regulated financial adviser, and never moves real money.
        </p>
        <div className="mx-auto mt-8 grid max-w-3xl grid-cols-1 gap-4 sm:grid-cols-3">
          <SecurityItem icon={Lock} label="Tenant-isolated data, bcrypt-hashed passwords" />
          <SecurityItem icon={ShieldCheck} label="Server-side authorization on every endpoint" />
          <SecurityItem icon={FileCheck2} label="Full audit trail on every approved action" />
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 py-20 text-center">
        <h2 className="text-3xl font-semibold text-ink">Ready to see your business's future?</h2>
        <div className="mt-6">
          <Link to="/signup">
            <Button>
              Start your financial journey <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

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

function TwinChartPreview() {
  const width = 300
  const height = 130
  const padY = 10
  const min = Math.min(...TWIN_BASELINE, ...TWIN_SIMULATED)
  const max = Math.max(...TWIN_BASELINE, ...TWIN_SIMULATED)
  const range = max - min || 1

  const toXY = (value: number, i: number, count: number) => {
    const x = (i / (count - 1)) * width
    const y = height - padY - ((value - min) / range) * (height - padY * 2)
    return [x, y] as const
  }

  const toPath = (values: number[]) =>
    values.map((v, i) => toXY(v, i, values.length)).map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ')

  const simulatedPath = toPath(TWIN_SIMULATED)
  const baselinePath = toPath(TWIN_BASELINE)
  const [lastX] = toXY(0, TWIN_SIMULATED.length - 1, TWIN_SIMULATED.length)
  const [firstX] = toXY(0, 0, TWIN_SIMULATED.length)
  const areaPath = `${simulatedPath} L${lastX.toFixed(1)},${height} L${firstX.toFixed(1)},${height} Z`
  const [, zeroY] = toXY(0, 0, TWIN_SIMULATED.length)

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-40 w-full" preserveAspectRatio="none">
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
