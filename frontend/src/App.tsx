import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import { AppLayout } from './layouts/AppLayout'
import { Copilot } from './pages/Copilot'
import { Dashboard } from './pages/Dashboard'
import { Decisions } from './pages/Decisions'
import { Forecast } from './pages/Forecast'
import { Invoices } from './pages/Invoices'
import { Landing } from './pages/Landing'
import { Login } from './pages/Login'
import { Notifications } from './pages/Notifications'
import { Onboarding } from './pages/Onboarding'
import { Settings } from './pages/Settings'
import { Simulator } from './pages/Simulator'
import { Admin } from './pages/Admin'
import { AccountStatus } from './pages/AccountStatus'

function ProtectedRoute({ children, statusOnly = false, admin = false }: { children: React.ReactNode; statusOnly?: boolean; admin?: boolean }) {
  const { isAuthenticated, isLoading, me } = useAuth()
  if (isLoading) {
    return <div className="flex min-h-screen items-center justify-center bg-midnight text-slate">Loading…</div>
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  if (!statusOnly && me?.user.account_status !== 'APPROVED') return <Navigate to="/account-status" replace />
  if (admin && !me?.user.is_admin) return <Navigate to="/dashboard" replace />
  if (!admin && !statusOnly && me?.user.is_admin) return <Navigate to="/admin" replace />
  return <>{children}</>
}

function SignupRoute() {
  const { me } = useAuth()
  if (me?.user.is_admin) return <Navigate to="/admin" replace />
  if (me && me.user.account_status !== 'APPROVED') return <Navigate to="/account-status" replace />
  return <Onboarding />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignupRoute />} />
      <Route path="/account-status" element={<ProtectedRoute statusOnly><AccountStatus /></ProtectedRoute>} />
      <Route path="/admin/*" element={<ProtectedRoute admin><Admin /></ProtectedRoute>} />

      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <Onboarding />
          </ProtectedRoute>
        }
      />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/copilot" element={<Copilot />} />
        <Route path="/forecast" element={<Forecast />} />
        <Route path="/simulator" element={<Simulator />} />
        <Route path="/invoices" element={<Invoices />} />
        <Route path="/decisions" element={<Decisions />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
