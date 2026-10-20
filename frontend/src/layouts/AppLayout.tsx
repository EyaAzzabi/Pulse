import { useQuery } from '@tanstack/react-query'
import {
  Bell,
  Bot,
  LayoutDashboard,
  LineChart,
  LogOut,
  Menu,
  Receipt,
  ScrollText,
  Settings,
  Sliders,
  Sparkles,
  X,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Navigate, NavLink, Outlet, useLocation } from 'react-router-dom'
import { ChatWidget } from '../components/ChatWidget'
import { Logo } from '../components/Logo'
import { NotificationBell } from '../components/NotificationBell'
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
  { to: '/notifications', label: 'Notifications', icon: Bell, badge: true },
]

const PAGE_TITLES: Record<string, string> = {
  ...Object.fromEntries(NAV_ITEMS.map((n) => [n.to, n.label])),
  '/settings': 'Settings',
}

function initials(name?: string) {
  return (name ?? '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join('')
}

export function AppLayout() {
  const { me, currentOrg, logout } = useAuth()
  const orgId = currentOrg?.organization_id
  const location = useLocation()
  const [drawerOpen, setDrawerOpen] = useState(false)

  useEffect(() => setDrawerOpen(false), [location.pathname])

  const onboardingQuery = useQuery({
    queryKey: ['onboarding-gate', orgId],
    queryFn: async () => (await api.get(`/onboarding?organization_id=${orgId}`)).data,
    enabled: !!orgId,
    retry: false,
  })

  const unread = useQuery({
    queryKey: ['notifications-unread', orgId],
    queryFn: async () => (await api.get<{ unread: number }>(`/notifications/unread-count?organization_id=${orgId}`)).data.unread,
    enabled: !!orgId,
    refetchInterval: 30_000,
  })

  if (onboardingQuery.data && onboardingQuery.data.completed === false) {
    return <Navigate to="/onboarding" replace />
  }

  const sidebar = (
    <div className="flex h-full flex-col p-4">
      <Logo size={36} withWordmark className="mb-8 px-2" />

      <nav className="flex-1 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon, ai, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
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
            {badge && !!unread.data && (
              <span className="rounded-full bg-risk px-1.5 py-0.5 text-[10px] font-bold text-white">
                {unread.data > 9 ? '9+' : unread.data}
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
              'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
              isActive ? 'bg-brand/10 text-brand' : 'text-slate hover:bg-slate-50 hover:text-ink',
            )
          }
        >
          <Settings className="h-4 w-4" />
          Settings
        </NavLink>

        <div className="rounded-xl border border-brand/20 bg-brand/5 px-3 py-2.5">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-brand">Connected</p>
          <p className="truncate text-sm font-medium text-ink">{me?.user.full_name}</p>
          <p className="truncate text-xs text-slate">{currentOrg?.organization_name}</p>
        </div>

        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate transition-colors hover:bg-risk/10 hover:text-risk"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex min-h-screen bg-midnight text-ink">
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 border-r border-slate-200 bg-white md:block">{sidebar}</aside>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-slate-900/40" onClick={() => setDrawerOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 bg-white shadow-2xl">
            <button
              type="button"
              onClick={() => setDrawerOpen(false)}
              className="absolute right-3 top-4 rounded-lg p-1.5 text-slate hover:bg-slate-50"
              aria-label="Close menu"
            >
              <X className="h-5 w-5" />
            </button>
            {sidebar}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-slate-200 bg-white/85 px-4 backdrop-blur sm:px-8">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            className="rounded-lg p-2 text-slate hover:bg-slate-50 md:hidden"
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="min-w-0">
            <p className="font-display text-base font-semibold text-ink">{PAGE_TITLES[location.pathname] ?? 'Pulse AI'}</p>
            <p className="hidden truncate text-xs text-slate sm:block">{currentOrg?.organization_name}</p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <NotificationBell orgId={orgId} />
            <div
              className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-brand to-brand-dark text-sm font-semibold text-white"
              title={me?.user.full_name}
            >
              {initials(me?.user.full_name) || '·'}
            </div>
          </div>
        </header>

        <main className="flex-1">
          <Outlet />
        </main>
      </div>

      {location.pathname !== '/copilot' && <ChatWidget />}
    </div>
  )
}
