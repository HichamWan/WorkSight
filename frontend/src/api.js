const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const TOKEN_KEY = 'worksight_token'
const USER_KEY = 'worksight_user'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY)) || null
  } catch {
    return null
  }
}

export function storeSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

async function request(path, { method = 'GET', body, formData } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (body) headers['Content-Type'] = 'application/json'

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: formData ?? (body ? JSON.stringify(body) : undefined)
  })

  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const err = await res.json()
      detail = err.detail || detail
    } catch { /* keep default */ }
    throw new Error(detail)
  }

  const contentType = res.headers.get('content-type') || ''
  return contentType.includes('application/json') ? res.json() : res.blob()
}

export const api = {
  login: (username, password) =>
    request('/hr/auth/login', { method: 'POST', body: { username, password } }),

  register: (payload) =>
    request('/hr/auth/register', { method: 'POST', body: payload }),

  me: () => request('/hr/auth/me'),

  dashboardSummary: () => request('/hr/dashboard/summary'),
  dashboardToday: () => request('/hr/dashboard/today'),
  dashboardAnalytics: () => request('/hr/dashboard/analytics'),

  employees: () => request('/hr/employees'),
  createEmployee: (payload) => request('/hr/employees', { method: 'POST', body: payload }),
  deleteEmployee: (id) => request(`/hr/employees/${id}`, { method: 'DELETE' }),

  attendance: () => request('/hr/attendance'),

  alerts: () => request('/hr/alerts')
}
