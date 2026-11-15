<template>
  <div class="bell" ref="root">
    <button
      class="btn btn--icon bell__btn"
      :title="t('notifications')"
      aria-label="Notifications"
      @click="open = !open"
    >
      <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.7 21a2 2 0 0 1-3.4 0" />
      </svg>
      <span v-if="count > 0" class="bell__badge">{{ count > 9 ? '9+' : count }}</span>
    </button>

    <transition name="bell-pop">
      <div v-if="open" class="bell__menu glass glass--strong">
        <div class="bell__head">
          <span class="bell__title">{{ t('notifications') }}</span>
          <span v-if="count" class="chip chip--accent">{{ count }}</span>
        </div>

        <div v-if="loading" class="bell__empty muted">{{ t('loadingAlerts') }}</div>
        <div v-else-if="!items.length" class="bell__empty muted">{{ t('noNotifications') }}</div>

        <ul v-else class="bell__list">
          <li v-for="a in items.slice(0, 6)" :key="a.id" class="bell__item">
            <span class="bell__dot" :class="dotClass(a)"></span>
            <span class="bell__text">
              <span class="bell__name">{{ alertName(a) }}</span>
              <span class="bell__meta muted">{{ a.type || a.category || 'alert' }}</span>
            </span>
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
import { api } from '../api'
import { useI18n } from '../i18n'
import { useAuth } from '../auth'
import { can } from '../roles'

const { t } = useI18n()
const { user } = useAuth()
const open = ref(false)
const loading = ref(false)
const items = ref([])
const root = ref(null)

const canViewAlerts = computed(() => can('viewAlerts', user.value))

const count = computed(() => items.value.length)

function dotClass(a) {
  const type = (a.type || a.category || '').toLowerCase()
  if (type.includes('late')) return 'bell__dot--warning'
  if (type.includes('under')) return 'bell__dot--danger'
  return 'bell__dot--accent'
}

function alertName(a) {
  return a.employee_name || a.name || a.title || a.message || `#${a.employee_id ?? ''}`
}

async function load() {
  if (!canViewAlerts.value) return
  loading.value = true
  try {
    const res = await api.alerts()
    items.value = Array.isArray(res) ? res : res?.alerts || []
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  load()
})
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.bell { position: relative; display: inline-block; }

.bell__btn { position: relative; }

.bell__badge {
  position: absolute;
  top: -4px;
  inset-inline-end: -4px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: var(--accent-gradient);
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  display: grid;
  place-items: center;
  box-shadow: 0 2px 6px var(--accent-glow);
}

.bell__menu {
  position: absolute;
  top: calc(100% + 6px);
  inset-inline-end: 0;
  width: 300px;
  padding: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: 60;
}

.bell__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px 10px;
  border-bottom: 1px solid var(--hairline);
}

.bell__title { font-size: 0.86rem; font-weight: 700; }

.bell__list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 260px;
  overflow-y: auto;
}

.bell__item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 4px;
  border-bottom: 1px solid var(--hairline-2);
}

.bell__item:last-child { border-bottom: none; }

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

.bell__text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.bell__name { font-size: 0.84rem; font-weight: 600; }
.bell__meta { font-size: 0.72rem; text-transform: capitalize; }

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
