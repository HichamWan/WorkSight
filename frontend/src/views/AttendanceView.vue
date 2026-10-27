<template>
  <div class="attendance">
    <section v-if="canRecord" class="glass checkin-panel">
      <div class="checkin-panel__title">
        <span>{{ t('manualAttendance') }}</span>
        <small class="muted">{{ t('manualAttendanceHint') }}</small>
      </div>
      <div class="checkin-panel__form">
        <div class="field checkin-field">
          <label class="field__label" for="checkin-emp">{{ t('employee') }}</label>
          <select id="checkin-emp" v-model="selectedEmployee" class="select">
            <option value="" disabled>{{ t('selectEmployee') }}</option>
            <option v-for="emp in employees" :key="emp.id" :value="emp.id">
              {{ emp.first_name }} {{ emp.last_name }} · {{ emp.employee_code }}
            </option>
          </select>
        </div>
        <button class="btn btn--primary" :disabled="!selectedEmployee || recording" @click="record('check-in')">
          {{ t('checkInAction') }}
        </button>
        <button class="btn btn--ghost" :disabled="!selectedEmployee || recording" @click="record('check-out')">
          {{ t('checkOutAction') }}
        </button>
      </div>
    </section>

    <section class="glass toolbar">
      <input v-model="query" class="input toolbar__search" type="text" :placeholder="t('searchByEmployee')" />
      <div class="date-filter">
        <label class="date-filter__label" for="start-date">{{ t('from') }}</label>
        <input id="start-date" v-model="startDate" class="input" type="date" />
      </div>
      <div class="date-filter">
        <label class="date-filter__label" for="end-date">{{ t('to') }}</label>
        <input id="end-date" v-model="endDate" class="input" type="date" />
      </div>
      <button class="btn btn--primary btn--sm" :disabled="loading" @click="load">{{ t('apply') }}</button>
      <button class="btn btn--ghost btn--sm" :disabled="loading" @click="resetFilters">{{ t('clear') }}</button>
      <span class="chip chip--accent" v-if="!loading">{{ rows.length }} {{ t('records') }}</span>
    </section>

    <section class="glass table-card">
      <div v-if="loading" class="empty muted">{{ t('loadingAttendance') }}</div>
      <div v-else-if="filtered.length === 0" class="empty muted">{{ t('noAttendance') }}</div>
      <template v-else>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th class="sortable" @click="toggleSort('employee_name')">Employee {{ arrow('employee_name') }}</th>
                <th class="sortable" @click="toggleSort('date')">Date {{ arrow('date') }}</th>
                <th>Check in</th>
                <th>Check out</th>
                <th class="sortable" @click="toggleSort('worked_hours')">Worked {{ arrow('worked_hours') }}</th>
                <th>Overtime</th>
                <th>Undertime</th>
                <th class="sortable" @click="toggleSort('status')">Status {{ arrow('status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pageRows" :key="row.id">
                <td class="strong">{{ row.employee_name }}</td>
                <td>{{ row.date }}</td>
                <td>{{ formatTime(row.check_in) }}</td>
                <td>{{ formatTime(row.check_out) }}</td>
                <td>{{ row.worked_hours != null ? row.worked_hours + ' h' : '—' }}</td>
                <td>
                  <span v-if="row.overtime_hours > 0" class="chip chip--warning">+{{ row.overtime_hours }} h</span>
                  <span v-else class="muted">—</span>
                </td>
                <td>
                  <span v-if="row.undertime_hours > 0" class="chip chip--danger">−{{ row.undertime_hours }} h</span>
                  <span v-else class="muted">—</span>
                </td>
                <td>
                  <span class="chip" :class="row.status === 'on_time' ? 'chip--success' : 'chip--warning'">
                    {{ formatStatus(row.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager :page="page" :total-pages="totalPages" :total="total" @change="setPage" />
      </template>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { can } from '../roles'
import { useAuth } from '../auth'
import { useTable } from '../table'
import { useI18n } from '../i18n'
import { notify } from '../toast'
import Pager from '../components/Pager.vue'

const { user } = useAuth()
const { t } = useI18n()
const canRecord = computed(() => can('recordAttendance', user.value))

const rows = ref([])
const employees = ref([])
const loading = ref(true)
const query = ref('')
const startDate = ref('')
const endDate = ref('')
const selectedEmployee = ref('')
const recording = ref(false)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) => r.employee_name?.toLowerCase().includes(q))
})

const { page, totalPages, total, paged: pageRows, sortKey, sortDir, toggleSort, setPage } = useTable(filtered, {
  pageSize: 12,
  initialSort: { key: 'date', dir: 'desc' }
})

function arrow(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? '▲' : '▼'
}

function formatStatus(status) {
  return (status || '').replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value).slice(0, 8)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function resetFilters() {
  startDate.value = ''
  endDate.value = ''
  query.value = ''
  load()
}

async function load() {
  loading.value = true
  try {
    const res = await api.attendance({
      start_date: startDate.value,
      end_date: endDate.value
    })
    rows.value = res.attendance || []
  } catch (e) {
    notify(e.message || 'Could not load attendance', 'error')
    rows.value = []
  } finally {
    loading.value = false
  }
}

async function loadEmployees() {
  try {
    const res = await api.employees()
    employees.value = res.employees || []
  } catch (e) {
    console.error('Failed to load employees for check-in:', e)
  }
}

async function record(kind) {
  if (!selectedEmployee.value) return
  recording.value = true
  try {
    const fn = kind === 'check-in' ? api.checkIn : api.checkOut
    await fn({
      employee_id: Number(selectedEmployee.value),
      timestamp: new Date().toISOString()
    })
    notify(`Check-${kind} recorded`, 'success')
    await load()
  } catch (e) {
    notify(e.message || `${kind} failed`, 'error')
  } finally {
    recording.value = false
  }
}

onMounted(() => {
  load()
  loadEmployees()
})
</script>

<style scoped>
.attendance {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.checkin-panel {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 18px 22px;
  flex-wrap: wrap;
}

.checkin-panel__title {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-weight: 700;
  min-width: 200px;
}

.checkin-panel__title small {
  font-weight: 500;
  font-size: 0.78rem;
}

.checkin-panel__form {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  flex: 1;
  flex-wrap: wrap;
  min-width: 0;
}

.checkin-field {
  min-width: 220px;
  flex: 1;
  max-width: 320px;
}

.toolbar {
  display: flex;
  gap: 14px;
  padding: 14px 18px;
  align-items: center;
  flex-wrap: wrap;
}

.toolbar__search {
  max-width: 260px;
}

.date-filter {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-filter__label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.date-filter .input {
  padding: 8px 12px;
}

.table-card {
  padding: 10px 18px 18px;
}

.empty {
  padding: 48px;
  text-align: center;
  font-size: 0.92rem;
}

.strong {
  color: var(--text-primary);
  font-weight: 600;
}

.sortable {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.sortable:hover { color: var(--accent); }

@media (max-width: 700px) {
  .checkin-panel { flex-direction: column; align-items: stretch; }
}
</style>
