<template>
  <div v-if="open" class="modal-backdrop confirm-backdrop" @click.self="cancel">
    <div class="modal confirm glass glass--strong" role="dialog" aria-modal="true">
      <div class="confirm__head">
        <div class="confirm__icon" v-html="icon"></div>
        <h2 class="confirm__title">{{ title }}</h2>
      </div>
      <p class="confirm__body muted">{{ message }}</p>

      <div class="confirm__actions">
        <button type="button" class="btn btn--ghost" @click="cancel">{{ cancelLabel }}</button>
        <button type="button" class="btn btn--danger" :disabled="busy" @click="confirm">
          {{ busy ? 'Working…' : confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirm' },
  cancelLabel: { type: String, default: 'Cancel' },
  /** Async handler; the dialog stays open (busy) until it resolves. */
  onConfirm: { type: Function, required: true }
})

const open = ref(false)
const busy = ref(false)

const icon =
  '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg>'

function show() {
  open.value = true
}

function cancel() {
  if (busy.value) return
  open.value = false
}

async function confirm() {
  busy.value = true
  try {
    await props.onConfirm()
    open.value = false
  } catch (e) {
    console.error('Confirm action failed:', e)
  } finally {
    busy.value = false
  }
}

defineExpose({ show, cancel })
</script>

<style scoped>
.confirm-backdrop {
  z-index: 90;
}

.confirm {
  max-width: 400px;
  padding: 26px 28px;
}

.confirm__head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.confirm__icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  background: var(--danger-soft);
  color: var(--danger);
  flex-shrink: 0;
}

.confirm__title {
  font-size: 1rem;
  font-weight: 700;
}

.confirm__body {
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 22px;
}

.confirm__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
