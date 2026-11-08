<template>
  <div class="depts">
    <!-- Summary strip -->
    <section class="stats">
      <div v-for="card in summaryCards" :key="card.label" class="stat glass">
        <div class="stat__icon" :class="`stat__icon--${card.tone}`" v-html="card.icon"></div>
        <div class="stat__body">
          <span class="stat__value">{{ card.value }}</span>
          <span class="stat__label muted">{{ card.label }}</span>
        </div>
      </div>
    </section>

    <!-- Department cards -->
    <section class="depts__grid">
      <article v-for="d in departments" :key="d.name" class="glass dept-card">
        <header class="dept-card__head">
          <h3 class="dept-card__name">{{ d.name }}</h3>
          <span class="chip chip--accent">{{ d.headcount }} {{ t('members') }}</span>
        </header>

        <div class="dept-card__rate">
          <div class="dept-card__bar">
            <div class="dept-card__fill" :style="{ width: d.rate + '%' }"></div>
          </div>
          <span class="dept-card__pct">{{ d.rate }}%</span>
        </div>

        <dl class="dept-card__meta">
          <div><dt class="muted">{{ t('presentToday') }}</dt><dd>{{ d.present }}</dd></div>
          <div><dt class="muted">{{ t('lateArrivals') }}</dt><dd>{{ d.late }}</dd></div>
          <div><dt class="muted">{{ t('avgHours') }}</dt><dd>{{ d.avgHours }} h</dd></div>
          <div><dt class="muted">{{ t('faceId') }}</dt><dd>{{ d.faceRegistered }}/{{ d.headcount }}</dd></div>
        </dl>
      </article>

      <div v-if="!loading && !departments.length" class="glass empty muted">
        {{ t('noDepartments') }}
      </div>
    </section>

    <!-- Breakdown table -->
    <section class="glass table-card">
      <div class="table-card__head">
        <h3 class="panel__title">{{ t('departmentBreakdown') }}</h3>
        <span class="chip chip--accent">{{ departments.length }} {{ t('departments') }}</span>
      </div>

      <div v-if="loading" class="empty muted">{{ t('loadingDepartments') }}</div>
      <div v-else-if="!departments.length" class="empty muted">{{ t('noDepartments') }}</div>
      <template v-else>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th class="sortable" @click="toggleSort('name')">{{ t('department') }} {{ arrow('name') }}</th>
                <th class="sortable" @click="toggleSort('headcount')">{{ t('headcount') }} {{ arrow('headcount') }}</th>
                <th class="sortable" @click="toggleSort('present')">{{ t('presentToday') }} {{ arrow('present') }}</th>
                <th class="sortable" @click="toggleSort('late')">{{ t('lateArrivals') }} {{ arrow('late') }}</th>
                <th class="sortable" @click="toggleSort('avgHours')">{{ t('avgHours') }} {{ arrow('avgHours') }}</th>
                <th class="sortable" @click="toggleSort('rate')">{{ t('attendanceRate') }} {{ arrow('rate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in paged" :key="d.name">
                <td>{{ d.name }}</td>
                <td>{{ d.headcount }}</td>
                <td>{{ d.present }}</td>
                <td>
                  <span v-if="d.late > 0" class="chip chip--warning">{{ d.late }}</span>
                  <span v-else class="muted">0</span>
                </td>
                <td>{{ d.avgHours }} h</td>
                <td>
                  <span class="chip" :class="rateTone(d.rate)">{{ d.rate }}%</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager
          v-if="totalPages > 1"
          :page="page"
          :total-pages="totalPages"
          :total="total"
          @change="setPage"
        />
      </template>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../i18n'
import { useTable } from '../table'
import { useToast } from '../toast'
import Pager from '../components/Pager.vue'

const { t } = useI18n()
const toast = useToast()

const employees = ref([])
const attendance = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [empRes, attRes] = await Promise.all([api.employees(), api.attendance({})])
    employees.value = empRes?.employees || []
    const data = attRes?.attendance ?? attRes?.records ?? attRes
    attendance.value = Array.isArray(data) ? data : []
  } catch (e) {
    toast.error(e.message)
  } finally {
    loading.value = false
  }
})

const todayStr = new Date().toISOString().slice(0, 10)

