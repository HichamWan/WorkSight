<template>
  <div class="reports">
    <section class="glass toolbar">
      <div class="toolbar__group">
        <label class="field__label" for="report-type">{{ t('reportType') }}</label>
        <select id="report-type" v-model="reportType" class="input select" @change="load">
          <option value="attendance">{{ t('attendanceReport') }}</option>
          <option value="work-hours">{{ t('workHoursReport') }}</option>
        </select>
      </div>

      <div class="toolbar__spacer"></div>

      <div class="toolbar__group toolbar__group--actions">
        <button class="btn btn--ghost" :disabled="loading || exporting" @click="exportReport('csv')">
          {{ exporting && exportFormat === 'csv' ? t('saving') : t('exportCsv') }}
        </button>
        <button class="btn btn--primary" :disabled="loading || exporting" @click="exportReport('excel')">
          {{ exporting && exportFormat === 'excel' ? t('saving') : t('exportExcel') }}
        </button>
      </div>
    </section>

    <p v-if="error" class="banner banner--error">{{ error }}</p>
    <p v-else-if="notice" class="banner banner--success">{{ notice }}</p>

    <section class="glass table-card">
      <div class="table-card__head">
        <h2 class="panel__title">{{ reportTitle }}</h2>
        <span class="chip chip--accent" v-if="!loading">{{ rows.length }} {{ t('rowsLabel') }}</span>
      </div>

      <div v-if="loading" class="empty muted">{{ t('loadingReport') }}</div>
      <div v-else-if="rows.length === 0" class="empty muted">{{ t('noReportData') }}</div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th v-for="col in columns" :key="col">{{ prettyHeader(col) }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in rows" :key="row.id ?? index">
              <td v-for="col in columns" :key="col">{{ formatCell(col, row[col]) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api, downloadReport } from '../api'
import { useI18n } from '../i18n'

const { t } = useI18n()

const TYPES = {
  attendance: { key: 'attendanceReport', load: () => api.reportAttendance() },
  'work-hours': { key: 'workHoursReport', load: () => api.reportWorkHours() }
}

const reportType = ref('attendance')
const rows = ref([])
const columns = ref([])
const loading = ref(true)
const exporting = ref(false)
const exportFormat = ref('')
const error = ref('')
const notice = ref('')

const reportTitle = computed(() => t(TYPES[reportType.value].key))

async function load() {
  loading.value = true
  error.value = ''
  notice.value = ''
  try {
    const res = await TYPES[reportType.value].load()
    rows.value = res.data || []
    columns.value = rows.value.length ? Object.keys(rows.value[0]) : []
  } catch (e) {
    error.value = e.message || 'Could not load report'
    rows.value = []
    columns.value = []
  } finally {
    loading.value = false
  }
}

async function exportReport(format) {
  exporting.value = true
  exportFormat.value = format
  error.value = ''
  notice.value = ''
  try {
    const filename = await downloadReport(reportType.value, format)
    notice.value = t('exportSuccess', { file: filename })
  } catch (e) {
    error.value = e.message || 'Export failed'
  } finally {
    exporting.value = false
    exportFormat.value = ''
  }
}

function prettyHeader(key) {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatCell(key, value) {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'number') {
    // Hours columns read better with a unit suffix.
    return key.includes('hours') ? `${value} h` : value
  }
  return value
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: flex-end;
  gap: 18px;
  padding: 16px 20px;
  flex-wrap: wrap;
}

.toolbar__spacer {
  flex: 1;
}

.toolbar__group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.toolbar__group--actions {
  flex-direction: row;
  gap: 10px;
}

.select {
  min-width: 190px;
}

.field__label {
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
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

.banner--success {
  background: var(--success-soft);
  color: var(--success);
}

.table-card {
  padding: 20px 22px 22px;
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

.table-wrap {
  overflow-x: auto;
}

.empty {
  padding: 48px;
  text-align: center;
  font-size: 0.92rem;
}
</style>
