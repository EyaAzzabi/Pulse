export interface UserOut {
  id: string
  email: string
  full_name: string
  preferred_language: string
  default_currency: string
  timezone: string
  is_admin: boolean
  account_status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'SUSPENDED'
  review_reason: string
}

export interface MembershipOut {
  organization_id: string
  organization_name: string
  role: 'OWNER' | 'FINANCE_MANAGER' | 'ACCOUNTANT' | 'VIEWER'
}

export interface MeResponse {
  user: UserOut
  memberships: MembershipOut[]
}

export interface FinancialSummary {
  as_of: string
  currency: string
  current_cash: string
  trailing_30d_inflow: string
  trailing_30d_outflow: string
  net_cash_flow_30d: string
  monthly_burn_rate: string
  cash_runway_days: number | null
  outstanding_receivables: string
  outstanding_payables: string
  overdue_receivables_count: number
  overdue_receivables_amount: string
  overdue_payables_count: number
  overdue_payables_amount: string
  upcoming_obligations_30d: string
  largest_customer_share_pct: string
  expense_trend_pct: string
  risk_level: 'low' | 'medium' | 'high'
  risk_reasons: string[]
}

export interface CashflowPoint {
  date: string
  actual_cash: string | null
  projected_cash: string | null
  confidence: string | null
  is_forecast: boolean
}

export interface TransactionOut {
  id: string
  date: string
  amount: string
  currency: string
  category: string
  direction: 'IN' | 'OUT'
  source: string
  status: string
  description: string
}

export interface InvoiceOut {
  id: string
  direction: 'RECEIVABLE' | 'PAYABLE'
  counterparty_name: string
  amount: string
  amount_paid: string
  currency: string
  issue_date: string
  due_date: string
  status: string
  reference: string
}

export interface ForecastPointOut {
  date: string
  projected_cash: string
  known_component: string
  uncertain_component: string
  confidence: string
}

export interface ForecastRunOut {
  id: string
  created_at: string
  horizon_days: number
  method: string
  starting_cash: string
  shortfall_date: string | null
  points: ForecastPointOut[]
}

export interface SimulationCreateRequest {
  name: string
  horizon_days: number
  customer_payment_delay_days: number
  supplier_payment_delay_days: number
  revenue_change_pct: number
  expense_change_pct: number
  inventory_purchase_amount: number
  financing_amount: number
  financing_monthly_cost: number
  one_time_cash_injection: number
}

export interface SimulationResultOut {
  id: string
  scenario_id: string
  name: string
  created_at: string
  assumptions: Record<string, unknown>
  lowest_cash_point: string
  lowest_cash_date: string | null
  runway_days: number | null
  days_below_zero: number
  impact_vs_baseline: string
  baseline_points: ForecastPointOut[]
  simulated_points: ForecastPointOut[]
}

export interface Recommendation {
  key: string
  title: string
  rationale: string
  expected_impact: string
  feasibility: string
  cost: string
  residual_risk: string
  requires_approval: boolean
}

export interface ChatResponse {
  conversation_id: string
  message: string
  ai_generated: boolean
  llm_available: boolean
  metrics: Record<string, unknown>
  risk_indicators: string[]
  evidence: string[]
  suggested_follow_ups: string[]
  chart_points: { date: string; projected_cash: string; confidence: string }[]
}

export interface ConversationOut {
  id: string
  title: string
  created_at: string
  messages: { role: 'user' | 'assistant'; content: string; created_at: string }[]
}

export interface ActionOut {
  id: string
  organization_id: string
  action_type: string
  target: Record<string, unknown>
  details: Record<string, unknown>
  expected_result: string
  risks: string
  evidence: Record<string, unknown>
  requires_approval: boolean
  status: string
  created_at: string
  approved_by_user_id: string | null
  approved_at: string | null
  execution_result: Record<string, unknown>
}

export interface NotificationOut {
  id: string
  category: string
  severity: 'info' | 'warning' | 'critical'
  title: string
  body: string
  link: string
  read: boolean
  created_at: string
}
