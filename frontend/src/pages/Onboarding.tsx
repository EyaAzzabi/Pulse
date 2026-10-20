import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Briefcase,
  Building2,
  Calculator,
  Check,
  Coffee,
  Crown,
  Database,
  Eye,
  Factory,
  FileSpreadsheet,
  HandCoins,
  Landmark,
  Loader2,
  Lock,
  Mail,
  PenLine,
  Scissors,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
  Store,
  Target,
  TrendingUp,
  Wallet,
} from 'lucide-react'
import {
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type ClipboardEvent,
  type KeyboardEvent,
  type ReactNode,
} from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Logo } from '../components/Logo'
import { Badge, riskTone } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { cn } from '../lib/cn'
import { formatDate, formatMoney } from '../lib/format'
import type { FinancialSummary, ForecastRunOut } from '../types'
import { Landing } from './Landing'

type Persona = 'owner' | 'finance_manager' | 'accountant' | 'viewer'
type DataSource = 'csv' | 'sample' | 'estimates'
type Icon = typeof Wallet

const STEPS = [
  { label: 'Your account', hint: 'Name, business and login' },
  { label: 'Verify your email', hint: 'One-time code' },
  { label: 'Your role', hint: 'Who you are in the business' },
  { label: 'Business profile', hint: 'Industry, country, size' },
  { label: 'Connect your data', hint: 'Import, sample or estimates' },
  { label: 'Financial snapshot', hint: 'Cash and monthly flows' },
  { label: 'Goals', hint: 'What matters most' },
  { label: 'AI preferences', hint: 'Alerts and tolerance' },
  { label: 'Initialization', hint: 'First forecast and risk read' },
]
const INIT_STEP = STEPS.length - 1
// Steps before this one happen before the account exists.
const FIRST_ACCOUNT_STEP = 2
const STEP = { account: 0, verify: 1, role: 2, business: 3, data: 4, financial: 5, goals: 6, ai: 7 }
const RESEND_SECONDS = 60

const PERSONAS: { key: Persona; title: string; badge: string; icon: Icon; desc: string; perms: string[] }[] = [
  {
    key: 'owner',
    title: 'Owner or founder',
    badge: 'Full control',
    icon: Crown,
    desc: 'I run the business and make the final call on money decisions.',
    perms: ['Approves every consequential action', 'Manages team, settings and integrations', 'Everything the roles below can do'],
  },
  {
    key: 'finance_manager',
    title: 'Finance manager',
    badge: 'Decision level',
    icon: Briefcase,
    desc: 'I own cash planning and decide how to respond to risks.',
    perms: ['Runs forecasts and Digital Twin simulations', 'Proposes and approves invoice reminders', 'Edits the financial profile'],
  },
  {
    key: 'accountant',
    title: 'Accountant',
    badge: 'Operational',
    icon: Calculator,
    desc: 'I keep the books accurate and up to date.',
    perms: ['Imports transactions from CSV', 'Reviews invoices and drafts reminders', 'Cannot approve or execute actions'],
  },
  {
    key: 'viewer',
    title: 'Viewer',
    badge: 'Read only',
    icon: Eye,
    desc: 'I follow the numbers without changing them.',
    perms: ['Dashboards, forecasts and reports', 'Asks the copilot and runs what-if simulations', 'Cannot import data or act on invoices'],
  },
]

const PERSONA_HOME: Record<Persona, string> = {
  owner: '/dashboard',
  finance_manager: '/simulator',
  accountant: '/invoices',
  viewer: '/dashboard',
}

const INDUSTRIES: { key: string; label: string; icon: Icon }[] = [
  { key: 'retail', label: 'Retail', icon: Store },
  { key: 'ecommerce', label: 'E-commerce', icon: ShoppingCart },
  { key: 'hospitality', label: 'Hospitality', icon: Coffee },
  { key: 'services', label: 'Services', icon: Briefcase },
  { key: 'manufacturing', label: 'Manufacturing', icon: Factory },
  { key: 'other', label: 'Other', icon: Building2 },
]
const CURRENCIES = ['EUR', 'USD', 'GBP', 'TND']
const CURRENCY_SYMBOL: Record<string, string> = { EUR: '€', USD: '$', GBP: '£', TND: 'DT' }
const SIZES = ['1-10', '11-50', '51-200', '200+']

const GOALS: { key: string; label: string; desc: string; icon: Icon }[] = [
  { key: 'prevent_shortages', label: 'Prevent cash shortages', desc: 'Early warnings before the balance dips.', icon: ShieldCheck },
  { key: 'improve_collection', label: 'Improve payment collection', desc: 'Chase overdue invoices in the right order.', icon: HandCoins },
  { key: 'control_costs', label: 'Control operating costs', desc: 'See which expenses move the needle.', icon: Scissors },
  { key: 'plan_growth', label: 'Plan business growth', desc: 'Test hires and purchases before committing.', icon: TrendingUp },
  { key: 'explore_financing', label: 'Explore financing', desc: 'Model what a loan would cost month by month.', icon: Landmark },
  { key: 'reduce_uncertainty', label: 'Reduce uncertainty', desc: 'Know which numbers are certain and which are not.', icon: Target },
]

interface FormState {
  persona: Persona
  industry: string
  country: string
  currency: string
  company_size: string
  data_source: DataSource
  sample_loaded: boolean
  monthly_revenue_estimate: string
  monthly_fixed_expenses_estimate: string
  current_cash_balance: string
  customer_payment_delay_days: string
  supplier_payment_delay_days: string
  employee_count: string
  goals: string[]
  alert_sensitivity: 'conservative' | 'balanced' | 'relaxed'
  risk_tolerance: 'conservative' | 'balanced' | 'growth-focused'
  forecast_horizon_days: string
}

