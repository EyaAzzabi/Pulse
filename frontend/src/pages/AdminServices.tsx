import { useQuery } from '@tanstack/react-query'
import { Activity, Database, Mail, Network, ShieldCheck, RefreshCw, CircleCheck, CircleMinus } from 'lucide-react'
import { api } from '../lib/api'

interface SystemState {
  database: { available: boolean; engine: string }
  llm: { configured: boolean; provider: string; model: string | null }
  email: { configured: boolean; mode: string }
  workflows: { configured: boolean }
  engine: { mode: string; human_approval: boolean }
}

export function AdminServices() {
  const query = useQuery({ queryKey: ['admin', 'system'], queryFn: async () => (await api.get<SystemState>('/admin/system')).data, refetchInterval: 30000 })
  const data = query.data
  const services = data ? [
    { icon: Database, label: 'Database', ok: data.database.available, state: data.database.available ? 'Connection verified' : 'Unavailable', detail: data.database.engine === 'sqlite' ? 'SQLite · local storage' : 'PostgreSQL · relational storage' },
    { icon: Activity, label: 'Financial engine', ok: true, state: 'Deterministic', detail: 'Financial calculations run independently of the language model. No LLM key required.' },
    { icon: Network, label: 'Generative copilot', ok: data.llm.configured, state: data.llm.configured ? 'Configured' : 'No LLM mode', detail: data.llm.configured ? `${data.llm.provider} · ${data.llm.model}` : 'The copilot uses deterministic responses. Text generation is optional.' },
    { icon: Mail, label: 'Verification email', ok: data.email.configured, state: data.email.configured ? data.email.mode === 'n8n' ? 'n8n configured' : 'SMTP configured' : data.email.mode === 'server_log' ? 'Server log (development)' : 'Not configured', detail: data.email.configured ? data.email.mode === 'n8n' ? 'n8n is configured for verification codes. SMTP provides a fallback when configured.' : 'SMTP is configured for verification codes.' : data.email.mode === 'server_log' ? 'Explicit local mode: codes are written to the server log.' : 'Email is unavailable. Configure Gmail SMTP or the n8n workflow.' },
    { icon: Network, label: 'Execution workflows', ok: data.workflows.configured, state: data.workflows.configured ? 'Webhook configured' : 'Not configured', detail: 'Business actions require human approval before execution.' },
    { icon: ShieldCheck, label: 'Account approvals', ok: true, state: 'Human approval', detail: 'New accounts await administrative approval. Every access change is recorded.' },
  ] : []
  return <><div className="admin-page-heading"><div><span className="admin-eyebrow">BEHIND THE TRUST</span><h1>A clear view of your services.</h1><p>PULSE component configuration and availability, with secrets kept private.</p></div><button className="admin-secondary" disabled={query.isFetching} onClick={() => void query.refetch()}><RefreshCw size={15} />Refresh</button></div><div className="admin-service-note"><ShieldCheck size={18} /><p>Configured means the settings are present. Only the database connection is tested here; no email or webhook is sent.</p></div>{query.isPending && <div className="admin-state">Loading services…</div>}{query.isError && <div className="admin-state" role="alert"><p>Unable to read service status.</p><button className="admin-secondary" onClick={() => void query.refetch()}>Try again</button></div>}<div className="admin-services-grid">{services.map(s => <article className="admin-service" key={s.label}><span className={`service-icon ${s.ok ? 'ok' : 'optional'}`}><s.icon size={23} /></span><div><h2>{s.label}</h2><span className={`admin-status ${s.ok ? 'approved' : 'pending'}`}><i />{s.state}</span><p>{s.detail}</p></div>{s.ok ? <CircleCheck size={19} className="service-check" /> : <CircleMinus size={19} className="service-optional" />}</article>)}</div></>
}
