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
