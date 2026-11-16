<template>
  <div class="bell" ref="root">
    <button
      class="btn btn--icon bell__btn"
      :title="t('notifications')"
      aria-label="Notifications"
      @click="toggleBell"
    >
      <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.7 21a2 2 0 0 1-3.4 0" />
      </svg>
      <span v-if="unread > 0" :key="unread" class="bell__badge">{{ unread > 99 ? '99+' : unread }}</span>
    </button>

    <transition name="bell-pop">
      <div v-if="open" class="bell__menu glass glass--strong">
        <div class="bell__head">
          <span class="bell__title">{{ t('notifications') }}</span>
          <div class="bell__head-actions">
            <span v-if="unread" class="chip chip--accent">{{ unread }}</span>
            <button
              v-if="unread"
              type="button"
              class="bell__mark-all"
              @click.stop="markAllAlertsRead"
            >
              {{ t('markAllRead') }}
            </button>
          </div>
        </div>

        <div v-if="loading && !items.length" class="bell__empty muted">{{ t('loadingAlerts') }}</div>
        <div v-else-if="!items.length" class="bell__empty muted">{{ t('noNotifications') }}</div>

        <ul v-else class="bell__list">
          <li
            v-for="a in items.slice(0, 8)"
            :key="a.key || a.id"
            class="bell__item"
            :class="{
              'bell__item--clickable': canViewAlerts,
              'bell__item--unread': !a.read
            }"
            role="button"
            tabindex="0"
            :title="a.employee_id ? t('viewProfile') : t('viewAll')"
            @click="openAlert(a)"
            @keydown.enter.prevent="openAlert(a)"
            @keydown.space.prevent="openAlert(a)"
          >
            <span class="bell__dot" :class="a.read ? 'bell__dot--read' : dotClass(a)"></span>
            <span class="bell__text">
              <span class="bell__name">{{ alertName(a) }}</span>
              <span class="bell__meta muted">{{ alertMeta(a) }}</span>
            </span>
            <svg class="bell__chevron" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m9 18 6-6-6-6" />
            </svg>
          </li>
        </ul>

        <router-link v-if="canViewAlerts" to="/alerts" class="bell__footer" @click="open = false">
          {{ t('viewAllAlerts') }}
        </router-link>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../i18n'
import { useAuth } from '../auth'
import { can } from '../roles'
import {
  alerts as items,
  unread,
  loading,
  refreshAlerts,
  markAlertsRead,
  markAllAlertsRead
} from '../alertsStore'

const router = useRouter()
const { t } = useI18n()
const { user } = useAuth()
const open = ref(false)
const root = ref(null)

const canViewAlerts = computed(() => can('viewAlerts', user.value))

function dotClass(a) {
  const type = (a.type || a.category || '').toLowerCase()
  if (type.includes('late')) return 'bell__dot--warning'
  if (type.includes('under')) return 'bell__dot--danger'
  return 'bell__dot--accent'
}

function alertName(a) {
  return a.employee_name || a.name || a.title || a.message || `#${a.employee_id ?? ''}`
}

function alertMeta(a) {
  // Prefer the alert message (e.g. "worked 2.5h overtime"), fall back to its type.
  const type = (a.type || a.category || 'alert').replace(/_/g, ' ')
  return a.message && a.message !== alertName(a) ? a.message : type
}

function toggleBell() {
  const next = !open.value
  open.value = next
  if (next) refreshAlerts()
}

function openAlert(a) {
  if (!canViewAlerts.value) return
  // Mark as read first so the badge drops immediately.
  if (a && !a.read) markAlertsRead([a.key || a.id])
  open.value = false
  if (a?.employee_id) router.push(`/employees/${a.employee_id}`)
  else router.push('/alerts')
}

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}

function onKeydown(e) {
  if (e.key === 'Escape') open.value = false
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  document.addEventListener('keydown', onKeydown)
  if (canViewAlerts.value) refreshAlerts()
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.bell { position: relative; display: inline-block; }

.bell__btn { position: relative; }

.bell__badge {
  position: absolute;
  top: -5px;
  inset-inline-end: -6px;
  min-width: 17px;
  height: 17px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--accent-gradient);
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  line-height: 1;
  display: grid;
  place-items: center;
  box-shadow: 0 2px 6px var(--accent-glow);
  animation: badge-pop 0.28s ease;
}

@keyframes badge-pop {
  0% { transform: scale(0.6); opacity: 0.4; }
  60% { transform: scale(1.15); }
  100% { transform: scale(1); opacity: 1; }
}

.bell__menu {
  position: absolute;
  top: calc(100% + 6px);
  inset-inline-end: 0;
  width: 320px;
  padding: 12px;
  /* Opaque surface so charts/cards never bleed through the panel */
  background: var(--surface-solid);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md), 0 24px 50px -28px rgba(0, 0, 0, 0.75);
  z-index: 400;
  cursor: default;
}

.bell__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 0 4px 10px;
  border-bottom: 1px solid var(--hairline);
}

.bell__title { font-size: 0.86rem; font-weight: 700; }

.bell__head-actions { display: flex; align-items: center; gap: 8px; }

.bell__mark-all {
  border: none;
  background: none;
  padding: 0;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--accent-strong);
  cursor: pointer;
  text-decoration: underline;
  white-space: nowrap;
}
.bell__mark-all:hover { color: var(--accent); }

.bell__list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 300px;
  overflow-y: auto;
}

.bell__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: var(--radius-sm);
  border-bottom: 1px solid var(--hairline-2);
  transition: background 0.15s ease, transform 0.15s ease;
  outline: none;
}

.bell__item:last-child { border-bottom: none; }

.bell__item--unread { background: var(--accent-soft); }
.bell__item--unread .bell__name { font-weight: 700; }

.bell__item--clickable { cursor: pointer; }
.bell__item--clickable:hover { background: var(--row-hover); transform: translateX(2px); }
.bell__item--clickable:active { transform: scale(0.99); }
.bell__item--clickable:focus-visible {
  box-shadow: 0 0 0 2px var(--accent-border);
  background: var(--accent-soft);
}

.bell__chevron {
  flex-shrink: 0;
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.bell__item--clickable:hover .bell__chevron { opacity: 1; transform: translateX(2px); }

.bell__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
  background: var(--accent);
}
.bell__dot--warning { background: var(--warning); }
.bell__dot--danger { background: var(--danger); }
.bell__dot--accent { background: var(--accent); }
.bell__dot--read { background: var(--hairline); }

.bell__text { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
.bell__name { font-size: 0.84rem; font-weight: 600; }
.bell__meta {
  font-size: 0.72rem;
  text-transform: capitalize;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bell__empty { padding: 18px 4px; text-align: center; font-size: 0.84rem; }

.bell__footer {
  display: block;
  margin-top: 8px;
  padding: 9px;
  text-align: center;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent-strong);
  text-decoration: none;
  border-top: 1px solid var(--hairline);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  transition: background 0.15s ease;
}
.bell__footer:hover { background: var(--row-hover); }

.bell-pop-enter-active,
.bell-pop-leave-active { transition: opacity 0.16s ease, transform 0.16s ease; }
.bell-pop-enter-from,
.bell-pop-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
