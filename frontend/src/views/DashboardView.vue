<template>
  <div class="dashboard">
    <!-- Stat cards -->
    <section class="stats">
      <div v-for="stat in statCards" :key="stat.label" class="stat glass">
        <div class="stat__icon" :class="`stat__icon--${stat.tone}`" v-html="stat.icon"></div>
        <div class="stat__body">
          <span class="stat__value">{{ stat.value }}</span>
          <span class="stat__label muted">{{ stat.label }}</span>
        </div>
      </div>
    </section>

    <div class="grid">
      <!-- Today overview -->
      <section class="panel">
        <h2 class="panel__title">Today</h2>
        <div class="today">
          <div class="today__ring">
            <svg viewBox="0 0 120 120" width="130" height="130">
              <circle cx="60" cy="60" r="52" fill="none" class="ring-track" stroke-width="11" />
              <circle
                cx="60" cy="60" r="52" fill="none"
                stroke="var(--accent)" stroke-width="11" stroke-linecap="round"
                :stroke-dasharray="`${checkedInPct * 3.267} 327`"
                transform="rotate(-90 60 60)"
              />
              <text x="60" y="58" text-anchor="middle" font-size="20" font-weight="700" class="ring-value">
                {{ checkedInPct }}%
              </text>
              <text x="60" y="76" text-anchor="middle" font-size="10" class="ring-label">checked in</text>
            </svg>
          </div>
          <ul class="today__list">
            <li class="today__row">
              <span class="muted">Checked in</span>
              <strong>{{ today.checked_in ?? '—' }}</strong>
            </li>
            <li class="today__row">
              <span class="muted">Not checked in</span>
              <strong>{{ today.not_checked_in ?? '—' }}</strong>
            </li>
            <li class="today__row">
              <span class="muted">On time</span>
              <strong class="text-success">{{ today.on_time ?? '—' }}</strong>
            </li>
            <li class="today__row">
              <span class="muted">Late</span>
              <strong class="text-warning">{{ today.late ?? '—' }}</strong>
            </li>
          </ul>
        </div>
      </section>

      <!-- Attendance trend -->
      <section class="panel">
        <h2 class="panel__title">Attendance trend</h2>
        <TrendChart :trend="trend" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import TrendChart from '../components/TrendChart.vue'

const summary = ref({})
const today = ref({})
const trend = ref([])

const statCards = computed(() => [
  {
    label: 'Total employees',
    value: summary.value.total_employees ?? '—',
    tone: 'accent',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/></svg>'
  },
  {
    label: 'Present today',
    value: summary.value.present ?? '—',
    tone: 'success',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
  },
  {
    label: 'Late arrivals',
    value: summary.value.late ?? '—',
    tone: 'warning',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
  },
  {
    label: 'Overtime hours',
    value: summary.value.overtime ?? '—',
    tone: 'accent',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><circle cx="12" cy="12" r="6"/></svg>'
  }
])

const checkedInPct = computed(() => {
  const total = today.value.total_employees
  if (!total) return 0
  return Math.round(((today.value.checked_in ?? 0) / total) * 100)
})

onMounted(async () => {
  try {
    const [s, t, a] = await Promise.all([
      api.dashboardSummary(),
      api.dashboardToday(),
      api.dashboardAnalytics()
    ])
    summary.value = s
    today.value = t
    trend.value = a.attendance_trend || []
  } catch (e) {
    console.error('Dashboard load failed:', e)
  }
})
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px 22px;
}

.stat__icon {
  width: 40px;
  height: 40px;
  border-radius: 9px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border: 1px solid var(--border);
}

.stat__icon--accent { background: var(--accent-soft); color: var(--accent); }
.stat__icon--success { background: var(--success-soft); color: var(--success); }
.stat__icon--warning { background: var(--warning-soft); color: var(--warning); }

.stat__body {
  display: flex;
  flex-direction: column;
}

.stat__value {
  font-size: 1.55rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.stat__label {
  font-size: 0.8rem;
  font-weight: 500;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 16px;
}

.panel {
  padding: 24px 26px;
}

.panel__title {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 18px;
}

/* Today panel */
.today {
  display: flex;
  align-items: center;
  gap: 30px;
  flex-wrap: wrap;
}

.today__list {
  list-style: none;
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.today__row {
  display: flex;
  justify-content: space-between;
  padding: 9px 4px;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(163, 177, 198, 0.18);
}

.today__row:last-child { border-bottom: none; }

.text-success { color: var(--success); }
.text-warning { color: var(--warning); }

</style>
