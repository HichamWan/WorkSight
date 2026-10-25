import { ref } from 'vue'

const items = ref([])
let nextId = 1

/**
 * Minimal toast notification store.
 * Usage: toast('Saved', 'success')
 */
export function notify(message, tone = 'info', timeout = 3500) {
  const id = nextId++
  items.value.push({ id, message, tone })

  if (timeout > 0) {
    setTimeout(() => dismiss(id), timeout)
  }
  return id
}

export function dismiss(id) {
  items.value = items.value.filter((item) => item.id !== id)
}

export function useToast() {
  return {
    items,
    dismiss,
    success: (message) => notify(message, 'success'),
    error: (message) => notify(message, 'error'),
    info: (message) => notify(message, 'info')
  }
}
