<template>
  <div class="employees">
    <section class="glass toolbar">
      <input v-model="query" class="input toolbar__search" type="text" placeholder="Search employees…" />
      <div class="toolbar__spacer"></div>
      <button v-if="canCreate" class="btn btn--primary" @click="openModal()">+ {{ t('addEmployee') }}</button>
    </section>

    <section class="glass table-card">
      <div v-if="loading" class="empty muted">Loading employees…</div>
      <div v-else-if="filtered.length === 0" class="empty muted">No employees found.</div>
      <template v-else>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th class="sortable" @click="toggleSort('first_name')">Employee {{ arrow('first_name') }}</th>
                <th class="sortable" @click="toggleSort('employee_code')">Code {{ arrow('employee_code') }}</th>
                <th class="sortable" @click="toggleSort('department')">Department {{ arrow('department') }}</th>
                <th class="sortable" @click="toggleSort('position')">Position {{ arrow('position') }}</th>
                <th>Contact</th>
                <th>Face ID</th>
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
                    {{ emp.face_registered ? 'Registered' : 'Not set' }}
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
        <h2 class="modal__title">{{ editing ? 'Edit employee' : 'Add employee' }}</h2>
        <form class="modal__form" @submit.prevent="save">
          <div class="field">
            <label class="field__label">Employee code</label>
            <input v-model="form.employee_code" class="input" required placeholder="e.g. EMP-107" />
          </div>
          <div class="field-row">
            <div class="field">
              <label class="field__label">First name</label>
              <input v-model="form.first_name" class="input" required />
            </div>
            <div class="field">
              <label class="field__label">Last name</label>
              <input v-model="form.last_name" class="input" required />
            </div>
          </div>
          <div class="field">
            <label class="field__label">Email</label>
            <input v-model="form.email" class="input" type="email" required placeholder="name@company.com" />
          </div>
          <div class="field-row">
            <div class="field">
              <label class="field__label">Phone</label>
              <input v-model="form.phone" class="input" required />
            </div>
            <div class="field">
              <label class="field__label">Department</label>
              <input v-model="form.department" class="input" required />
            </div>
          </div>
          <div class="field">
            <label class="field__label">Position</label>
            <input v-model="form.position" class="input" required />
          </div>

          <p v-if="formError" class="form-error">{{ formError }}</p>

          <div class="modal__actions">
            <button type="button" class="btn btn--ghost" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn--primary" :disabled="saving">
              {{ saving ? 'Saving…' : editing ? 'Update employee' : 'Create employee' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { api } from '../api'
import { can } from '../roles'
import { useAuth } from '../auth'
import { useTable } from '../table'
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
  const q = query.value.trim().toLowerCase()
  if (!q) return employees.value
  return employees.value.filter((e) =>
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
  confirmMessage.value = `Delete ${emp.first_name} ${emp.last_name}? This cannot be undone.`
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
  z-index: 50;
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
