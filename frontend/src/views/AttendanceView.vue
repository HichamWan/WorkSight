<template>
  <div class="attendance">
    <section class="glass toolbar">
      <input v-model="query" class="input toolbar__search" type="text" placeholder="Search by employee…" />
      <span class="chip chip--accent" v-if="!loading">{{ rows.length }} records</span>
    </section>

    <section class="glass table-card">
      <div v-if="loading" class="empty muted">Loading attendance records…</div>
      <div v-else-if="filtered.length === 0" class="empty muted">No attendance records found.</div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Date</th>
              <th>Check in</th>
              <th>Check out</th>
              <th>Worked</th>
              <th>Overtime</th>
              <th>Undertime</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filtered" :key="row.id">
              <td class="strong">{{ row.employee_name }}</td>
              <td>{{ row.date }}</td>
              <td>{{ row.check_in }}</td>
              <td>{{ row.check_out }}</td>
              <td>{{ row.worked_hours != null ? row.worked_hours + ' h' : '—' }}</td>
              <td>
                <span v-if="row.overtime_hours > 0" class="chip chip--warning">
                  +{{ row.overtime_hours }} h
                </span>
                <span v-else class="muted">—</span>
              </td>
              <td>
                <span v-if="row.undertime_hours > 0" class="chip chip--danger">
                  −{{ row.undertime_hours }} h
                </span>
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
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

const rows = ref([])
const loading = ref(true)
const query = ref('')

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) => r.employee_name?.toLowerCase().includes(q))
})

function formatStatus(status) {
  return (status || '').replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

onMounted(async () => {
  try {
    const res = await api.attendance()
    rows.value = res.attendance || []
  } catch (e) {
    console.error('Failed to load attendance:', e)
  } finally {
    loading.value = false
  }
})
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

.strong {
  color: var(--text-primary);
  font-weight: 600;
}
</style>
