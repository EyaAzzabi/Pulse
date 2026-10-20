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
  return <div className="account-status-page"><Logo withWordmark size={40} /><div className="account-status-card"><div className="account-status-icon"><ShieldCheck size={35} /></div><span className="admin-eyebrow">A TRUSTED WORKSPACE</span><h1>{status === 'PENDING' ? 'Your next chapter is taking shape.' : status === 'REJECTED' ? 'Your request has been reviewed.' : 'Your access is suspended.'}</h1><p>{status === 'PENDING' ? 'Your email is verified. Our team now needs to approve your account before you can access PULSE.' : 'Review the reason below. Your access to business features is currently disabled.'}</p><div className="status-progress"><span><Check size={17} />Email verified</span><span><Clock3 size={17} />{status === 'PENDING' ? 'Administrative approval' : 'Administrative decision'}</span><span><Mail size={17} />{me?.user.email}</span></div>{me?.user.review_reason && <div className="review-reason"><strong>Decision reason</strong><p>{me.user.review_reason}</p></div>}<button className="admin-primary" disabled={busy} onClick={async () => { setBusy(true); try { await refreshMe() } finally { setBusy(false) } }}><RefreshCw size={16} />{busy ? 'Checking…' : 'Check my status'}</button><span className="status-auto">Automatically refreshed every 30 seconds.</span></div><button className="admin-text-button" onClick={logout}><LogOut size={16} />Sign out</button></div>
}
