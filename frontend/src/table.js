import { ref, computed, watch } from 'vue'

/**
 * Client-side sort + paginate over a list of rows.
 *
 * const { page, totalPages, sorted, paged, total, toggleSort, setPage } = useTable(employees)
 * <th @click="toggleSort('first_name')">First name</th>
 */
export function useTable(source, options = {}) {
  const { pageSize = 10, initialSort = null } = options
  const sortKey = ref(initialSort?.key ?? null)
  const sortDir = ref(initialSort?.dir ?? 'asc')
  const page = ref(1)

  // Reset to page 1 whenever the source list changes.
  watch(source, () => {
    if (page.value > 1) page.value = 1
  })

  const sorted = computed(() => {
    const list = Array.isArray(source.value) ? source.value : source.value
    if (!sortKey.value) return [...list]
    const key = sortKey.value
    const dir = sortDir.value === 'desc' ? -1 : 1
    return [...list].sort((a, b) => {
      const av = a?.[key]
      const bv = b?.[key]
      if (av == null && bv == null) return 0
      if (av == null) return 1
      if (bv == null) return -1
      if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir
      return String(av).localeCompare(String(bv), undefined, { numeric: true }) * dir
    })
  })

  const total = computed(() => sorted.value.length)
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
  const paged = computed(() => {
    const start = (page.value - 1) * pageSize
    return sorted.value.slice(start, start + pageSize)
  })

  function toggleSort(key) {
    if (sortKey.value === key) {
      sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = key
      sortDir.value = 'asc'
    }
  }

  function setPage(value) {
    const next = Math.max(1, Math.min(totalPages.value, Number(value) || 1))
    page.value = next
  }

  return { page, total, totalPages, paged, sorted, sortKey, sortDir, toggleSort, setPage, pageSize }
}
