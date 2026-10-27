<template>
  <div class="gsearch" ref="root">
    <div class="gsearch__field">
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.5-3.5" />
      </svg>
      <input
        v-model="query"
        class="gsearch__input"
        type="text"
        :placeholder="t('search')"
        @input="onInput"
        @focus="query && (open = true)"
      />
      <span v-if="searching" class="gsearch__spinner"></span>
    </div>

    <transition name="gsearch-pop">
      <div v-if="open && (results.length || !searching)" class="gsearch__menu glass glass--strong">
        <div v-if="!results.length" class="gsearch__empty muted">
          {{ searching ? '…' : t('noSearchResults') }}
        </div>
        <ul v-else class="gsearch__list">
          <li v-for="r in results" :key="r.id">
            <button class="gsearch__item" @click="go(r)">
              <span class="gsearch__avatar">{{ initials(r) }}</span>
              <span class="gsearch__text">
                <span class="gsearch__name">{{ r.first_name }} {{ r.last_name }}</span>
                <span class="gsearch__meta muted">{{ r.department || '—' }} · {{ r.position || '—' }}</span>
              </span>
            </button>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useI18n } from '../i18n'
import { can } from '../roles'
import { useAuth } from '../auth'

const { t } = useI18n()
const { user } = useAuth()
const router = useRouter()

const query = ref('')
const open = ref(false)
const searching = ref(false)
const results = ref([])
const root = ref(null)

let debounce = null

function onInput() {
  clearTimeout(debounce)
  if (!query.value.trim()) {
    open.value = false
    results.value = []
    return
  }
  open.value = true
  searching.value = true
  debounce = setTimeout(async () => {
    try {
      const res = await api.employees({ search: query.value.trim() })
      results.value = (res?.employees || []).slice(0, 6)
    } catch {
      results.value = []
    } finally {
      searching.value = false
    }
  }, 250)
}

function initials(r) {
  return ((r.first_name || '?')[0] + (r.last_name || '')[0] || '').toUpperCase()
}

function go(r) {
  open.value = false
  query.value = ''
  router.push({ name: 'employee-detail', params: { id: r.id } })
}

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.gsearch { position: relative; min-width: 0; }

.gsearch__field {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px solid var(--input-border);
  border-radius: var(--radius-pill);
  background: var(--input-bg);
  color: var(--text-muted);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  width: clamp(160px, 26vw, 320px);
}
.gsearch__field:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--input-ring);
}

.gsearch__input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.86rem;
  color: var(--text);
}
.gsearch__input::placeholder { color: var(--text-muted); }

.gsearch__spinner {
  width: 13px;
  height: 13px;
  border: 2px solid var(--accent-border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: gsearch-spin 0.7s linear infinite;
}
@keyframes gsearch-spin { to { transform: rotate(360deg); } }

.gsearch__menu {
  position: absolute;
  top: calc(100% + 8px);
  inset-inline-start: 0;
  width: min(380px, 90vw);
  padding: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: 60;
}

.gsearch__empty { padding: 16px; text-align: center; font-size: 0.84rem; }

.gsearch__list { list-style: none; margin: 0; padding: 0; }

.gsearch__item {
  display: flex;
  align-items: center;
  gap: 11px;
  width: 100%;
  padding: 9px 10px;
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  font-family: inherit;
  text-align: start;
  cursor: pointer;
  transition: background 0.13s ease;
}
.gsearch__item:hover { background: var(--row-hover); }

.gsearch__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-gradient);
  flex-shrink: 0;
}

.gsearch__text { display: flex; flex-direction: column; min-width: 0; }
.gsearch__name { font-size: 0.86rem; font-weight: 600; color: var(--text); }
.gsearch__meta { font-size: 0.74rem; }

.gsearch-pop-enter-active,
.gsearch-pop-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.gsearch-pop-enter-from,
.gsearch-pop-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
