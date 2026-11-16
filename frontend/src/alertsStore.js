import { ref } from 'vue'
import { api } from './api'

// Shared alert state so the bell badge, the bell list and the Alerts page
// always agree about what has been read.
export const alerts = ref([])
export const total = ref(0)
export const unread = ref(0)
export const loading = ref(false)
export const error = ref('')
export const loaded = ref(false)

function normalize(res) {
  const list = Array.isArray(res) ? res : res?.alerts || []
  const unreadCount =
    typeof res?.unread === 'number' ? res.unread : list.filter((a) => !a.read).length
  return { list, total: res?.total ?? list.length, unread: unreadCount }
}

export async function refreshAlerts() {
  loading.value = true
  error.value = ''
  try {
    const { list, total: t, unread: u } = normalize(await api.alerts())
    alerts.value = list
    total.value = t
    unread.value = u
    loaded.value = true
  } catch (e) {
    error.value = e.message || 'Could not load alerts'
    alerts.value = []
  } finally {
    loading.value = false
  }
}

function applyLocalRead(keys) {
  const set = new Set(keys)
  alerts.value = alerts.value.map((a) => (set.has(a.key) ? { ...a, read: true } : a))
  if (alerts.value.length) unread.value = alerts.value.filter((a) => !a.read).length
}

export async function markAlertsRead(keys) {
  const list = (keys || []).filter(Boolean)
  if (!list.length) return
  applyLocalRead(list)
  try {
    const res = await api.markAlertsRead(list)
    if (typeof res?.unread === 'number') unread.value = res.unread
  } catch {
    await refreshAlerts()
  }
}

export async function markAllAlertsRead() {
  const keys = alerts.value.filter((a) => !a.read).map((a) => a.key)
  alerts.value = alerts.value.map((a) => ({ ...a, read: true }))
  unread.value = 0
  try {
    const res = await api.markAllAlertsRead()
    if (typeof res?.unread === 'number') unread.value = res.unread
  } catch {
    await refreshAlerts()
  }
  return keys.length
}
