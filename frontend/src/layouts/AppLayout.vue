<template>
  <div class="layout">
    <aside class="sidebar glass glass--strong" :class="{ 'sidebar--collapsed': collapsed }">
      <router-link to="/" class="sidebar__brand sidebar__brand--link" :title="t('dashboard')">
        <div class="brand-mark">
          <img src="/logo-sm.png" alt="WorkSight" class="brand-mark__img" />
        </div>
        <span v-if="!collapsed" class="brand-name">WorkSight</span>
        <button class="btn btn--icon sidebar__collapse" :title="collapsed ? 'Expand' : 'Collapse'" @click.prevent.stop="toggleCollapse">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :style="collapsed ? 'transform: scaleX(-1)' : ''">
            <path d="m15 18-6-6 6-6" />
          </svg>
        </button>
      </router-link>

      <nav class="sidebar__nav">
        <router-link
          v-for="item in visibleNav"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ 'nav-link--active': isNavActive(item) }"
          :title="t(item.key)"
        >
          <span class="nav-link__icon" v-html="item.icon"></span>
          <span v-if="!collapsed" class="nav-link__label">{{ t(item.key) }}</span>
        </router-link>
      </nav>

      <div class="sidebar__footer">
        <div ref="userWrap" class="user-wrap">
          <button
            class="user-card glass--soft"
            :class="{ 'user-card--open': profileOpen }"
            :title="t('myProfile')"
            @click="toggleProfile"
          >
            <img
              v-if="avatarSrc"
              :src="avatarSrc"
              :alt="user?.username || 'User'"
              class="user-card__avatar user-card__avatar--photo"
            />
            <img
              v-else
              src="/logo-sm.png"
              alt="WorkSight"
              class="user-card__avatar user-card__avatar--default"
            />
            <div v-if="!collapsed" class="user-card__info">
              <span class="user-card__name">{{ user?.username || 'User' }}</span>
              <span class="user-card__role muted">{{ currentRole }}</span>
            </div>
            <svg
              v-if="!collapsed"
              class="user-card__chevron"
              :class="{ 'user-card__chevron--up': profileOpen }"
              viewBox="0 0 24 24" width="14" height="14" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            >
              <path d="m18 15-6-6-6 6" />
            </svg>
          </button>

          <transition name="profile-pop">
            <div v-if="profileOpen" class="profile-pop">
              <header class="profile-pop__head">
                <img
                  v-if="avatarSrc"
                  :src="avatarSrc"
                  :alt="user?.username || 'User'"
                  class="profile-pop__avatar profile-pop__avatar--photo"
                />
                <img
                  v-else
                  src="/logo-sm.png"
                  alt="WorkSight"
                  class="profile-pop__avatar profile-pop__avatar--default"
                />
                <div class="profile-pop__identity">
                  <strong class="profile-pop__name">{{ user?.username || 'User' }}</strong>
                  <span class="muted profile-pop__email">{{ user?.email || '—' }}</span>
                </div>
                <span class="chip chip--accent">{{ currentRole }}</span>
              </header>

              <dl class="profile-pop__grid">
                <div class="profile-pop__row">
                  <dt class="muted">{{ t('companyInfo') }}</dt>
                  <dd>{{ profile?.company?.name || '—' }}</dd>
                </div>
                <div class="profile-pop__row">
                  <dt class="muted">{{ t('employees') }}</dt>
                  <dd>{{ profile?.stats?.employees ?? '—' }}</dd>
                </div>
                <div class="profile-pop__row">
                  <dt class="muted">{{ t('pendingLeaves') }}</dt>
                  <dd>{{ profile?.stats?.pending_leaves ?? '—' }}</dd>
                </div>
                <div class="profile-pop__row">
                  <dt class="muted">{{ t('memberSince') }}</dt>
                  <dd>{{ memberSince }}</dd>
                </div>
              </dl>

              <div class="profile-pop__actions">
                <router-link to="/settings" class="btn btn--ghost btn--sm" @click="profileOpen = false">
                  {{ t('openSettings') }}
                </router-link>
                <button class="btn btn--ghost btn--sm" @click="toggleTheme">
                  {{ theme === 'dark' ? t('light') : t('dark') }}
                </button>
              </div>
            </div>
          </transition>
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
        <GlobalSearch />
        <NotificationsBell />
        <LanguageSwitcher />
        <ThemeToggle />
        <span
          class="chip"
          :class="health === 'ok' ? 'chip--success' : 'chip--danger'"
          :title="health === 'ok' ? t('connectionOk') : t('connectionFail')"
        >
          {{ health === 'ok' ? t('systemOnline') : t('connectionFail') }}
        </span>
      </header>

      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../auth'
