<template>
  <div class="layout">
    <aside class="sidebar glass glass--strong">
      <div class="sidebar__brand">
        <div class="brand-mark">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 7v5l3 2" />
          </svg>
        </div>
        <span class="brand-name">WorkSight</span>
      </div>

      <nav class="sidebar__nav">
        <router-link
          v-for="item in visibleNav"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          active-class="nav-link--active"
          :exact="item.to === '/'"
        >
          <span class="nav-link__icon" v-html="item.icon"></span>
          {{ t(item.key) }}
        </router-link>
      </nav>

      <div class="sidebar__footer">
        <div class="user-card glass--soft">
          <div class="user-card__avatar">{{ initials }}</div>
          <div class="user-card__info">
            <span class="user-card__name">{{ user?.username || 'User' }}</span>
            <span class="user-card__role muted">{{ currentRole }}</span>
          </div>
        </div>
        <button class="btn btn--ghost btn--sm sidebar__logout" @click="handleLogout">
          {{ t('logout') }}
        </button>
      </div>
    </aside>

    <main class="content">
      <header class="topbar glass glass--strong">
        <div>
          <h1 class="topbar__title">{{ pageTitle }}</h1>
          <p class="topbar__date muted">{{ todayLabel }}</p>
        </div>
        <div class="topbar__spacer"></div>
        <LanguageSwitcher />
        <ThemeToggle />
        <span class="chip chip--success">{{ t('systemOnline') }}</span>
      </header>

      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../auth'
import { useI18n } from '../i18n'
import { api } from '../api'
import { can, roleLabel } from '../roles'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import ThemeToggle from '../components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const { user, logout } = useAuth()
const { t } = useI18n()

const navItems = [
  {
    to: '/',
    key: 'dashboard',
    permission: 'viewDashboard',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>'
  },
  {
    to: '/employees',
    key: 'employees',
    permission: 'viewEmployees',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/></svg>'
  },
  {
    to: '/attendance',
    key: 'attendance',
    permission: 'viewAttendance',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M8 2v4M16 2v4M3 9h18"/><path d="M9 14l2 2 4-4"/></svg>'
  },
  {
    to: '/alerts',
    key: 'alerts',
    permission: 'viewAlerts',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>'
  },
  {
    to: '/reports',
    key: 'reports',
    permission: 'viewReports',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M12 18v-6M9 15l3 3 3-3"/></svg>'
  }
]

const visibleNav = computed(() => navItems.filter((item) => can(item.permission, user.value)))
const currentRole = computed(() => roleLabel(user.value))

const pageTitle = computed(() => {
  const item = visibleNav.value.find((n) => n.to === route.path)
  return item ? t(item.key) : t('dashboard')
})

const todayLabel = computed(() =>
  new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
)

const initials = computed(() =>
  (user.value?.username || 'U').slice(0, 2).toUpperCase()
)

async function handleLogout() {
  try {
    await api.logout()
  } catch (e) {
    // Always clear the local session, even if the API call fails.
    console.warn('Server logout failed:', e)
  }
  logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  padding: 18px;
  gap: 18px;
  max-width: 1560px;
  margin: 0 auto;
}

/* ---------- Sidebar ---------- */
.sidebar {
  width: var(--sidebar-width);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  position: sticky;
  top: 18px;
  height: calc(100vh - 36px);
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0 10px 22px;
}

.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: grid;
  place-items: center;
  background: var(--accent-gradient);
  box-shadow: 0 2px 10px var(--accent-glow);
  color: #fff;
}

.brand-name {
  font-size: 1.12rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: var(--radius-md);
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  border: 1px solid transparent;
  transition: all 0.18s ease;
}

.nav-link:hover {
  background: var(--row-hover);
  color: var(--text-primary);
}

.nav-link--active {
  background: var(--accent-soft);
  border-color: var(--accent-border);
  color: var(--accent-strong);
  box-shadow: var(--shadow-soft);
}

.nav-link__icon {
  display: inline-flex;
}

.sidebar__footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid var(--hairline);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border-soft);
  background: var(--glass-fill-c);
}

.user-card__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent);
  flex-shrink: 0;
}

.user-card__info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-card__name {
  font-size: 0.86rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-card__role {
  font-size: 0.72rem;
}

.sidebar__logout {
  width: 100%;
}

/* ---------- Content ---------- */
.content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.topbar {
  display: flex;
  align-items: center;
  padding: 16px 22px;
}

.topbar__title {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.topbar__date {
  font-size: 0.8rem;
}

.topbar__spacer {
  flex: 1;
}

@media (max-width: 900px) {
  .layout { flex-direction: column; }
  .sidebar {
    width: 100%;
    height: auto;
    position: static;
  }
  .sidebar__nav { flex-direction: row; flex-wrap: wrap; }
}
</style>
