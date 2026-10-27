/**
 * Role / permission matrix.
 * Mirrors the roles the FastAPI backend enforces via require_role().
 */
export const PERMISSIONS = {
  viewDashboard: ['HR', 'MANAGER', 'EXECUTIVE'],
  viewEmployees: ['HR', 'MANAGER', 'EXECUTIVE'],
  viewAttendance: ['HR', 'MANAGER', 'EXECUTIVE'],
  viewAlerts: ['HR', 'MANAGER'],
  viewReports: ['HR', 'MANAGER'],
  createEmployee: ['HR', 'MANAGER'],
  updateEmployee: ['HR', 'MANAGER'],
  deleteEmployee: ['HR'],
  recordAttendance: ['HR', 'MANAGER']
}

export function normalizeRole(user) {
  return (user?.role || '').toString().trim().toUpperCase()
}

/** True when the user's role is allowed to perform the given action. */
export function can(permission, user) {
  const allowed = PERMISSIONS[permission]
  if (!allowed) return true
  return allowed.includes(normalizeRole(user))
}

export function roleLabel(user) {
  const role = normalizeRole(user)
  return role ? role.charAt(0) + role.slice(1).toLowerCase() : '—'
}
