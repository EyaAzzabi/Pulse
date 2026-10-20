import { useQuery } from '@tanstack/react-query'
import {
  Bell,
  Bot,
  FileText,
  LayoutDashboard,
  LineChart,
  LogOut,
  Receipt,
  ScrollText,
  Sliders,
  Sparkles,
} from 'lucide-react'
import { Navigate, NavLink, Outlet, useLocation } from 'react-router-dom'
import { ChatWidget } from '../components/ChatWidget'
import { Logo } from '../components/Logo'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { cn } from '../lib/cn'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/copilot', label: 'Copilot', icon: Bot, ai: true },
  { to: '/forecast', label: 'Forecast', icon: LineChart },
  { to: '/simulator', label: 'Simulator', icon: Sliders, ai: true },
  { to: '/invoices', label: 'Invoices', icon: Receipt },
  { to: '/decisions', label: 'Decisions', icon: ScrollText },
  { to: '/notifications', label: 'Notifications', icon: Bell },
]

export function AppLayout() {
  const { me, currentOrg, logout } = useAuth()
  const orgId = currentOrg?.organization_id
  const location = useLocation()

  const onboardingQuery = useQuery({
    queryKey: ['onboarding-gate', orgId],
    queryFn: async () => (await api.get(`/onboarding?organization_id=${orgId}`)).data,
    enabled: !!orgId,
    retry: false,
  })

  if (onboardingQuery.data && onboardingQuery.data.completed === false) {
    return <Navigate to="/onboarding" replace />
  }

  return (
    <div className="flex min-h-screen bg-midnight text-ink">
      <aside className="flex w-60 flex-col border-r border-slate-200 bg-white p-4">
        <Logo size={36} withWordmark className="mb-8 px-2" />

        <nav className="flex-1 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon, ai }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive ? 'bg-brand/10 text-brand' : 'text-slate hover:bg-slate-50 hover:text-ink',
                )
              }
            >
              <Icon className="h-4 w-4" />
              <span className="flex-1">{label}</span>
              {ai && (
                <span className="flex items-center gap-0.5 rounded-full bg-amber/15 px-1.5 py-0.5 text-[10px] font-semibold text-amber">
                  <Sparkles className="h-2.5 w-2.5" /> AI
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto space-y-3 border-t border-slate-200 pt-4">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive ? 'bg-brand/10 text-brand' : 'text-slate hover:bg-slate-50 hover:text-ink',
              )
            }
          >
            <FileText className="h-4 w-4" />
            Settings
          </NavLink>

          <div className="rounded-xl border border-brand/20 bg-brand/5 px-3 py-2.5">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-brand">Connected</p>
            <p className="truncate text-sm font-medium text-ink">{me?.user.full_name}</p>
            <p className="truncate text-xs text-slate">{currentOrg?.organization_name}</p>
          </div>

          <button
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate transition-colors hover:bg-risk/10 hover:text-risk"
          >
            <LogOut className="h-4 w-4" />
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>

      {location.pathname !== '/copilot' && <ChatWidget />}
    </div>
  )
}
