<template>
  <div class="employees">
    <section class="glass toolbar">
      <input v-model="query" class="input toolbar__search" type="text" :placeholder="t('searchEmployees')" />
      <select v-model="deptFilter" class="select toolbar__dept" :title="t('department')">
        <option value="">{{ t('department') }} · {{ t('viewAll') }}</option>
        <option v-for="d in departmentsList" :key="d" :value="d">{{ d }}</option>
      </select>
      <button v-if="deptFilter" class="btn btn--ghost btn--sm" @click="deptFilter = ''">✕</button>
      <div class="toolbar__spacer"></div>
      <button class="btn btn--ghost" :disabled="loading" @click="exportCsv">{{ t('exportCsv') }}</button>
      <button v-if="canCreate" class="btn btn--ghost" :disabled="importing" @click="fileInput?.click()">
        {{ importing ? t('loading') : t('importCsv') }}
      </button>
      <input ref="fileInput" type="file" accept=".csv,text/csv" class="hidden" @change="importCsv" />
      <button v-if="canCreate" class="btn btn--primary" @click="openModal()">+ {{ t('addEmployee') }}</button>
    </section>

    <section class="glass table-card">
      <div v-if="loading" class="empty muted">{{ t('loadingEmployees') }}</div>
      <div v-else-if="filtered.length === 0" class="empty muted">{{ t('noEmployees') }}</div>
      <template v-else>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th class="sortable" @click="toggleSort('first_name')">{{ t('employee') }} {{ arrow('first_name') }}</th>
                <th class="sortable" @click="toggleSort('employee_code')">{{ t('code') }} {{ arrow('employee_code') }}</th>
                <th class="sortable" @click="toggleSort('department')">{{ t('department') }} {{ arrow('department') }}</th>
                <th class="sortable" @click="toggleSort('position')">{{ t('position') }} {{ arrow('position') }}</th>
                <th>{{ t('contact') }}</th>
                <th>{{ t('faceId') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in pageRows" :key="emp.id">
                <td>
                  <div class="emp-cell">
                    <div class="emp-avatar">{{ initials(emp) }}</div>
                    <div class="emp-cell__name">
                      <router-link class="emp-link" :to="{ name: 'employee-detail', params: { id: emp.id } }">
                        {{ emp.first_name }} {{ emp.last_name }}
                      </router-link>
                      <span class="muted">{{ emp.email }}</span>
                    </div>
                  </div>
                </td>
                <td>{{ emp.employee_code }}</td>
                <td>{{ emp.department }}</td>
                <td>{{ emp.position }}</td>
                <td>{{ emp.phone }}</td>
                <td>
                  <span class="chip" :class="emp.face_registered ? 'chip--success' : ''">
                    {{ emp.face_registered ? t('registered') : t('notSet') }}
                  </span>
                </td>
                <td>
                  <div class="row-actions">
                    <button v-if="canUpdate" class="btn btn--sm btn--ghost" @click="openModal(emp)">{{ t('edit') }}</button>
                    <button v-if="canDelete" class="btn btn--sm btn--danger" @click="askRemove(emp)">{{ t('delete') }}</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager :page="page" :total-pages="totalPages" :total="total" @change="setPage" />
      </template>
    </section>

    <ConfirmDialog
      ref="confirmRef"
      :title="t('deleteEmployeeTitle')"
      :message="confirmMessage"
      :confirm-label="t('delete')"
      :on-confirm="confirmRemove"
    />

    <!-- Add / edit employee modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal glass glass--strong">
        <h2 class="modal__title">{{ editing ? t('edit') + ' ' + t('employee') : t('addEmployeeTitle') }}</h2>
        <form class="modal__form" @submit.prevent="save">
          <div class="field">
            <label class="field__label">{{ t('employeeCode') }}</label>
            <input v-model="form.employee_code" class="input" required placeholder="e.g. EMP-107" />
          </div>
          <div class="field-row">
            <div class="field">
              <label class="field__label">{{ t('firstName') }}</label>
              <input v-model="form.first_name" class="input" required />
            </div>
            <div class="field">
              <label class="field__label">{{ t('lastName') }}</label>
              <input v-model="form.last_name" class="input" required />
            </div>
          </div>
          <div class="field">
            <label class="field__label">{{ t('email') }}</label>
            <input v-model="form.email" class="input" type="email" required placeholder="name@company.com" />
          </div>
          <div class="field-row">
            <div class="field">
              <label class="field__label">{{ t('phone') }}</label>
              <input v-model="form.phone" class="input" required />
            </div>
            <div class="field">
              <label class="field__label">{{ t('department') }}</label>
              <input v-model="form.department" class="input" required />
            </div>
          </div>
          <div class="field">
            <label class="field__label">{{ t('position') }}</label>
            <input v-model="form.position" class="input" required />
          </div>

          <p v-if="formError" class="form-error">{{ formError }}</p>

          <div class="modal__actions">
            <button type="button" class="btn btn--ghost" @click="closeModal">{{ t('cancel') }}</button>
            <button type="submit" class="btn btn--primary" :disabled="saving">
              {{ saving ? t('saving') : editing ? t('updateEmployee') : t('createEmployee') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { api } from '../api'
import { can } from '../roles'
import { useAuth } from '../auth'
import { useTable } from '../table'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '../i18n'
import { notify } from '../toast'
import Pager from '../components/Pager.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const { user } = useAuth()
const { t } = useI18n()
const canCreate = computed(() => can('createEmployee', user.value))
const canUpdate = computed(() => can('updateEmployee', user.value))
const canDelete = computed(() => can('deleteEmployee', user.value))

const employees = ref([])
const loading = ref(true)
const query = ref('')
const route = useRoute()
const router = useRouter()
const deptFilter = ref(String(route.query.department || ''))
const departmentsList = computed(() =>
  [...new Set(employees.value.map((e) => e.department).filter(Boolean))].sort()
)

watch(deptFilter, (v) => {
  const q = { ...route.query }
  if (v) q.department = v
  else delete q.department
  router.replace({ query: q })
})

watch(
  () => route.query.department,
  (v) => {
    deptFilter.value = typeof v === 'string' ? v : ''
  }
)

const showModal = ref(false)
const saving = ref(false)
const formError = ref('')
const editing = ref(null)

const BLANK_FORM = {
  employee_code: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  department: '',
  position: ''
}

const form = reactive({ ...BLANK_FORM })

const filtered = computed(() => {
  let rows = employees.value
  if (deptFilter.value) rows = rows.filter((e) => e.department === deptFilter.value)
  const q = query.value.trim().toLowerCase()
  if (!q) return rows
  return rows.filter((e) =>
    [e.first_name, e.last_name, e.email, e.department, e.employee_code]
      .join(' ')
      .toLowerCase()
      .includes(q)
  )
})

const { page, totalPages, total, paged: pageRows, sortKey, sortDir, toggleSort, setPage } = useTable(filtered, {
  pageSize: 10,
  initialSort: { key: 'first_name', dir: 'asc' }
})

function arrow(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? '▲' : '▼'
}

function initials(emp) {
  return `${emp.first_name?.[0] ?? ''}${emp.last_name?.[0] ?? ''}`.toUpperCase()
}

const fileInput = ref(null)
const importing = ref(false)

const CSV_FIELDS = ['employee_code', 'first_name', 'last_name', 'email', 'phone', 'department', 'position']

function exportCsv() {
  const rows = [CSV_FIELDS, ...filtered.value.map((e) => CSV_FIELDS.map((f) => e[f] ?? ''))]
  const csv = rows
    .map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(','))
    .join('\n')
  const url = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `worksight-employees-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

function parseCsv(text) {
  return text
    .replace(/^\ufeff/, '')
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => line.match(/("([^"]|"")*"|[^,]*)(,|$)/g)?.map((cell) => cell.replace(/,$/, '').replace(/^"|"$/g, '').replaceAll('""', '"')) || [])
}

async function importCsv(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  const text = await file.text()
  const rows = parseCsv(text)
  if (rows.length < 2) {
    notify(t('importFailed'), 'error')
    return
  }
  const header = rows[0].map((h) => h.trim().toLowerCase())
  const idx = Object.fromEntries(CSV_FIELDS.map((f) => [f, header.indexOf(f)]))
  const records = rows.slice(1).map((cells) =>
    Object.fromEntries(CSV_FIELDS.map((f) => [f, (cells[idx[f]] ?? '').trim()]))
  )
  importing.value = true
  let ok = 0
  let failed = 0
  for (const rec of records) {
    if (!rec.employee_code || !rec.first_name) {
      failed += 1
      continue
    }
    try {
      await api.createEmployee(rec)
      ok += 1
    } catch {
      failed += 1
    }
  }
  importing.value = false
  await load()
  notify(t('importDone', { ok, failed }), ok ? 'success' : 'error')
}

function openModal(emp = null) {
  editing.value = emp
  Object.assign(form, BLANK_FORM)
  if (emp) {
    Object.assign(form, {
      employee_code: emp.employee_code ?? '',
      first_name: emp.first_name ?? '',
      last_name: emp.last_name ?? '',
      email: emp.email ?? '',
      phone: emp.phone ?? '',
      department: emp.department ?? '',
      position: emp.position ?? ''
    })
  }
  formError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editing.value = null
}

async function load() {
  loading.value = true
  try {
    const res = await api.employees()
    employees.value = res.employees || []
  } catch (e) {
    notify(e.message || 'Could not load employees', 'error')
  } finally {
    loading.value = false
  }
}

async function save() {
  return editing.value ? update() : create()
}

async function create() {
  saving.value = true
  formError.value = ''
  try {
    await api.createEmployee({ ...form })
    notify(t('employeeCreated'), 'success')
    closeModal()
    await load()
  } catch (e) {
    formError.value = e.message || 'Could not create employee'
  } finally {
    saving.value = false
  }
}

async function update() {
  saving.value = true
  formError.value = ''
  try {
    await api.updateEmployee(editing.value.id, { ...form })
    notify(t('employeeUpdated'), 'success')
    closeModal()
    await load()
  } catch (e) {
    formError.value = e.message || 'Could not update employee'
  } finally {
    saving.value = false
  }
}

// ----- Delete (using ConfirmDialog) -----
const confirmRef = ref(null)
const confirmMessage = ref('')
const pendingDelete = ref(null)

function askRemove(emp) {
  pendingDelete.value = emp
  confirmMessage.value = t('deleteConfirm', { name: `${emp.first_name} ${emp.last_name}` })
  confirmRef.value?.show()
}

async function confirmRemove() {
  const emp = pendingDelete.value
  if (!emp) return
  try {
    await api.deleteEmployee(emp.id)
    notify(t('employeeDeleted'), 'success')
    pendingDelete.value = null
    await load()
  } catch (e) {
    notify(e.message || 'Delete failed', 'error')
    throw e
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar__dept { width: auto; min-width: 160px; }

.toolbar {
  display: flex;
  gap: 14px;
  padding: 14px 18px;
  align-items: center;
}

.toolbar__search {
  max-width: 320px;
}

.table-card {
  padding: 10px 18px 18px;
}

.empty {
  padding: 48px;
  text-align: center;
  font-size: 0.92rem;
}

.emp-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.emp-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent);
  flex-shrink: 0;
}

.emp-cell__name {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.emp-cell__name strong {
  color: var(--text-primary);
  font-weight: 600;
}

.emp-cell__name .muted {
  font-size: 0.76rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: grid;
  place-items: center;
  padding: 24px;
  z-index: 200;
}

.modal {
  width: 100%;
  max-width: 520px;
  padding: 30px 32px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal__title {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.modal__form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-error {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--danger);
  background: var(--danger-soft);
  border: 1px solid rgba(255, 107, 126, 0.3);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.toolbar__spacer {
  flex: 1;
}

.emp-link {
  color: var(--text-primary);
  font-weight: 700;
  text-decoration: none;
}

.emp-link:hover {
  color: var(--accent);
}

.sortable {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.sortable:hover { color: var(--accent); }

@media (max-width: 700px) {
  .toolbar { flex-wrap: wrap; }
}
</style>
