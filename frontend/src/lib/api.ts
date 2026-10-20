import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pulse_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (axios.isAxiosError(error) && error.response?.status === 403 && error.response.data?.detail === 'Account approval required') {
      window.dispatchEvent(new Event('pulse-account-status-changed'))
    }
    return Promise.reject(error)
  },
)

export function setAuthToken(token: string | null) {
  if (token) {
    localStorage.setItem('pulse_token', token)
  } else {
    localStorage.removeItem('pulse_token')
  }
}

export function getAuthToken(): string | null {
  return localStorage.getItem('pulse_token')
}
