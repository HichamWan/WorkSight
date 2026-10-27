<template>
  <div class="alerts">
    <section class="glass table-card">
      <div class="table-card__head">
        <h2 class="panel__title">{{ activeLabel }} alerts</h2>
        <span class="chip" :class="alerts.length ? 'chip--warning' : 'chip--success'">
          {{ alerts.length }} total
        </span>
      </div>

      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          class="tab"
          :class="{ 'tab--active': activeTab === tab.key }"
          @click="selectTab(tab.key)"
        >
          {{ tab.key === 'all' ? t('all') : t(tab.key2) }}
        </button>
      </div>

      <p v-if="error" class="banner banner--error">{{ error }}</p>

      <div v-if="loading" class="empty muted">Loading alerts…</div>
      <div v-else-if="alerts.length === 0" class="empty muted">No alerts — everything looks good.</div>
      <ul v-else class="alert-list">
        <li v-for="alert in alerts" :key="alert.id" class="alert-item glass--soft">
          <div class="alert-item__icon" :class="toneClass(alert.type)" v-html="icon"></div>
          <div class="alert-item__body">
            <strong>{{ alert.employee_name }}</strong>
            <span class="muted">{{ alert.message }}</span>
          </div>
          <div class="alert-item__meta">
            <span class="chip" :class="toneClass(alert.type)">{{ formatType(alert.type) }}</span>
            <span class="muted alert-item__date">{{ alert.date }}</span>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../i18n'

const { t } = useI18n()

const alerts = ref([])
const loading = ref(true)
const error = ref('')
const activeTab = ref('all')

const tabs = [
  { key: 'all', key2: 'all', load: () => api.alerts() },
  { key: 'overtime', key2: 'overtime', load: () => api.alertsOvertime() },
  { key: 'under-time', key2: 'undertime', load: () => api.alertsUndertime() },
  { key: 'late', key2: 'late', load: () => api.alertsLate() }
]

const activeLabel = computed(
  () => (activeTab.value === 'all' ? t('all') : t(activeTab.value.replace('-', '')))
)

const icon =
  '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>'

function toneClass(type) {
  if (type === 'overtime') return 'chip--warning'
  if (type === 'late') return 'chip--danger'
  if (type === 'under_time' || type === 'undertime') return 'chip--accent'
  return 'chip--accent'
}

function formatType(type) {
  return (type || 'info').replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const tab = tabs.find((t) => t.key === activeTab.value)
    const res = await tab.load()
    // The backend returns either { alerts: [...], total } or a bare array.
    alerts.value = Array.isArray(res) ? res : res.alerts || []
  } catch (e) {
    error.value = e.message || 'Could not load alerts'
    alerts.value = []
  } finally {
    loading.value = false
  }
}

function selectTab(key) {
  if (key === activeTab.value) return
  activeTab.value = key
  load()
}

onMounted(load)
</script>

<style scoped>
.table-card {
  padding: 22px 24px;
}

.table-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel__title {
  font-size: 0.95rem;
  font-weight: 700;
}

.tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.tab {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
}

.tab:hover {
  background: var(--row-hover);
  color: var(--text-primary);
}

.tab--active {
  background: var(--accent-soft);
  border-color: var(--accent-border);
  color: var(--accent-strong);
}

.banner {
  padding: 12px 18px;
  border-radius: var(--radius-sm);
  font-size: 0.87rem;
  font-weight: 600;
  margin-bottom: 14px;
}

.banner--error {
  background: var(--danger-soft);
  color: var(--danger);
}

.empty {
  padding: 48px;
  text-align: center;
  font-size: 0.92rem;
}

.alert-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 15px 18px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border-soft);
  background: var(--glass-bg-soft);
}

.alert-item__icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border: 1px solid var(--border);
}

.alert-item__icon.chip--warning { background: var(--warning-soft); color: var(--warning); }
.alert-item__icon.chip--danger { background: var(--danger-soft); color: var(--danger); }
.alert-item__icon.chip--accent { background: var(--accent-soft); color: var(--accent); }

.alert-item__body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.alert-item__body strong {
  color: var(--text-primary);
  font-weight: 600;
}

.alert-item__body .muted {
  font-size: 0.84rem;
}

.alert-item__meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.alert-item__date {
  font-size: 0.78rem;
}
</style>