import { useI18n } from '../i18n'
import { useTheme } from '../theme'
import { api } from '../api'
import { can, roleLabel } from '../roles'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import NotificationsBell from '../components/NotificationsBell.vue'
import GlobalSearch from '../components/GlobalSearch.vue'

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
  },
  {
    to: '/leaves',
    key: 'leaveRequests',
    permission: 'viewLeaves',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M8 2v4M16 2v4M3 9h18"/><path d="M12 12v5M9.5 14.5h5"/></svg>'
  },
  {
    to: '/departments',
    key: 'departments',
    permission: 'viewEmployees',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6"/></svg>'
  },
  {
    to: '/face',
    key: 'faceId',
    permission: 'recordAttendance',
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="3.2"/><path d="M9.5 10.2h.01M14.5 10.2h.01M9.8 15c.7.6 1.4.9 2.2.9s1.5-.3 2.2-.9"/></svg>'
  },
  {
    to: '/settings',
    key: 'settings',
    permission: null,
    icon: '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h.01a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.01a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.01a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
  }
]

const visibleNav = computed(() => navItems.filter((item) => can(item.permission, user.value)))
const currentRole = computed(() => roleLabel(user.value))

// Highlight the section a deep link belongs to (e.g. /employees/12 -> Employees),
// and never light up Dashboard for nested routes.
function isNavActive(item) {
  if (item.to === '/') return route.path === '/'
  return route.path === item.to || route.path.startsWith(`${item.to}/`)
}

const pageTitle = computed(() => {
  const item = visibleNav.value.find((n) => n.to === route.path)
  if (item) return t(item.key)
  if (route.name === 'employee-detail') return t('employeeProfile')
  return t('dashboard')
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

const avatarSrc = computed(() => api.avatarUrl(user.value?.avatar))

// Real-time health indicator (refreshed every 60s)
const health = ref('ok')
async function checkHealth() {
  try {
    const res = await api.health()
    health.value = res?.status === 'ok' ? 'ok' : 'fail'
  } catch {
    health.value = 'fail'
  }
}
const healthTimer = setInterval(checkHealth, 60000)
onBeforeUnmount(() => clearInterval(healthTimer))
checkHealth()

// Collapsible sidebar (persisted)
const COLLAPSE_KEY = 'worksight_sidebar_collapsed'
const collapsed = ref(localStorage.getItem(COLLAPSE_KEY) === '1')

function toggleCollapse() {
  collapsed.value = !collapsed.value
  localStorage.setItem(COLLAPSE_KEY, collapsed.value ? '1' : '0')
}

// ---------- Profile popover ----------
const { theme, toggleTheme } = useTheme()
const profileOpen = ref(false)
const profile = ref(null)
const userWrap = ref(null)

const memberSince = computed(() => {
  const raw = profile.value?.company?.created_at
  if (!raw) return '—'
  const d = new Date(raw)
  return Number.isNaN(d.getTime()) ? raw : d.toLocaleDateString()
})

async function loadProfile() {
  try {
    profile.value = await api.profile()
  } catch {
    profile.value = null
  }
}

function toggleProfile() {
  profileOpen.value = !profileOpen.value
  if (profileOpen.value) loadProfile()
}

function onDocClick(e) {
  if (userWrap.value && !userWrap.value.contains(e.target)) profileOpen.value = false
}

function onEsc(e) {
  if (e.key === 'Escape') profileOpen.value = false
}

onMounted(() => {
  document.addEventListener('click', onDocClick)
  document.addEventListener('keydown', onEsc)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onDocClick)
  document.removeEventListener('keydown', onEsc)
})

watch(() => route.path, () => { profileOpen.value = false })

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
  transition: width 0.22s ease;
}

.sidebar--collapsed {
  width: 72px;
  padding: 24px 10px;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0 10px 22px;
}

.sidebar__collapse {
  width: 26px;
  height: 26px;
  margin-inline-start: auto;
  border: none;
  background: transparent;
  color: var(--text-muted);
}
.sidebar__collapse:hover { color: var(--text); }

.sidebar--collapsed .sidebar__brand { flex-direction: column; padding-inline: 0; }
.sidebar--collapsed .sidebar__collapse { margin: 8px 0 0; }

.sidebar--collapsed .nav-link { justify-content: center; padding: 11px; }
.sidebar--collapsed .nav-link__icon { margin: 0; }

.sidebar--collapsed .user-card { justify-content: center; padding: 10px 6px; }
.sidebar--collapsed .user-card__info { display: none; }

