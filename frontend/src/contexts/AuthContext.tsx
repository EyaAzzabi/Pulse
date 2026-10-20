import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, getAuthToken, setAuthToken } from '../lib/api'
import type { MeResponse, MembershipOut } from '../types'

interface AuthContextValue {
  me: MeResponse | null
  currentOrg: MembershipOut | null
  isLoading: boolean
  isAuthenticated: boolean
  setCurrentOrgId: (organizationId: string) => void
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string, organizationName: string, otpCode: string) => Promise<void>
  logout: () => void
  refreshMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const CURRENT_ORG_KEY = 'pulse_current_org_id'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<MeResponse | null>(null)
  const [currentOrgId, setCurrentOrgIdState] = useState<string | null>(
    localStorage.getItem(CURRENT_ORG_KEY),
  )
  const [isLoading, setIsLoading] = useState(true)

  async function refreshMe() {
    const token = getAuthToken()
    if (!token) {
      setMe(null)
      setIsLoading(false)
      return
    }
    try {
      const res = await api.get<MeResponse>('/auth/me')
      setMe(res.data)
      if (!currentOrgId && res.data.memberships.length > 0) {
        setCurrentOrgId(res.data.memberships[0].organization_id)
      }
    } catch {
      setAuthToken(null)
      setMe(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    refreshMe()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function setCurrentOrgId(organizationId: string) {
    localStorage.setItem(CURRENT_ORG_KEY, organizationId)
    setCurrentOrgIdState(organizationId)
  }

  async function login(email: string, password: string) {
    const res = await api.post('/auth/login', { email, password })
    setAuthToken(res.data.access_token)
    await refreshMe()
  }

  async function register(email: string, password: string, fullName: string, organizationName: string, otpCode: string) {
    const res = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      organization_name: organizationName,
      otp_code: otpCode,
    })
    setAuthToken(res.data.access_token)
    await refreshMe()
  }

  function logout() {
    setAuthToken(null)
    localStorage.removeItem(CURRENT_ORG_KEY)
    setMe(null)
    setCurrentOrgIdState(null)
  }

  const currentOrg = me?.memberships.find((m) => m.organization_id === currentOrgId) ?? me?.memberships[0] ?? null

  return (
    <AuthContext.Provider
      value={{
        me,
        currentOrg,
        isLoading,
        isAuthenticated: !!me,
        setCurrentOrgId,
        login,
        register,
        logout,
        refreshMe,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
