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
        <h2 class="panel__title">{{ t('today') }}</h2>
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
              <text x="60" y="76" text-anchor="middle" font-size="10" class="ring-label">{{ t('checkedInPct') }}</text>
            </svg>
          </div>
          <ul class="today__list">
            <li class="today__row">
              <span class="muted">{{ t('checkedIn') }}</span>
              <strong>{{ today.checked_in ?? '—' }}</strong>
            </li>
            <li class="today__row">
              <span class="muted">{{ t('notCheckedIn') }}</span>
              <strong>{{ today.not_checked_in ?? '—' }}</strong>
            </li>
            <li class="today__row">
              <span class="muted">{{ t('onTime') }}</span>
              <strong class="text-success">{{ today.on_time ?? '—' }}</strong>
            </li>
            <li class="today__row">
              <span class="muted">{{ t('late') }}</span>
              <strong class="text-warning">{{ today.late ?? '—' }}</strong>
            </li>
          </ul>
        </div>
      </section>

      <!-- Attendance trend -->
      <section class="panel">
        <h2 class="panel__title">{{ t('attendanceTrend') }}</h2>
        <TrendChart :trend="trend" />
      </section>
    </div>

    <div class="grid grid--lower">
      <!-- Work hours leaderboard -->
      <section class="panel">
        <h2 class="panel__title">{{ t('workHoursBoard') }}</h2>
        <div v-if="workHours.length === 0" class="empty muted">{{ t('noData') }}</div>
        <ul v-else class="board">
          <li v-for="(w, i) in topWorkHours" :key="w.employee_id" class="board__row">
            <span class="board__rank" :class="{ 'board__rank--top': i === 0 }">{{ i + 1 }}</span>
            <span class="board__name">{{ w.employee_name }}</span>
            <div class="board__bar">
              <div class="board__fill" :style="{ width: boardPct(w) + '%' }"></div>
            </div>
            <span class="board__hours">{{ w.total_worked_hours }} h</span>
            <span v-if="w.total_overtime_hours > 0" class="chip chip--warning">+{{ w.total_overtime_hours }}</span>
          </li>
        </ul>
      </section>

      <!-- Recent activity -->
      <section class="panel">
        <h2 class="panel__title">{{ t('recentActivity') }}</h2>
        <div v-if="activity.length === 0" class="empty muted">{{ t('noActivity') }}</div>
        <ul v-else class="feed">
          <li v-for="a in activity" :key="a.id" class="feed__row">
            <span class="feed__dot" :class="`feed__dot--${activityTone(a.action)}`"></span>
            <div class="feed__body">
              <strong>{{ a.username }}</strong>
              <span class="muted">{{ activityText(a) }}</span>
            </div>
            <time class="muted feed__time">{{ feedTime(a.created_at) }}</time>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../i18n'
import TrendChart from '../components/TrendChart.vue'

const { t } = useI18n()

const summary = ref({})
const today = ref({})
const trend = ref([])
const workHours = ref([])
const activity = ref([])

const topWorkHours = computed(() =>
  [...workHours.value].sort((a, b) => b.total_worked_hours - a.total_worked_hours).slice(0, 5)
)

function boardPct(w) {
  const max = topWorkHours.value[0]?.total_worked_hours || 1
  return Math.max(6, Math.round((w.total_worked_hours / max) * 100))
}

const ACTIVITY_LABELS = {
  employee_created: 'actEmployeeCreated',
  employee_updated: 'actEmployeeUpdated',
  employee_deleted: 'actEmployeeDeleted',
  check_in: 'actCheckIn',
  face_enrolled: 'actFaceEnrolled',
  leave_requested: 'actLeaveRequested',
  leave_approved: 'actLeaveApproved',
  leave_rejected: 'actLeaveRejected'
}

function activityText(a) {
  const key = ACTIVITY_LABELS[a.action]
  return key ? `${t(key)} · ${a.detail}` : `${a.action} · ${a.detail}`
}

function activityTone(action) {
  if (action === 'employee_deleted' || action === 'leave_rejected') return 'danger'
  if (action.startsWith('leave') || action === 'employee_created') return 'accent'
  return 'success'
}

function feedTime(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const statCards = computed(() => [
  {
    label: t('totalEmployees'),
    value: summary.value.total_employees ?? '—',
    tone: 'accent',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/></svg>'
  },
  {
    label: t('presentToday'),
    value: summary.value.present ?? '—',
    tone: 'success',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
  },
  {
    label: t('lateArrivals'),
    value: summary.value.late ?? '—',
    tone: 'warning',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
  },
  {
    label: t('overtimeHours'),
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
    const [s, td, a, wh, act] = await Promise.all([
      api.dashboardSummary(),
      api.dashboardToday(),
      api.dashboardAnalytics(),
      api.workHours().catch(() => ({ work_hours: [] })),
      api.activity().catch(() => ({ activity: [] }))
    ])
    summary.value = s
    today.value = td
    trend.value = a.attendance_trend || []
    workHours.value = wh.work_hours || []
    activity.value = act.activity || []
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

/* Lower panels (work hours + activity) */
.grid--lower { margin-top: 0; }

.board { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.board__row { display: flex; align-items: center; gap: 12px; }
.board__rank {
  width: 24px; height: 24px; border-radius: 50%;
  display: grid; place-items: center;
  font-size: 0.72rem; font-weight: 700;
  background: var(--surface-2); color: var(--text-2);
  flex-shrink: 0;
}
.board__rank--top { background: var(--accent-gradient); color: #fff; }
.board__name { width: 110px; font-weight: 600; font-size: 0.86rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.board__bar {
  flex: 1; height: 7px; border-radius: var(--radius-pill);
  background: var(--surface-2); border: 1px solid var(--hairline);
  overflow: hidden;
}
.board__fill { height: 100%; background: var(--accent-gradient); border-radius: var(--radius-pill); }
.board__hours { font-weight: 700; font-size: 0.84rem; min-width: 52px; text-align: end; }

.feed { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
.feed__row {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--hairline);
}
.feed__row:last-child { border-bottom: none; }
.feed__dot {
  width: 9px; height: 9px; border-radius: 50%; margin-top: 6px; flex-shrink: 0;
  background: var(--success);
}
.feed__dot--danger { background: var(--danger); }
.feed__dot--accent { background: var(--accent); }
.feed__body { flex: 1; font-size: 0.85rem; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.feed__time { font-size: 0.74rem; white-space: nowrap; margin-top: 2px; }

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
