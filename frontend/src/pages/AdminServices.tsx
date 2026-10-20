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
    { icon: Database, label: 'Base de données', ok: data.database.available, state: data.database.available ? 'Connexion vérifiée' : 'Indisponible', detail: data.database.engine === 'sqlite' ? 'SQLite · stockage local' : 'PostgreSQL · stockage relationnel' },
    { icon: Activity, label: 'Moteur financier', ok: true, state: 'Déterministe', detail: 'Calculs financiers indépendants du modèle de langage. Aucune clé LLM nécessaire.' },
    { icon: Network, label: 'Copilot génératif', ok: data.llm.configured, state: data.llm.configured ? 'Configuré' : 'Mode sans LLM', detail: data.llm.configured ? `${data.llm.provider} · ${data.llm.model}` : 'Le copilot utilise ses réponses déterministes. La génération de texte est facultative.' },
    { icon: Mail, label: 'E-mail de vérification', ok: data.email.configured, state: data.email.configured ? 'SMTP configuré' : 'Journal serveur', detail: data.email.configured ? 'Transport SMTP configuré pour les codes de vérification.' : 'Les codes OTP sont écrits dans le journal serveur en mode local.' },
    { icon: Network, label: 'Workflows d’exécution', ok: data.workflows.configured, state: data.workflows.configured ? 'Webhook configuré' : 'Non configuré', detail: 'Les actions métier restent soumises à l’approbation humaine avant toute exécution.' },
    { icon: ShieldCheck, label: 'Validation des comptes', ok: true, state: 'Contrôle humain', detail: 'Les nouveaux comptes attendent une décision administrative. Chaque changement d’accès est tracé.' },
  ] : []
  return <><div className="admin-page-heading"><div><span className="admin-eyebrow">LES COULISSES DE LA CONFIANCE</span><h1>Un regard sur vos services.</h1><p>Configuration et disponibilité des composants PULSE, sans exposition des secrets.</p></div><button className="admin-secondary" disabled={query.isFetching} onClick={() => void query.refetch()}><RefreshCw size={15} />Actualiser</button></div><div className="admin-service-note"><ShieldCheck size={18} /><p>« Configuré » indique la présence des paramètres. Seule la connexion à la base est testée ici ; aucun e-mail ni webhook n’est envoyé.</p></div>{query.isPending && <div className="admin-state">Chargement des services…</div>}{query.isError && <div className="admin-state" role="alert"><p>Impossible de lire l’état des services.</p><button className="admin-secondary" onClick={() => void query.refetch()}>Réessayer</button></div>}<div className="admin-services-grid">{services.map(s => <article className="admin-service" key={s.label}><span className={`service-icon ${s.ok ? 'ok' : 'optional'}`}><s.icon size={23} /></span><div><h2>{s.label}</h2><span className={`admin-status ${s.ok ? 'approved' : 'pending'}`}><i />{s.state}</span><p>{s.detail}</p></div>{s.ok ? <CircleCheck size={19} className="service-check" /> : <CircleMinus size={19} className="service-optional" />}</article>)}</div></>
}
