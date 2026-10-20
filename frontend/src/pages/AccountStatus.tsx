import { useEffect, useState } from 'react'
import { Clock3, ShieldCheck, RefreshCw, LogOut, Check, Mail } from 'lucide-react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Logo } from '../components/Logo'
import './Admin.css'

export function AccountStatus() {
  const { me, refreshMe, logout } = useAuth()
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    const timer = window.setInterval(() => { void refreshMe() }, 30000)
    return () => window.clearInterval(timer)
  }, [refreshMe])
  if (me?.user.account_status === 'APPROVED') return <Navigate to={me.user.is_admin ? '/admin' : '/onboarding'} replace />
  const status = me?.user.account_status ?? 'PENDING'
  return <div className="account-status-page"><Logo withWordmark size={40} /><div className="account-status-card"><div className="account-status-icon"><ShieldCheck size={35} /></div><span className="admin-eyebrow">UN ESPACE DE CONFIANCE</span><h1>{status === 'PENDING' ? 'Votre prochain chapitre se prépare.' : status === 'REJECTED' ? 'Votre demande a été examinée.' : 'Votre accès est suspendu.'}</h1><p>{status === 'PENDING' ? 'Votre adresse e-mail est vérifiée. Notre équipe doit maintenant valider votre compte avant de vous ouvrir les portes de PULSE.' : 'Consultez le motif de la décision ci-dessous. Votre accès aux fonctionnalités métier est actuellement désactivé.'}</p><div className="status-progress"><span><Check size={17} />E-mail vérifié</span><span><Clock3 size={17} />{status === 'PENDING' ? 'Validation administrative' : 'Décision administrative'}</span><span><Mail size={17} />{me?.user.email}</span></div>{me?.user.review_reason && <div className="review-reason"><strong>Motif communiqué</strong><p>{me.user.review_reason}</p></div>}<button className="admin-primary" disabled={busy} onClick={async () => { setBusy(true); try { await refreshMe() } finally { setBusy(false) } }}><RefreshCw size={16} />{busy ? 'Vérification…' : 'Vérifier mon statut'}</button><span className="status-auto">Actualisation automatique toutes les 30 secondes.</span></div><button className="admin-text-button" onClick={logout}><LogOut size={16} />Se déconnecter</button></div>
}
