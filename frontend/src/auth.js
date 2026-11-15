import { ref } from 'vue'
import { api, getStoredUser, storeSession, clearSession, getToken } from './api'

const user = ref(getStoredUser())
const loading = ref(false)

export function useAuth() {
  async function login(username, password) {
    loading.value = true
    try {
      const res = await api.login(username, password)
      storeSession(res.access_token, res.user)
      user.value = res.user
      return res.user
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    try {
      const res = await api.register(payload)
      storeSession(res.access_token, res.user)
      user.value = res.user
      return res.user
    } finally {
      loading.value = false
    }
  }

  function logout() {
    clearSession()
    user.value = null
  }

  const isAuthenticated = () => Boolean(getToken())

  return { user, loading, login, register, logout, isAuthenticated }
}