.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #070d20;
  box-shadow: 0 2px 12px -2px var(--accent-glow);
  transition: transform 0.45s cubic-bezier(0.34, 1.4, 0.64, 1), box-shadow 0.3s ease;
  flex-shrink: 0;
}

.brand-mark__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.brand-mark:hover {
  transform: perspective(200px) rotateY(180deg) scale(1.05);
  box-shadow: 0 4px 18px -4px var(--accent-glow);
}

.brand-name {
  font-size: 1.12rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.sidebar__brand--link {
  text-decoration: none;
  color: inherit;
}
.sidebar__brand--link:hover .brand-name { color: var(--accent-strong); }

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
  background: var(--accent-soft);
  border-color: var(--accent-border);
  color: var(--text-primary);
  transform: translateX(5px) perspective(400px) rotateY(-4deg);
  box-shadow: var(--shadow-soft);
}

.nav-link--active {
  background: var(--accent-soft);
  border-color: var(--accent-border);
  color: var(--accent-strong);
  box-shadow: var(--shadow-soft);
}

.nav-link__icon {
  display: inline-flex;
  transition: transform 0.25s cubic-bezier(0.34, 1.4, 0.64, 1);
}

.nav-link:hover .nav-link__icon {
  transform: scale(1.2) rotate(-6deg);
}

.nav-link--active .nav-link__icon {
  transform: scale(1.12);
}

.sidebar__footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid var(--hairline);
}

.user-wrap { position: relative; }

.user-card {
  display: flex;
  align-items: center;
  gap: 11px;
  width: 100%;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border-soft);
  background: var(--glass-fill-c);
  cursor: pointer;
  text-align: start;
  transition: background 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
}

.user-card:hover,
.user-card--open {
  background: var(--accent-soft);
  border-color: var(--accent-border);
  box-shadow: var(--shadow-soft);
}

.user-card__chevron {
  margin-inline-start: auto;
  color: var(--text-muted);
  transition: transform 0.2s ease, color 0.2s ease;
  flex-shrink: 0;
}
.user-card:hover .user-card__chevron { color: var(--text); }
.user-card__chevron--up { transform: rotate(180deg); }

/* ---------- Profile popover ---------- */
.profile-pop {
  position: absolute;
  bottom: calc(100% + 10px);
  inset-inline-start: 0;
  width: 286px;
  padding: 14px;
  border-radius: var(--radius-md);
  background: var(--surface-solid);
  border: 1px solid var(--border-strong);
  box-shadow: var(--shadow-md), 0 26px 50px -28px rgba(0, 0, 0, 0.8);
  z-index: 400;
}

.profile-pop__head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--hairline);
}

.profile-pop__avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-gradient);
  box-shadow: 0 4px 14px -6px var(--accent-glow);
  flex-shrink: 0;
}

.profile-pop__identity { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.profile-pop__name { font-size: 0.9rem; }
.profile-pop__email { font-size: 0.74rem; overflow: hidden; text-overflow: ellipsis; }

.profile-pop__grid {
  display: flex;
  flex-direction: column;
  margin: 6px 0 10px;
}

.profile-pop__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 7px 0;
  font-size: 0.8rem;
  border-bottom: 1px solid var(--hairline-2);
}
.profile-pop__row:last-child { border-bottom: none; }
.profile-pop__row dd { margin: 0; font-weight: 600; text-align: end; }

.profile-pop__actions { display: flex; flex-wrap: wrap; gap: 8px; }
.profile-pop__actions .btn { flex: 1; justify-content: center; }

.profile-pop-enter-active,
.profile-pop-leave-active { transition: opacity 0.16s ease, transform 0.16s ease; }
.profile-pop-enter-from,
.profile-pop-leave-to { opacity: 0; transform: translateY(6px) scale(0.98); }

@media (prefers-reduced-motion: reduce) {
  .profile-pop-enter-active,
  .profile-pop-leave-active { transition: none; }
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

.user-card__avatar--photo,
.profile-pop__avatar--photo {
  object-fit: cover;
  border: 2px solid var(--accent-border);
}

/* Default avatar = WorkSight logo on a dark disc so the artwork never bleeds white */
.user-card__avatar--default,
.profile-pop__avatar--default {
  object-fit: cover;
  background: #070d20;
  border: 2px solid var(--border-strong);
  transform: scale(1.02);
}

.profile-pop__avatar--photo { width: 38px; height: 38px; }

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
  /* backdrop-filter creates a stacking context; keep the topbar (and its
     dropdown menus: notifications, search, language) above the page panels */
  position: relative;
  z-index: 100;
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
