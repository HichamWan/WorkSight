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
      <section class="glass panel">
        <h2 class="panel__title">Today</h2>
        <div class="today">
          <div class="today__ring">
            <svg viewBox="0 0 120 120" width="130" height="130">
              <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(163,177,198,0.35)" stroke-width="11" />
              <circle
                cx="60" cy="60" r="52" fill="none"
                stroke="url(#ringGrad)" stroke-width="11" stroke-linecap="round"
                :stroke-dasharray="`${checkedInPct * 3.267} 327`"
                transform="rotate(-90 60 60)"
              />
              <defs>
                <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#5b7cff" />
                  <stop offset="100%" stop-color="#2f4ce0" />
                </linearGradient>
              </defs>
              <text x="60" y="58" text-anchor="middle" font-size="20" font-weight="700" fill="#232a35">
                {{ checkedInPct }}%
              </text>
              <text x="60" y="76" text-anchor="middle" font-size="10" fill="#8b95a3">checked in</text>
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
      <section class="glass panel">
        <h2 class="panel__title">Attendance trend</h2>
        <div class="trend">
          <div v-for="day in trend" :key="day.date" class="trend__day">
            <div class="trend__bars">
              <div class="trend__bar trend__bar--present" :style="barStyle(day.present)" :title="`Present: ${day.present}`"></div>
              <div class="trend__bar trend__bar--late" :style="barStyle(day.late, 60)" :title="`Late: ${day.late}`"></div>
              <div class="trend__bar trend__bar--absent" :style="barStyle(day.absent, 60)" :title="`Absent: ${day.absent}`"></div>
            </div>
            <span class="trend__date muted">{{ shortDate(day.date) }}</span>
          </div>
        </div>
        <div class="legend">
          <span class="legend__item"><i class="dot dot--present"></i>Present</span>
          <span class="legend__item"><i class="dot dot--late"></i>Late</span>
          <span class="legend__item"><i class="dot dot--absent"></i>Absent</span>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

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

function barStyle(value, max = 60) {
  return { height: `${Math.max(6, Math.min(100, (value / max) * 100))}%` }
}

function shortDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

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
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.65);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
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

/* Trend panel */
.trend {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 160px;
  margin-bottom: 12px;
}

.trend__day {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  height: 100%;
}

.trend__bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  flex: 1;
}

.trend__bar {
  width: 14px;
  border-radius: 7px 7px 3px 3px;
  transition: height 0.4s ease;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
}

.trend__bar--present { background: linear-gradient(180deg, #7c93ff, #3d5bee); }
.trend__bar--late { background: linear-gradient(180deg, #ffc46b, #d9820b); }
.trend__bar--absent { background: linear-gradient(180deg, #c3ccdb, #9aa6b8); }

.trend__date { font-size: 0.74rem; }

.legend {
  display: flex;
  gap: 18px;
  padding-top: 12px;
  border-top: 1px solid rgba(163, 177, 198, 0.2);
}

.legend__item {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.dot--present { background: #3d5bee; }
.dot--late { background: #d9820b; }
.dot--absent { background: #9aa6b8; }
</style>
