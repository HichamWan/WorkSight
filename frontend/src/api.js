const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

function isAuthEndpoint(path) {
  return path.startsWith('/hr/auth/')
}

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

function queryString(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.append(key, value)
  })
  const stringified = search.toString()
  return stringified ? `?${stringified}` : ''
}

async function request(path, { method = 'GET', body, formData, params } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (body) headers['Content-Type'] = 'application/json'

  const res = await fetch(`${BASE_URL}${path}${queryString(params)}`, {
    method,
    headers,
    body: formData ?? (body ? JSON.stringify(body) : undefined)
  })

  // Token rejected — clear the local session and bounce the user to /login.
  if (res.status === 401 && !isAuthEndpoint(path)) {
    clearSession()
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      const next = encodeURIComponent(window.location.pathname + window.location.search)
      window.location.assign(`/login?next=${next}`)
    }
    throw new Error('Session expired. Please sign in again.')
  }

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
  // ---------- Auth ----------
  login: (username, password) =>
    request('/hr/auth/login', { method: 'POST', body: { username, password } }),

  register: (payload) =>
    request('/hr/auth/register', { method: 'POST', body: payload }),

  logout: () => request('/hr/auth/logout', { method: 'POST' }),

  me: () => request('/hr/auth/me'),

  changePassword: (currentPassword, newPassword) =>
    request('/hr/auth/change-password', {
      method: 'POST',
      body: { current_password: currentPassword, new_password: newPassword }
    }),

  // ---------- Dashboard ----------
  dashboardSummary: () => request('/hr/dashboard/summary'),
  dashboardToday: () => request('/hr/dashboard/today'),
  dashboardAnalytics: () => request('/hr/dashboard/analytics'),

  // ---------- Employees ----------
  employees: (params) => request('/hr/employees', { params }),
  employee: (id) => request(`/hr/employees/${id}`),
  createEmployee: (payload) => request('/hr/employees', { method: 'POST', body: payload }),
  updateEmployee: (id, payload) => request(`/hr/employees/${id}`, { method: 'PUT', body: payload }),
  deleteEmployee: (id) => request(`/hr/employees/${id}`, { method: 'DELETE' }),

  // ---------- Attendance ----------
  attendance: (params) => request('/hr/attendance', { params }),
  checkIn: (payload) => request('/hr/attendance/check-in', { method: 'POST', body: payload }),
  checkOut: (payload) => request('/hr/attendance/check-out', { method: 'POST', body: payload }),

  // ---------- Work hours ----------
  workHours: (params) => request('/hr/work-hours', { params }),

  // ---------- Alerts ----------
  alerts: () => request('/hr/alerts'),
  alertsOvertime: () => request('/hr/alerts/overtime'),
  alertsUndertime: () => request('/hr/alerts/under-time'),
  alertsLate: () => request('/hr/alerts/late'),

  // ---------- Reports ----------
  reportAttendance: (params) => request('/hr/reports/attendance', { params }),
  reportWorkHours: (params) => request('/hr/reports/work-hours', { params }),
  exportReport: (reportType, format = 'csv') =>
    request('/hr/reports/export', { params: { report_type: reportType, format } })
}

/**
 * Download a report file (CSV/Excel) and save it using the filename
 * the backend sends in the Content-Disposition header.
 */
export async function downloadReport(reportType, format = 'csv') {
  const token = getToken()
  const headers = token ? { Authorization: `Bearer ${token}` } : {}

  const res = await fetch(
    `${BASE_URL}/hr/reports/export?report_type=${encodeURIComponent(reportType)}&format=${encodeURIComponent(format)}`,
    { method: 'GET', headers }
  )

  if (!res.ok) throw new Error(`Export failed (${res.status})`)

  const disposition = res.headers.get('content-disposition') || ''
  const match = /filename="?([^"]+)"?/.exec(disposition)
  const filename = match ? match[1] : `report_${reportType}.${format}`

  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)

  return filename
}
