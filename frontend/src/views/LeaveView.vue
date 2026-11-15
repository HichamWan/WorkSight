<template>
  <div class="leaves">
    <!-- New request -->
    <section class="glass leaves__form-card">
      <h2 class="panel__title">{{ t('newLeaveRequest') }}</h2>

      <form class="leaves__form" @submit.prevent="submit">
        <div class="field">
          <label class="field__label">{{ t('selectEmployee') }}</label>
          <select v-model="form.employee_id" class="select" required>
            <option :value="null" disabled>{{ t('selectEmployee') }}</option>
            <option v-for="e in employees" :key="e.id" :value="e.id">
              {{ e.first_name }} {{ e.last_name }} · {{ e.department || '—' }}
            </option>
          </select>
        </div>

        <div class="leaves__dates">
          <div class="field">
            <label class="field__label">{{ t('from') }}</label>
            <input v-model="form.start_date" type="date" class="input" required />
          </div>
          <div class="field">
            <label class="field__label">{{ t('to') }}</label>
            <input v-model="form.end_date" type="date" class="input" required />
          </div>
        </div>

        <div class="field">
          <label class="field__label">{{ t('reason') }}</label>
          <textarea v-model="form.reason" class="input leaves__reason" rows="3" required></textarea>
        </div>

        <p v-if="formError" class="form-error">{{ formError }}</p>

        <div class="leaves__submit">
          <button type="submit" class="btn btn--primary" :disabled="submitting">
            {{ submitting ? t('saving') : t('submitLeave') }}
          </button>
        </div>
      </form>
    </section>

    <!-- Requests list -->
    <section class="glass table-card">
      <div class="table-card__head">
        <h2 class="panel__title">{{ t('leaveRequests') }}</h2>
        <div class="leaves__filters">
          <select v-model="statusFilter" class="select leaves__filter">
            <option value="all">{{ t('all') }}</option>
            <option value="pending">{{ t('pending') }}</option>
            <option value="approved">{{ t('approved') }}</option>
            <option value="rejected">{{ t('rejected') }}</option>
          </select>
          <span class="chip chip--accent">{{ filtered.length }} {{ t('total') }}</span>
        </div>
      </div>

      <div v-if="loading" class="empty muted">{{ t('loadingLeaves') }}</div>
      <div v-else-if="filtered.length === 0" class="empty muted">{{ t('noLeaves') }}</div>
      <template v-else>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>{{ t('employee') }}</th>
                <th>{{ t('from') }}</th>
                <th>{{ t('to') }}</th>
                <th>{{ t('reason') }}</th>
                <th class="sortable" @click="toggleSort('status')">{{ t('status') }} {{ arrow('status') }}</th>
                <th v-if="canDecide"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="l in paged" :key="l.id">
                <td>
                  <span class="leaves__name">{{ l.employee_name }}</span>
                  <span class="muted leaves__dept">{{ l.department || l.employee_code }}</span>
                </td>
                <td>{{ l.start_date }}</td>
                <td>{{ l.end_date }}</td>
                <td class="leaves__reason-cell">{{ l.reason }}</td>
                <td>
                  <span class="chip" :class="statusTone(l.status)">{{ t(l.status) }}</span>
                </td>
                <td v-if="canDecide">
                  <div v-if="l.status === 'pending'" class="leaves__actions">
                    <button class="btn btn--sm btn--primary" @click="decide(l, 'approved')">
                      {{ t('approve') }}
                    </button>
                    <button class="btn btn--sm btn--ghost" @click="decide(l, 'rejected')">
                      {{ t('reject') }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager v-if="totalPages > 1" :page="page" :total-pages="totalPages" :total="total" @change="setPage" />
      </template>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../i18n'
import { useTable } from '../table'
import { useToast } from '../toast'
import { useAuth } from '../auth'
import { can } from '../roles'
import Pager from '../components/Pager.vue'

const { t } = useI18n()
const toast = useToast()
const { user } = useAuth()

const employees = ref([])
const leaves = ref([])
const loading = ref(true)
const statusFilter = ref('all')

// Approve/reject requires HR or Manager (same roles allowed to update employees).
const canDecide = computed(() => can('updateEmployee', user.value))

const form = reactive({ employee_id: null, start_date: '', end_date: '', reason: '' })
const formError = ref('')
const submitting = ref(false)

const filtered = computed(() =>
  statusFilter.value === 'all' ? leaves.value : leaves.value.filter((l) => l.status === statusFilter.value)
)

const { page, totalPages, paged, total, sortKey, sortDir, toggleSort, setPage } = useTable(filtered, { pageSize: 8 })

function arrow(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? '↑' : '↓'
}

function statusTone(status) {
  if (status === 'approved') return 'chip--success'
  if (status === 'rejected') return 'chip--danger'
  return 'chip--warning'
}

async function load() {
  loading.value = true
  try {
    const [empRes, leaveRes] = await Promise.all([api.employees(), api.leaves()])
    employees.value = empRes?.employees || []
    leaves.value = leaveRes?.leaves || []
  } catch (e) {
    toast.error(e.message)
  } finally {
    loading.value = false
  }
}

async function submit() {
  formError.value = ''
  if (!form.employee_id) {
    formError.value = t('selectEmployee')
    return
  }
  if (form.end_date < form.start_date) {
    formError.value = t('leaveDateError')
    return
  }
  submitting.value = true
  try {
    const res = await api.createLeave({
      employee_id: form.employee_id,
      start_date: form.start_date,
      end_date: form.end_date,
      reason: form.reason
    })
    leaves.value.unshift(res.leave)
    toast.success(t('leaveCreated'))
    form.start_date = form.end_date = form.reason = ''
  } catch (e) {
    formError.value = e.message
    toast.error(e.message)
  } finally {
    submitting.value = false
  }
}

async function decide(leave, status) {
  try {
    const res = await api.setLeaveStatus(leave.id, status)
    Object.assign(leave, res.leave)
    toast.success(status === 'approved' ? t('leaveApproved') : t('leaveRejected'))
  } catch (e) {
    toast.error(e.message)
  }
}

onMounted(load)
</script>

<style scoped>
.leaves {
  display: grid;
  grid-template-columns: minmax(300px, 380px) 1fr;
  gap: 18px;
  align-items: start;
}

.leaves__form-card { padding: 22px; }
.panel__title { font-size: 0.95rem; font-weight: 700; }

.leaves__form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 14px;
}

.leaves__dates {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.leaves__reason { resize: vertical; min-height: 74px; }

.leaves__submit { display: flex; justify-content: flex-end; }

.form-error {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--danger);
  background: var(--danger-soft);
  border: 1px solid var(--danger);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}

.table-card { padding: 20px; }
.table-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.leaves__filters { display: flex; align-items: center; gap: 10px; }
.leaves__filter { width: auto; padding: 7px 12px; font-size: 0.84rem; }

.leaves__name { display: block; font-weight: 600; }
.leaves__dept { font-size: 0.76rem; }
.leaves__reason-cell { max-width: 260px; }

.leaves__actions { display: flex; gap: 8px; }

.empty { padding: 36px; text-align: center; font-size: 0.88rem; }
.sortable { cursor: pointer; user-select: none; }

@media (max-width: 980px) {
  .leaves { grid-template-columns: 1fr; }
}
</style>
