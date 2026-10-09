<template>
  <div class="lang" ref="root">
    <button
      class="btn btn--icon lang__btn"
      :title="currentLabel"
      aria-label="Change language"
      @click="open = !open"
    >
      <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="9" />
        <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" />
      </svg>
    </button>

    <transition name="lang-pop">
      <ul v-if="open" class="lang__menu glass glass--strong">
        <li v-for="l in locales" :key="l.code">
          <button
            class="lang__item"
            :class="{ 'lang__item--active': l.code === locale }"
            @click="select(l.code)"
          >
            <span class="lang__name">{{ l.label }}</span>
            <svg v-if="l.code === locale" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </button>
        </li>
      </ul>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from '../i18n'

const { locale, setLocale, locales } = useI18n()
const open = ref(false)
const root = ref(null)

const currentLabel = computed(
  () => locales.find((l) => l.code === locale.value)?.label || 'Language'
)

function select(code) {
  setLocale(code)
  open.value = false
}

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.lang {
  position: relative;
  display: inline-block;
}

.lang__menu {
  position: absolute;
  top: calc(100% + 6px);
  inset-inline-end: 0;
  min-width: 172px;
  list-style: none;
  padding: 6px;
  margin: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: 60;
}

.lang__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.lang__item:hover {
  background: var(--row-hover);
  color: var(--text-primary);
}

.lang__item--active {
  color: var(--accent-strong);
  font-weight: 700;
  background: var(--accent-soft);
}

.lang-pop-enter-active,
.lang-pop-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}
.lang-pop-enter-from,
.lang-pop-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