const departments = computed(() => {
  const map = new Map()

  for (const e of employees.value) {
    const name = e.department || t('unassigned')
    if (!map.has(name)) {
      map.set(name, {
        name,
        headcount: 0,
        present: 0,
        late: 0,
        faceRegistered: 0,
        hoursTotal: 0,
        hoursCount: 0,
        rate: 0,
        avgHours: 0
      })
    }
    const d = map.get(name)
    d.headcount += 1
    if (e.face_registered) d.faceRegistered += 1
  }

  for (const a of attendance.value) {
    const emp = employees.value.find((e) => e.id === a.employee_id)
    if (!emp) continue
    const d = map.get(emp.department || t('unassigned'))
    if (!d) continue

    if (typeof a.worked_hours === 'number') {
      d.hoursTotal += a.worked_hours
      d.hoursCount += 1
    }
    if (a.date === todayStr) {
      if (a.check_in) d.present += 1
      if ((a.status || '').toLowerCase().includes('late')) d.late += 1
    }
  }

  for (const d of map.values()) {
    d.avgHours = d.hoursCount ? Math.round((d.hoursTotal / d.hoursCount) * 10) / 10 : 0
    d.rate = d.headcount ? Math.round((d.present / d.headcount) * 100) : 0
  }

  return [...map.values()].sort((a, b) => b.headcount - a.headcount)
})

const totalHeadcount = computed(() => departments.value.reduce((sum, d) => sum + d.headcount, 0))
const totalPresent = computed(() => departments.value.reduce((sum, d) => sum + d.present, 0))
const overallRate = computed(() =>
  totalHeadcount.value ? Math.round((totalPresent.value / totalHeadcount.value) * 100) : 0
)

const summaryCards = computed(() => [
  {
    label: t('departments'),
    value: departments.value.length,
    tone: 'accent',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6"/></svg>'
  },
  {
    label: t('headcount'),
    value: totalHeadcount.value,
    tone: 'neutral',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/></svg>'
  },
  {
    label: t('presentToday'),
    value: totalPresent.value,
    tone: 'success',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
  },
  {
    label: t('attendanceRate'),
    value: `${overallRate.value}%`,
    tone: 'warning',
    icon: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m7 14 4-4 3 3 5-6"/></svg>'
  }
])

const { page, totalPages, paged, total, toggleSort, setPage, sortKey, sortDir } = useTable(
  departments,
  { pageSize: 8, initialSort: { key: 'headcount', dir: 'desc' } }
)

function arrow(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? '↑' : '↓'
}

function rateTone(rate) {
  if (rate >= 80) return 'chip--success'
  if (rate >= 50) return 'chip--warning'
  return 'chip--danger'
}
</script>

<style scoped>
.depts { display: flex; flex-direction: column; gap: 18px; }

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
}

.stat__icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  background: var(--accent-soft);
  color: var(--accent-strong);
  flex-shrink: 0;
}
.stat__icon--success { background: var(--success-soft); color: var(--success); }
.stat__icon--warning { background: var(--warning-soft); color: var(--warning); }
.stat__icon--neutral { background: var(--surface-2); color: var(--text-2); }

.stat__body { display: flex; flex-direction: column; min-width: 0; }
.stat__value { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; }
.stat__label { font-size: 0.78rem; }

.depts__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.dept-card { padding: 18px; }
.dept-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 14px;
}
.dept-card__name { font-size: 0.95rem; font-weight: 700; }

.dept-card__rate {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.dept-card__bar {
  flex: 1;
  height: 7px;
  border-radius: var(--radius-pill);
  background: var(--surface-2);
  border: 1px solid var(--hairline);
  overflow: hidden;
}
.dept-card__fill {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: var(--radius-pill);
  transition: width 0.4s ease;
}
.dept-card__pct { font-size: 0.8rem; font-weight: 700; min-width: 38px; text-align: end; }

.dept-card__meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.dept-card__meta div { display: flex; flex-direction: column; gap: 2px; }
.dept-card__meta dt { font-size: 0.72rem; }
.dept-card__meta dd { margin: 0; font-size: 0.92rem; font-weight: 600; }

.table-card { padding: 20px; }
.table-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.panel__title { font-size: 0.95rem; font-weight: 700; }

.empty { padding: 36px; text-align: center; font-size: 0.88rem; }

.sortable { cursor: pointer; user-select: none; }
</style>
