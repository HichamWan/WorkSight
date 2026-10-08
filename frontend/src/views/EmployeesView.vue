<template>
  <div class="employees">
    <section class="glass toolbar">
      <input v-model="query" class="input toolbar__search" type="text" placeholder="Search employees…" />
      <button class="btn btn--primary" @click="openModal">+ Add employee</button>
    </section>

    <section class="glass table-card">
      <div v-if="loading" class="empty muted">Loading employees…</div>
      <div v-else-if="filtered.length === 0" class="empty muted">No employees found.</div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Code</th>
              <th>Department</th>
              <th>Position</th>
              <th>Contact</th>
              <th>Face ID</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in filtered" :key="emp.id">
              <td>
                <div class="emp-cell">
                  <div class="emp-avatar">{{ initials(emp) }}</div>
                  <div class="emp-cell__name">
                    <strong>{{ emp.first_name }} {{ emp.last_name }}</strong>
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
                <button class="btn btn--sm btn--danger" @click="remove(emp)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Add employee modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal glass glass--strong">
        <h2 class="modal__title">Add employee</h2>
        <form class="modal__form" @submit.prevent="create">
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
              {{ saving ? 'Saving…' : 'Create employee' }}
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

const employees = ref([])
const loading = ref(true)
const query = ref('')
const showModal = ref(false)
const saving = ref(false)
const formError = ref('')

const form = reactive({
  employee_code: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  department: '',
  position: ''
})

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

function initials(emp) {
  return `${emp.first_name?.[0] ?? ''}${emp.last_name?.[0] ?? ''}`.toUpperCase()
}

function openModal() {
  Object.assign(form, {
    employee_code: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: ''
  })
  formError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function load() {
  loading.value = true
  try {
    const res = await api.employees()
    employees.value = res.employees || []
  } catch (e) {
    console.error('Failed to load employees:', e)
  } finally {
    loading.value = false
  }
}

async function create() {
  saving.value = true
  formError.value = ''
  try {
    await api.createEmployee({ ...form })
    showModal.value = false
    await load()
  } catch (e) {
    formError.value = e.message || 'Could not create employee'
  } finally {
    saving.value = false
  }
}

async function remove(emp) {
  if (!confirm(`Delete ${emp.first_name} ${emp.last_name}? This cannot be undone.`)) return
  try {
    await api.deleteEmployee(emp.id)
    await load()
  } catch (e) {
    alert(e.message || 'Delete failed')
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
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.74rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #5b7cff, #2f4ce0);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
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
  background: rgba(50, 60, 80, 0.3);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
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
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}
</style>
