<template>
  <div class="toast-host" role="status" aria-live="polite">
    <transition-group name="toast">
      <div
        v-for="item in items"
        :key="item.id"
        class="toast"
        :class="`toast--${item.tone}`"
      >
        <span class="toast__dot"></span>
        <span class="toast__text">{{ item.message }}</span>
        <button class="toast__close" aria-label="Close" @click="dismiss(item.id)">✕</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToast } from '../toast'

const { items, dismiss } = useToast()
</script>

<style scoped>
.toast-host {
  position: fixed;
  bottom: 24px;
  inset-inline-end: 24px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 260px;
  max-width: 380px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--shadow-md);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
}

.toast__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--text-muted);
}

.toast--success .toast__dot { background: var(--success); }
.toast--error .toast__dot { background: var(--danger); }
.toast--info .toast__dot { background: var(--accent); }

.toast__text {
  flex: 1;
  word-break: break-word;
}

.toast__close {
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.78rem;
  padding: 2px 4px;
  border-radius: 4px;
}

.toast__close:hover { color: var(--text); }

.toast-enter-active,
.toast-leave-active {
  transition: all 0.28s ease;
}

.toast-enter-from { opacity: 0; transform: translateY(10px) scale(0.97); }
.toast-leave-to { opacity: 0; transform: translateY(6px) scale(0.97); }

@media (max-width: 600px) {
  .toast-host {
    inset-inline: 16px;
    bottom: 16px;
  }
  .toast { min-width: 0; width: 100%; }
}
</style>
