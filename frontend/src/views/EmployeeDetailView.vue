<template>
  <div class="detail">
    <button class="btn btn--ghost btn--sm back-link" @click="goBack">{{ t('backToEmployees') }}</button>

    <p v-if="error" class="banner banner--error">{{ error }}</p>

    <section v-if="loading" class="glass empty muted">{{ t('loadingEmployee') }}</section>

    <template v-else-if="employee">
      <section class="glass hero">
        <div class="hero__avatar">{{ initials(employee) }}</div>
        <div class="hero__meta">
          <h2 class="hero__name">{{ employee.first_name }} {{ employee.last_name }}</h2>
          <span class="muted">{{ employee.position }} · {{ employee.department }}</span>
          <div class="hero__chips">
            <span class="chip chip--accent">{{ employee.employee_code }}</span>
            <span class="chip" :class="employee.face_registered ? 'chip--success' : ''">
              {{ employee.face_registered ? t('faceRegistered') : t('faceNotSet') }}
            </span>
            <span class="chip">{{ employee.status || 'active' }}</span>
          </div>
        </div>
      </section>

      <section class="glass info-card">
        <h3 class="panel__title">{{ t('employeeDetails') }}</h3>
        <div class="info-grid">
          <div v-for="row in infoRows" :key="row.label" class="info-row">
            <span class="info-row__label">{{ row.label }}</span>
            <span class="info-row__value">{{ row.value || '—' }}</span>
          </div>
        </div>
      </section>

      <section class="glass table-card">
        <div class="table-card__head">
          <h3 class="panel__title">{{ t('attendanceHistory') }}</h3>
          <span class="chip chip--accent" v-if="!historyLoading">{{ history.length }} {{ t('records') }}</span>
        </div>

        <div v-if="historyLoading" class="empty muted">{{ t('loadingAttendance') }}</div>
        <div v-else-if="history.length === 0" class="empty muted">{{ t('noHistory') }}</div>
        <template v-else>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
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
    </template>

    <section v-else class="glass empty muted">Employee not found.</section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { useTable } from '../table'
import { useI18n } from '../i18n'
import Pager from '../components/Pager.vue'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()

const employee = ref(null)
const history = ref([])
const loading = ref(true)
const historyLoading = ref(true)
const error = ref('')

const { page, totalPages, total, paged: pageRows, sortKey, sortDir, toggleSort, setPage } = useTable(history, {
  pageSize: 8,
  initialSort: { key: 'date', dir: 'desc' }
})

const infoRows = computed(() => [
  { label: t('employeeCode'), value: employee.value?.employee_code },
  { label: t('email'), value: employee.value?.email },
  { label: t('phone'), value: employee.value?.phone },
  { label: t('department'), value: employee.value?.department },
  { label: t('position'), value: employee.value?.position },
  { label: t('status'), value: employee.value?.status },
  { label: t('memberSince'), value: formatDate(employee.value?.created_at) }
])

function initials(emp) {
  return `${emp.first_name?.[0] ?? ''}${emp.last_name?.[0] ?? ''}`.toUpperCase()
}

function arrow(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? '▲' : '▼'
}

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString()
}

function formatTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value).slice(0, 8)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatStatus(status) {
  return (status || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function goBack() {
  router.push({ name: 'employees' })
}

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    employee.value = await api.employee(id)
  } catch (e) {
    error.value = e.message || 'Could not load employee'
  } finally {
    loading.value = false
  }

  try {
    const res = await api.attendance({ employee_id: id })
    history.value = res.attendance || []
  } catch (e) {
    console.error('Failed to load employee history:', e)
  } finally {
    historyLoading.value = false
  }
})
</script>

<style scoped>
.detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.back-link {
  align-self: flex-start;
}

.hero {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 24px 26px;
  flex-wrap: wrap;
}

.hero__avatar {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-gradient);
  box-shadow: 0 2px 10px var(--accent-glow);
  flex-shrink: 0;
}

.hero__meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.hero__name {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.hero__chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.info-card {
  padding: 22px 26px;
}

.panel__title {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 14px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 2px 26px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 11px 0;
  font-size: 0.89rem;
  border-bottom: 1px solid var(--hairline-2);
}

.info-row__label { color: var(--text-muted); }
.info-row__value { font-weight: 600; text-align: end; word-break: break-word; }

.table-card {
  padding: 20px 22px 22px;
}

.table-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.sortable {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.sortable:hover { color: var(--accent); }

.strong { color: var(--text-primary); }

.empty {
  padding: 48px;
  text-align: center;
  font-size: 0.92rem;
}

.banner {
  padding: 12px 18px;
  border-radius: var(--radius-sm);
  font-size: 0.87rem;
  font-weight: 600;
}

.banner--error {
  background: var(--danger-soft);
  color: var(--danger);
}

@media (max-width: 700px) {
  .hero { gap: 16px; }
  .info-row { padding: 9px 0; }
}
</style>