const DEFAULT_FORM: FormState = {
  persona: 'owner',
  industry: 'ecommerce',
  country: '',
  currency: 'EUR',
  company_size: '1-10',
  data_source: 'estimates',
  sample_loaded: false,
  monthly_revenue_estimate: '',
  monthly_fixed_expenses_estimate: '',
  current_cash_balance: '',
  customer_payment_delay_days: '30',
  supplier_payment_delay_days: '30',
  employee_count: '',
  goals: [],
  alert_sensitivity: 'balanced',
  risk_tolerance: 'balanced',
  forecast_horizon_days: '90',
}

type Update = <K extends keyof FormState>(key: K, value: FormState[K]) => void

interface CsvResult {
  imported: number
  skipped_duplicates: number
  errors: { row: number; reason: string }[]
}

type TaskStatus = 'pending' | 'running' | 'done' | 'error'
const INIT_TASKS = [
  { key: 'profile', label: 'Saving your business profile' },
  { key: 'cash', label: 'Anchoring your cash position' },
  { key: 'forecast', label: 'Computing your 90-day forecast' },
  { key: 'risk', label: 'Detecting risks' },
] as const

interface AccountState {
  fullName: string
  organizationName: string
  email: string
  password: string
}

export function Onboarding() {
  const { currentOrg, refreshMe, register, isAuthenticated } = useAuth()
  const orgId = currentOrg?.organization_id
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [step, setStep] = useState(0)
  const [account, setAccount] = useState<AccountState>({ fullName: '', organizationName: '', email: '', password: '' })
  const [otp, setOtp] = useState('')
  const [otpDelivery, setOtpDelivery] = useState<'email' | 'server_log' | null>(null)
  const [resendIn, setResendIn] = useState(0)
  const [form, setForm] = useState<FormState>(DEFAULT_FORM)
  const [busy, setBusy] = useState(false)
  const [stepError, setStepError] = useState<string | null>(null)
  const [csvResult, setCsvResult] = useState<CsvResult | null>(null)
  const [taskStatus, setTaskStatus] = useState<Record<string, TaskStatus>>({})
  const [summary, setSummary] = useState<FinancialSummary | null>(null)
  const [forecast, setForecast] = useState<ForecastRunOut | null>(null)
  const initStarted = useRef(false)

  const existingQuery = useQuery({
    queryKey: ['onboarding', orgId],
    queryFn: async () => (await api.get(`/onboarding?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  useEffect(() => {
    const saved = existingQuery.data
    if (!saved) return
    if (saved.completed) {
      navigate('/dashboard', { replace: true })
      return
    }
    if (saved.data && Object.keys(saved.data).length > 0) {
      setForm((prev) => ({ ...prev, ...saved.data }))
      setStep(Math.min(Math.max(saved.current_step - 1, FIRST_ACCOUNT_STEP), INIT_STEP))
    }
  }, [existingQuery.data, navigate])

  // Once signed in, the account steps are done: skip straight past them.
  useEffect(() => {
    if (isAuthenticated && step < FIRST_ACCOUNT_STEP) setStep(FIRST_ACCOUNT_STEP)
  }, [isAuthenticated, step])

  useEffect(() => {
    if (resendIn <= 0) return
    const t = setTimeout(() => setResendIn((s) => s - 1), 1000)
    return () => clearTimeout(t)
  }, [resendIn])

  useEffect(() => {
    if (step === INIT_STEP && !initStarted.current) {
      initStarted.current = true
      runInitialization()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step])

  const update: Update = (key, value) => {
    setStepError(null)
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  function toggleGoal(key: string) {
    setForm((prev) => ({
      ...prev,
      goals: prev.goals.includes(key) ? prev.goals.filter((g) => g !== key) : [...prev.goals, key],
    }))
  }

  function saveProgress(nextStep: number, data: FormState) {
    api.put(`/onboarding?organization_id=${orgId}`, { current_step: nextStep + 1, data }).catch(() => {})
  }

  async function uploadCsv(file: File) {
    setBusy(true)
    setStepError(null)
    try {
      const body = new FormData()
      body.append('file', file)
      const res = await api.post<CsvResult>(`/transactions/import?organization_id=${orgId}`, body)
      setCsvResult(res.data)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setStepError(detail || 'Upload failed. Check the file and try again.')
    } finally {
      setBusy(false)
    }
  }

  function errorDetail(err: unknown): { status?: number; detail?: string } {
    const r = (err as { response?: { status?: number; data?: { detail?: unknown } } })?.response
    return { status: r?.status, detail: typeof r?.data?.detail === 'string' ? r.data.detail : undefined }
  }

  async function sendCode() {
    setBusy(true)
    setStepError(null)
    try {
      const res = await api.post<{ delivery: 'email' | 'server_log' }>('/auth/request-otp', { email: account.email })
      setOtpDelivery(res.data.delivery)
      setResendIn(RESEND_SECONDS)
      setOtp('')
      return true
    } catch (err) {
      const { status, detail } = errorDetail(err)
      setStepError(
        status === 409
          ? 'An account with this email already exists. Sign in instead.'
          : detail || 'Could not send the code. Please try again.',
      )
      return false
    } finally {
      setBusy(false)
    }
  }

  async function goNext() {
    setStepError(null)
    let nextForm = form

    if (step === STEP.account) {
      const { fullName, organizationName, email, password } = account
      if (!fullName.trim() || !organizationName.trim()) {
        setStepError('Enter your name and your business name.')
        return
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setStepError('Enter a valid email address.')
        return
      }
      if (password.length < 8) {
        setStepError('Use a password of at least 8 characters.')
        return
      }
      if (await sendCode()) setStep(STEP.verify)
      return
    }

    if (step === STEP.verify) {
      if (otp.length !== 6) {
        setStepError('Enter the 6-digit code from the email.')
        return
      }
      setBusy(true)
      try {
        await register(account.email, account.password, account.fullName, account.organizationName, otp)
        setStep(STEP.role)
      } catch (err) {
        setStepError(errorDetail(err).detail || 'Could not create your account. Please try again.')
      } finally {
        setBusy(false)
      }
      return
    }

    if (step === STEP.data) {
      if (form.data_source === 'csv' && !(csvResult && csvResult.imported + csvResult.skipped_duplicates > 0)) {
        setStepError('Upload a CSV with at least one valid row, or pick another option.')
        return
      }
      if (form.data_source === 'sample' && !form.sample_loaded) {
        setBusy(true)
        try {
          const res = await api.post(`/onboarding/sample-data?organization_id=${orgId}`)
          const p = res.data.profile
          nextForm = {
            ...form,
            sample_loaded: true,
            monthly_revenue_estimate: String(Math.round(Number(p.monthly_revenue_estimate))),
            monthly_fixed_expenses_estimate: String(Math.round(Number(p.monthly_fixed_expenses_estimate))),
            customer_payment_delay_days: String(p.customer_payment_delay_days),
            supplier_payment_delay_days: String(p.supplier_payment_delay_days),
            employee_count: String(p.employee_count),
          }
        } catch (err: unknown) {
          const status = (err as { response?: { status?: number } })?.response?.status
          if (status === 409) {
            nextForm = { ...form, sample_loaded: true }
          } else {
            setStepError('Could not load the sample data. Please try again.')
            setBusy(false)
            return
          }
        }
        setBusy(false)
        setForm(nextForm)
      }
    }

    if (step === STEP.financial && !form.sample_loaded && form.current_cash_balance === '') {
      setStepError('Your current cash balance is required to anchor the forecast.')
      return
    }

    const next = step + 1
    saveProgress(next, nextForm)
    setStep(next)
  }

  function goBack() {
    setStepError(null)
    if (step === INIT_STEP) {
      initStarted.current = false
      setTaskStatus({})
    }
    if (step > 0 && step !== FIRST_ACCOUNT_STEP) setStep((s) => s - 1)
  }

  async function runTask(key: string, fn: () => Promise<void>) {
    setTaskStatus((prev) => ({ ...prev, [key]: 'running' }))
    await fn()
    setTaskStatus((prev) => ({ ...prev, [key]: 'done' }))
  }

  async function runInitialization() {
    setTaskStatus({})
    setStepError(null)
    try {
      await runTask('profile', async () => {
        await api.patch(`/organizations/${orgId}`, {
          industry: form.industry,
          country: form.country,
          currency: form.currency,
          company_size: form.company_size,
        })
        await api.patch(`/organizations/${orgId}/business-profile`, {
          monthly_revenue_estimate: Number(form.monthly_revenue_estimate || 0),
          monthly_fixed_expenses_estimate: Number(form.monthly_fixed_expenses_estimate || 0),
          customer_payment_delay_days: Number(form.customer_payment_delay_days || 30),
          supplier_payment_delay_days: Number(form.supplier_payment_delay_days || 30),
          employee_count: Number(form.employee_count || 0),
          alert_sensitivity: form.alert_sensitivity,
          risk_tolerance: form.risk_tolerance,
          forecast_horizon_days: Number(form.forecast_horizon_days || 90),
        })
        await api.put(`/onboarding?organization_id=${orgId}`, { current_step: INIT_STEP + 1, data: form })
      })
      await runTask('cash', async () => {
        await api.post(`/onboarding/finalize?organization_id=${orgId}`, {
          current_cash_balance: form.sample_loaded ? null : Number(form.current_cash_balance || 0),
        })
      })
      await runTask('forecast', async () => {
        const res = await api.post<ForecastRunOut>(`/forecast/run?organization_id=${orgId}`, {
          horizon_days: Number(form.forecast_horizon_days || 90),
        })
        setForecast(res.data)
      })
      await runTask('risk', async () => {
        const res = await api.get<FinancialSummary>(`/financial/summary?organization_id=${orgId}`)
        setSummary(res.data)
      })
    } catch {
      setTaskStatus((prev) => {
        const failed = INIT_TASKS.find((t) => prev[t.key] === 'running')
        return failed ? { ...prev, [failed.key]: 'error' } : prev
      })
      setStepError('Something went wrong while setting up. You can retry safely.')
    }
  }

  async function enterApp() {
    setBusy(true)
    try {
      await api.post(`/onboarding/complete?organization_id=${orgId}`)
      queryClient.setQueryData(['onboarding-gate', orgId], { completed: true })
      await refreshMe()
      navigate(PERSONA_HOME[form.persona])
    } catch {
      setStepError('Could not finish onboarding. Please try again.')
      setBusy(false)
    }
  }

  const initDone = INIT_TASKS.every((t) => taskStatus[t.key] === 'done')
  const initRunning = INIT_TASKS.some((t) => taskStatus[t.key] === 'running')
  const initFailed = INIT_TASKS.some((t) => taskStatus[t.key] === 'error')
  const progress = Math.round((step / INIT_STEP) * 100)

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-900">
      <div className="pointer-events-none fixed inset-0 scale-105 blur-[3px]" aria-hidden inert>
        <Landing />
      </div>
      <div className="fixed inset-0 bg-slate-950/60" />

      <div className="relative z-10 flex min-h-screen items-center justify-center p-4">
        <div className="flex max-h-[92vh] w-full max-w-5xl overflow-hidden rounded-3xl bg-white shadow-2xl">
          <aside className="hidden w-72 shrink-0 flex-col bg-gradient-to-b from-brand-dark to-slate-900 p-7 text-white md:flex">
            <div className="flex items-center gap-3">
              <Logo size={40} />
              <div>
                <p className="font-display text-base font-semibold">Create your workspace</p>
                <p className="text-xs text-blue-200">
                  {currentOrg?.organization_name ?? account.organizationName ?? ''}
                </p>
              </div>
            </div>

            <div className="mt-6 h-1 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-blue-400 transition-all duration-500" style={{ width: `${progress}%` }} />
            </div>

            <ol className="mt-6 space-y-1">
              {STEPS.map((s, i) => (
                <li
                  key={s.label}
                  className={cn(
                    'flex items-start gap-3 rounded-xl px-3 py-2',
                    i === step ? 'bg-white/10' : '',
                  )}
                >
                  <span
                    className={cn(
                      'mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold',
                      i < step && 'bg-blue-400 text-slate-900',
                      i === step && 'bg-white text-brand-dark',
                      i > step && 'bg-white/10 text-slate-400',
                    )}
                  >
                    {i < step ? <Check className="h-3.5 w-3.5" /> : i + 1}
                  </span>
                  <div>
                    <p className={cn('text-sm', i === step ? 'font-semibold text-white' : i < step ? 'text-slate-200' : 'text-slate-400')}>
                      {s.label}
                    </p>
                    {i === step && <p className="text-xs text-blue-200">{s.hint}</p>}
                  </div>
                </li>
              ))}
            </ol>

            <div className="mt-auto rounded-xl bg-white/5 p-4 text-xs leading-relaxed text-slate-300">
              <Lock className="mb-2 h-4 w-4 text-blue-300" />
              Your financial data stays private to your organization and is never used to train AI models. You
              can edit every answer later in Settings.
            </div>
          </aside>

          <div className="flex min-w-0 flex-1 flex-col">
            <div className="flex-1 overflow-y-auto scrollbar-thin p-8 sm:p-10">
              <p className="mb-6 text-xs font-medium uppercase tracking-wider text-slate md:hidden">
                Step {step + 1} of {STEPS.length} · {STEPS[step].label}
              </p>
              {step === STEP.account && <AccountStep account={account} setAccount={setAccount} onSubmit={goNext} />}
              {step === STEP.verify && (
                <VerifyStep
                  email={account.email}
                  otp={otp}
                  setOtp={setOtp}
                  delivery={otpDelivery}
                  resendIn={resendIn}
                  onResend={sendCode}
                  onChangeEmail={() => {
                    setStepError(null)
                    setStep(STEP.account)
                  }}
                  onComplete={goNext}
                  busy={busy}
                />
              )}
              {step === STEP.role && (
                <RoleStep persona={form.persona} update={update} orgName={currentOrg?.organization_name} />
              )}
              {step === STEP.business && <BusinessStep form={form} update={update} />}
              {step === STEP.data && (
                <DataStep form={form} update={update} csvResult={csvResult} uploadCsv={uploadCsv} busy={busy} />
              )}
              {step === STEP.financial && <FinancialStep form={form} update={update} />}
              {step === STEP.goals && <GoalsStep goals={form.goals} toggleGoal={toggleGoal} />}
              {step === STEP.ai && <AiStep form={form} update={update} />}
              {step === INIT_STEP && (
                <InitStep
                  taskStatus={taskStatus}
                  summary={summary}
                  forecast={forecast}
                  done={initDone}
                />
              )}

              {stepError && (
                <p className="mt-6 flex items-center gap-2 rounded-lg bg-risk/10 px-3 py-2 text-sm text-risk">
                  <AlertTriangle className="h-4 w-4 shrink-0" /> {stepError}
                </p>
              )}
            </div>

            <div className="flex items-center justify-between border-t border-slate-100 px-8 py-5 sm:px-10">
              {step === STEP.account ? (
                <p className="text-sm text-slate">
                  Already have an account?{' '}
                  <Link to="/login" className="font-medium text-brand hover:underline">
                    Sign in
                  </Link>
                </p>
              ) : (
                <Button
                  variant="secondary"
                  onClick={goBack}
                  disabled={step === FIRST_ACCOUNT_STEP || busy || initRunning}
                >
                  <ArrowLeft className="h-4 w-4" /> Back
                </Button>
              )}

              {step < INIT_STEP && (
                <Button onClick={goNext} disabled={busy}>
                  {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  {step === STEP.account
                    ? 'Send verification code'
                    : step === STEP.verify
                      ? 'Verify and create account'
                      : step === INIT_STEP - 1
                        ? 'Initialize my workspace'
                        : 'Continue'}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              )}

              {step === INIT_STEP && initFailed && (
                <Button
                  onClick={() => {
                    initStarted.current = true
                    runInitialization()
                  }}
                >
                  Retry setup
                </Button>
              )}

              {step === INIT_STEP && initDone && (
                <Button onClick={enterApp} disabled={busy}>
                  {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  Enter my financial command center <ArrowRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StepHeading({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-7">
      <h1 className="text-2xl font-semibold text-ink">{title}</h1>
      <p className="mt-1.5 text-sm text-slate">{subtitle}</p>
    </div>
  )
}

function AccountStep({
  account,
  setAccount,
  onSubmit,
}: {
  account: AccountState
  setAccount: (a: AccountState) => void
  onSubmit: () => void
}) {
  const set = (key: keyof AccountState) => (e: ChangeEvent<HTMLInputElement>) =>
    setAccount({ ...account, [key]: e.target.value })
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand/10">
        <Sparkles className="h-6 w-6 text-brand" />
      </div>
      <StepHeading
        title="Let's understand the business behind the numbers."
        subtitle="Create your account first. The next steps take about two minutes and build your first forecast and risk read."
      />
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <label className="block">
          <Label>Full name</Label>
          <input value={account.fullName} onChange={set('fullName')} autoComplete="name" className={inputClass} />
        </label>
        <label className="block">
          <Label>Business name</Label>
          <input
            value={account.organizationName}
            onChange={set('organizationName')}
            autoComplete="organization"
            className={inputClass}
          />
        </label>
        <label className="block">
          <Label>Work email</Label>
          <input type="email" value={account.email} onChange={set('email')} autoComplete="email" className={inputClass} />
        </label>
        <label className="block">
          <Label>Password</Label>
          <input
            type="password"
            value={account.password}
            onChange={set('password')}
            autoComplete="new-password"
            placeholder="At least 8 characters"
            className={inputClass}
          />
        </label>
      </div>
      <p className="mt-4 text-xs text-slate">We'll email you a 6-digit code to confirm the address belongs to you.</p>
      <button type="submit" className="hidden" />
    </form>
  )
}

function VerifyStep({
  email,
  otp,
  setOtp,
  delivery,
  resendIn,
  onResend,
  onChangeEmail,
  onComplete,
  busy,
}: {
  email: string
  otp: string
  setOtp: (v: string) => void
  delivery: 'email' | 'server_log' | null
  resendIn: number
  onResend: () => void
  onChangeEmail: () => void
  onComplete: () => void
  busy: boolean
}) {
  const refs = useRef<(HTMLInputElement | null)[]>([])
  const digits = Array.from({ length: 6 }, (_, i) => otp[i] ?? '')

  useEffect(() => {
    refs.current[0]?.focus()
  }, [])

  function setDigit(i: number, value: string) {
    const d = value.replace(/\D/g, '').slice(-1)
    const next = digits.slice()
    next[i] = d
    const joined = next.join('').slice(0, 6)
    setOtp(joined)
    if (d && i < 5) refs.current[i + 1]?.focus()
  }

  function onKeyDown(i: number, e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Backspace' && !digits[i] && i > 0) refs.current[i - 1]?.focus()
    if (e.key === 'Enter' && otp.length === 6) onComplete()
  }

  function onPaste(e: ClipboardEvent<HTMLInputElement>) {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    if (!pasted) return
    e.preventDefault()
    setOtp(pasted)
    refs.current[Math.min(pasted.length, 5)]?.focus()
  }

  return (
    <div>
      <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand/10">
        <Mail className="h-6 w-6 text-brand" />
      </div>
      <StepHeading title="Check your inbox" subtitle={`We sent a 6-digit code to ${email}. It expires in 10 minutes.`} />

      <div className="flex gap-2 sm:gap-3">
        {digits.map((d, i) => (
          <input
            key={i}
            ref={(el) => {
              refs.current[i] = el
            }}
            value={d}
            onChange={(e) => setDigit(i, e.target.value)}
            onKeyDown={(e) => onKeyDown(i, e)}
            onPaste={onPaste}
            inputMode="numeric"
            autoComplete={i === 0 ? 'one-time-code' : 'off'}
            maxLength={1}
            aria-label={`Digit ${i + 1}`}
            className="h-14 w-12 rounded-xl border-2 border-slate-200 text-center font-display text-2xl font-semibold text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/15 sm:w-14"
          />
        ))}
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
        <button
          type="button"
          onClick={onResend}
          disabled={resendIn > 0 || busy}
          className="font-medium text-brand hover:underline disabled:cursor-not-allowed disabled:text-slate disabled:no-underline"
        >
          {resendIn > 0 ? `Resend code in ${resendIn}s` : 'Resend code'}
        </button>
        <button type="button" onClick={onChangeEmail} className="text-slate hover:text-ink">
          Use a different email
        </button>
      </div>

      {delivery === 'server_log' && (
        <p className="mt-5 rounded-xl bg-amber/10 px-4 py-3 text-xs text-amber">
          Email delivery isn't configured on this server yet, so the code was written to the backend console
          instead of being emailed.
        </p>
      )}
    </div>
  )
}

function RoleStep({ persona, update, orgName }: { persona: Persona; update: Update; orgName?: string }) {
  return (
    <div>
      <StepHeading
        title="Your role in the business"
        subtitle="Each role in PULSE has its own permissions, enforced on every request. Pick the one that describes you best."
      />
      <div className="relative space-y-3">
        <div className="absolute bottom-6 left-[2.15rem] top-6 w-px bg-slate-200" />
        {PERSONAS.map((p) => {
          const selected = persona === p.key
          return (
            <button
              key={p.key}
              type="button"
              onClick={() => update('persona', p.key)}
              className={cn(
                'relative flex w-full gap-4 rounded-2xl border-2 p-4 text-left transition-colors',
                selected ? 'border-brand bg-brand/5' : 'border-slate-200 bg-white hover:border-slate-300',
              )}
            >
              <span
                className={cn(
                  'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl',
                  selected ? 'bg-brand text-white' : 'bg-slate-100 text-slate',
                )}
              >
                <p.icon className="h-5 w-5" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="flex flex-wrap items-center gap-2">
                  <span className="font-display text-base font-semibold text-ink">{p.title}</span>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate">{p.badge}</span>
                </span>
                <span className="mt-0.5 block text-sm text-slate">{p.desc}</span>
                <span className="mt-2 grid grid-cols-1 gap-x-4 gap-y-1 sm:grid-cols-3">
                  {p.perms.map((perm) => (
                    <span key={perm} className="flex items-start gap-1.5 text-xs text-ink/80">
                      <Check className={cn('mt-0.5 h-3 w-3 shrink-0', selected ? 'text-brand' : 'text-slate')} />
                      {perm}
                    </span>
                  ))}
                </span>
              </span>
            </button>
          )
        })}
      </div>
      <p className="mt-4 text-xs text-slate">
        You created {orgName ?? 'this organization'}, so you stay its owner either way. Your choice tailors your
        workspace, and these roles are what teammates get when you invite them.
      </p>
    </div>
  )
}

function BusinessStep({ form, update }: { form: FormState; update: Update }) {
  return (
    <div>
      <StepHeading title="Business profile" subtitle="Sets the currency, formatting and context PULSE uses everywhere." />

      <Label>Industry</Label>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {INDUSTRIES.map((ind) => (
          <SelectCard key={ind.key} selected={form.industry === ind.key} onClick={() => update('industry', ind.key)}>
            <ind.icon className={cn('h-5 w-5', form.industry === ind.key ? 'text-brand' : 'text-slate')} />
            <span className="text-sm font-medium text-ink">{ind.label}</span>
          </SelectCard>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <Label>Country</Label>
          <input
            value={form.country}
            onChange={(e) => update('country', e.target.value)}
            placeholder="e.g. France"
            className={inputClass}
          />
        </div>
        <div>
          <Label>Currency</Label>
          <div className="flex flex-wrap gap-2">
            {CURRENCIES.map((c) => (
              <Chip key={c} active={form.currency === c} onClick={() => update('currency', c)}>
                {CURRENCY_SYMBOL[c]} {c}
              </Chip>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6">
        <Label>Company size</Label>
        <div className="flex flex-wrap gap-2">
          {SIZES.map((s) => (
            <Chip key={s} active={form.company_size === s} onClick={() => update('company_size', s)}>
              {s} employees
            </Chip>
          ))}
        </div>
      </div>
    </div>
  )
}

function DataStep({
  form,
  update,
  csvResult,
  uploadCsv,
  busy,
}: {
  form: FormState
  update: Update
  csvResult: CsvResult | null
  uploadCsv: (file: File) => void
  busy: boolean
}) {
  const options: { key: DataSource; icon: Icon; title: string; desc: string }[] = [
    { key: 'csv', icon: FileSpreadsheet, title: 'Upload a CSV', desc: 'Import your transaction history from a bank or accounting export.' },
    { key: 'sample', icon: Database, title: 'Use Northstar Studio data', desc: 'Six months of transactions and invoices to explore every feature right away.' },
    { key: 'estimates', icon: PenLine, title: 'Start from my estimates', desc: 'Use the numbers you give in the next step and import history later.' },
  ]
  const disabled = form.sample_loaded

  return (
    <div>
      <StepHeading title="Connect your data" subtitle="The more history PULSE has, the sharper the forecast. You can add more anytime." />
      <div className="space-y-3">
        {options.map((o) => {
          const selected = form.data_source === o.key
          return (
            <button
              key={o.key}
              type="button"
              disabled={disabled && o.key !== 'sample'}
              onClick={() => update('data_source', o.key)}
              className={cn(
                'flex w-full items-start gap-4 rounded-2xl border-2 p-4 text-left transition-colors disabled:cursor-not-allowed disabled:opacity-50',
                selected ? 'border-brand bg-brand/5' : 'border-slate-200 hover:border-slate-300',
              )}
            >
              <span className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl', selected ? 'bg-brand text-white' : 'bg-slate-100 text-slate')}>
                <o.icon className="h-5 w-5" />
              </span>
              <span>
                <span className="block font-display text-base font-semibold text-ink">{o.title}</span>
                <span className="block text-sm text-slate">{o.desc}</span>
              </span>
            </button>
          )
        })}
      </div>

      {form.data_source === 'csv' && (
        <div className="mt-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5">
          <p className="text-sm text-ink">
            Required columns: <code className="text-brand">date, amount, direction, category</code>, optional{' '}
            <code className="text-brand">description</code>. Direction is IN or OUT.
          </p>
          <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-ink shadow-sm ring-1 ring-slate-200 hover:bg-slate-50">
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileSpreadsheet className="h-4 w-4 text-brand" />}
            Choose a CSV file
            <input
              type="file"
              accept=".csv,text/csv"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) uploadCsv(file)
              }}
            />
          </label>
          {csvResult && (
            <div className="mt-4 text-sm">
              <p className="flex items-center gap-2 text-success">
                <Check className="h-4 w-4" /> {csvResult.imported} transactions imported
                {csvResult.skipped_duplicates > 0 && `, ${csvResult.skipped_duplicates} duplicates skipped`}
              </p>
              {csvResult.errors.length > 0 && (
                <ul className="mt-2 space-y-1 text-xs text-risk">
                  {csvResult.errors.slice(0, 5).map((e) => (
                    <li key={`${e.row}-${e.reason}`}>Row {e.row}: {e.reason}</li>
                  ))}
                  {csvResult.errors.length > 5 && <li>And {csvResult.errors.length - 5} more rows with errors.</li>}
                </ul>
              )}
            </div>
          )}
        </div>
      )}

      {form.sample_loaded && (
        <p className="mt-5 flex items-center gap-2 text-sm text-success">
          <Check className="h-4 w-4" /> Northstar Studio data is loaded into your workspace.
        </p>
      )}
    </div>
  )
}

function FinancialStep({ form, update }: { form: FormState; update: Update }) {
  const symbol = CURRENCY_SYMBOL[form.currency] ?? form.currency
  return (
    <div>
      <StepHeading
        title="Financial snapshot"
        subtitle={
          form.sample_loaded
            ? 'Prefilled from the Northstar Studio data. Adjust anything that does not fit.'
            : 'Rough numbers are fine. Only the cash balance is required.'
        }
      />
      <div className="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-2">
        {form.sample_loaded ? (
          <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate sm:col-span-2">
            Your cash position comes from the imported transaction history, so there is nothing to enter here.
          </div>
        ) : (
          <MoneyField
            label="Current cash balance"
            hint="Today's balance across your business accounts. Every forecast starts from it."
            symbol={symbol}
            value={form.current_cash_balance}
            onChange={(v) => update('current_cash_balance', v)}
            required
          />
        )}
        <MoneyField
          label="Monthly revenue"
          hint="Your typical monthly sales, for context in reports and the copilot."
          symbol={symbol}
          value={form.monthly_revenue_estimate}
          onChange={(v) => update('monthly_revenue_estimate', v)}
        />
        <MoneyField
          label="Monthly fixed expenses"
          hint="Rent, payroll and subscriptions, the costs that arrive no matter what."
          symbol={symbol}
          value={form.monthly_fixed_expenses_estimate}
          onChange={(v) => update('monthly_fixed_expenses_estimate', v)}
        />
        <NumberField
          label="Employees"
          hint="Payroll is usually the largest recurring outflow."
          value={form.employee_count}
          onChange={(v) => update('employee_count', v)}
        />
        <NumberField
          label="Customer payment delay"
          suffix="days"
          hint="Late customer payments are the most common cause of SME cash gaps."
          value={form.customer_payment_delay_days}
          onChange={(v) => update('customer_payment_delay_days', v)}
        />
        <NumberField
          label="Supplier payment delay"
          suffix="days"
          hint="How long you usually take to pay suppliers."
          value={form.supplier_payment_delay_days}
          onChange={(v) => update('supplier_payment_delay_days', v)}
        />
      </div>
    </div>
  )
}

function GoalsStep({ goals, toggleGoal }: { goals: string[]; toggleGoal: (k: string) => void }) {
  return (
    <div>
      <StepHeading title="What matters most right now?" subtitle="Pick as many as you like. PULSE puts these insights first." />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {GOALS.map((g) => {
          const selected = goals.includes(g.key)
          return (
            <button
              key={g.key}
              type="button"
              onClick={() => toggleGoal(g.key)}
              className={cn(
                'relative flex items-start gap-3 rounded-2xl border-2 p-4 text-left transition-colors',
                selected ? 'border-brand bg-brand/5' : 'border-slate-200 hover:border-slate-300',
              )}
            >
              <g.icon className={cn('mt-0.5 h-5 w-5 shrink-0', selected ? 'text-brand' : 'text-slate')} />
              <span className="pr-6">
                <span className="block text-sm font-semibold text-ink">{g.label}</span>
                <span className="block text-xs text-slate">{g.desc}</span>
              </span>
              {selected && (
                <span className="absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full bg-brand text-white">
                  <Check className="h-3 w-3" />
                </span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

function AiStep({ form, update }: { form: FormState; update: Update }) {
  return (
    <div>
      <StepHeading title="AI preferences" subtitle="Tune how cautious PULSE is when it flags risks and suggests actions." />
      <div className="space-y-6">
        <div>
          <Label>Alert sensitivity</Label>
          <div className="flex flex-wrap gap-2">
            {(['conservative', 'balanced', 'relaxed'] as const).map((v) => (
              <Chip key={v} active={form.alert_sensitivity === v} onClick={() => update('alert_sensitivity', v)}>
                {v}
              </Chip>
            ))}
          </div>
          <p className="mt-1.5 text-xs text-slate">Conservative warns you earlier, relaxed only when a risk is close.</p>
        </div>
        <div>
          <Label>Risk tolerance</Label>
          <div className="flex flex-wrap gap-2">
            {(['conservative', 'balanced', 'growth-focused'] as const).map((v) => (
              <Chip key={v} active={form.risk_tolerance === v} onClick={() => update('risk_tolerance', v)}>
                {v}
              </Chip>
            ))}
          </div>
          <p className="mt-1.5 text-xs text-slate">Shapes how bold the suggested rescue strategies are.</p>
        </div>
        <div>
          <Label>Forecast horizon</Label>
          <div className="flex flex-wrap gap-2">
            {['30', '60', '90'].map((v) => (
              <Chip key={v} active={form.forecast_horizon_days === v} onClick={() => update('forecast_horizon_days', v)}>
                {v} days
              </Chip>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function InitStep({
  taskStatus,
  summary,
  forecast,
  done,
}: {
  taskStatus: Record<string, TaskStatus>
  summary: FinancialSummary | null
  forecast: ForecastRunOut | null
  done: boolean
}) {
  return (
    <div>
      <div className={cn('mb-5 flex h-12 w-12 items-center justify-center rounded-2xl', done ? 'bg-success/10' : 'bg-brand/10')}>
        {done ? <Check className="h-6 w-6 text-success" /> : <Loader2 className="h-6 w-6 animate-spin text-brand" />}
      </div>
      <StepHeading
        title={done ? 'Your workspace is ready' : 'Setting up your workspace'}
        subtitle={done ? 'Here is your first read, computed from your data just now.' : 'Each step below is a real computation, not an animation.'}
      />

      <div className="space-y-2">
        {INIT_TASKS.map((t) => {
          const s = taskStatus[t.key] ?? 'pending'
          return (
            <div key={t.key} className="flex items-center gap-3 rounded-xl bg-slate-50 px-4 py-3">
              {s === 'done' && <Check className="h-4 w-4 text-success" />}
              {s === 'running' && <Loader2 className="h-4 w-4 animate-spin text-brand" />}
              {s === 'pending' && <span className="h-4 w-4 rounded-full border-2 border-slate-300" />}
              {s === 'error' && <AlertTriangle className="h-4 w-4 text-risk" />}
              <span className={cn('text-sm', s === 'pending' ? 'text-slate' : 'text-ink')}>{t.label}</span>
            </div>
          )
        })}
      </div>

      {done && summary && (
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 p-4">
            <p className="text-xs text-slate">Current cash</p>
            <p className="mt-1 font-display text-xl font-semibold text-ink">{formatMoney(summary.current_cash, summary.currency)}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 p-4">
            <p className="text-xs text-slate">Risk level</p>
            <div className="mt-1.5">
              <Badge tone={riskTone(summary.risk_level)}>{summary.risk_level}</Badge>
            </div>
          </div>
          <div className="rounded-2xl border border-slate-200 p-4">
            <p className="text-xs text-slate">Forecast shortfall</p>
            <p className="mt-1 font-display text-xl font-semibold text-ink">
              {forecast?.shortfall_date ? formatDate(forecast.shortfall_date) : 'None'}
            </p>
          </div>
          <div className="rounded-2xl bg-brand/5 p-4 text-sm text-ink sm:col-span-3">
            <span className="font-semibold">Top finding: </span>
            {summary.risk_reasons[0]}
          </div>
        </div>
      )}
    </div>
  )
}

const inputClass =
  'w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/15'

function Label({ children }: { children: ReactNode }) {
  return <span className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate">{children}</span>
}

function MoneyField({
  label,
  hint,
  symbol,
  value,
  onChange,
  required,
}: {
  label: string
  hint: string
  symbol: string
  value: string
  onChange: (v: string) => void
  required?: boolean
}) {
  return (
    <label className="block">
      <Label>
        {label}
        {required && <span className="text-risk"> *</span>}
      </Label>
      <div className="flex items-center rounded-xl border border-slate-200 bg-white focus-within:border-brand focus-within:ring-2 focus-within:ring-brand/15">
        <span className="pl-3.5 text-sm font-medium text-slate">{symbol}</span>
        <input
          inputMode="numeric"
          value={value ? Number(value).toLocaleString('en-US') : ''}
          onChange={(e) => onChange(e.target.value.replace(/[^\d]/g, ''))}
          placeholder="0"
          className="w-full bg-transparent px-2 py-2.5 text-sm text-ink outline-none"
        />
      </div>
      <span className="mt-1 block text-xs text-slate">{hint}</span>
    </label>
  )
}

function NumberField({
  label,
  hint,
  value,
  onChange,
  suffix,
}: {
  label: string
  hint: string
  value: string
  onChange: (v: string) => void
  suffix?: string
}) {
  return (
    <label className="block">
      <Label>{label}</Label>
      <div className="flex items-center rounded-xl border border-slate-200 bg-white focus-within:border-brand focus-within:ring-2 focus-within:ring-brand/15">
        <input
          inputMode="numeric"
          value={value}
          onChange={(e) => onChange(e.target.value.replace(/[^\d]/g, ''))}
          placeholder="0"
          className="w-full bg-transparent px-3.5 py-2.5 text-sm text-ink outline-none"
        />
        {suffix && <span className="pr-3.5 text-sm text-slate">{suffix}</span>}
      </div>
      <span className="mt-1 block text-xs text-slate">{hint}</span>
    </label>
  )
}

function SelectCard({ selected, onClick, children }: { selected: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'flex flex-col items-start gap-2 rounded-2xl border-2 p-4 text-left transition-colors',
        selected ? 'border-brand bg-brand/5' : 'border-slate-200 hover:border-slate-300',
      )}
    >
      {children}
    </button>
  )
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded-full border px-3.5 py-1.5 text-sm font-medium capitalize transition-colors',
        active ? 'border-brand bg-brand text-white' : 'border-slate-200 text-slate hover:border-slate-300 hover:text-ink',
      )}
    >
      {children}
    </button>
  )
}
