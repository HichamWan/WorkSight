<template>
  <div class="settings">
    <!-- Profile -->
    <section class="glass settings__card">
      <div class="settings__head">
        <h2 class="settings__title">{{ t('profile') }}</h2>
        <span class="chip chip--accent">{{ currentRole }}</span>
      </div>

      <div class="settings__profile">
        <div class="settings__avatar">{{ initials }}</div>
        <div class="settings__id">
          <span class="settings__name">{{ user?.username || 'User' }}</span>
          <span class="muted settings__email">{{ user?.email || '—' }}</span>
        </div>
      </div>

      <dl class="settings__grid">
        <div class="settings__row">
          <dt class="muted">{{ t('username') }}</dt>
          <dd>{{ user?.username || '—' }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('email') }}</dt>
          <dd>{{ user?.email || '—' }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('status') }}</dt>
          <dd><span class="chip chip--success">{{ user?.status || 'active' }}</span></dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('role') || 'Role' }}</dt>
          <dd>{{ currentRole }}</dd>
        </div>
      </dl>
    </section>

    <!-- Security -->
    <section class="glass settings__card">
      <div class="settings__head">
        <h2 class="settings__title">{{ t('security') }}</h2>
      </div>

      <form class="settings__form" @submit.prevent="submitPassword">
        <div class="field">
          <label class="field__label">{{ t('currentPassword') }}</label>
          <input v-model="pw.current" type="password" class="input" autocomplete="current-password" required />
        </div>
        <div class="settings__form-row">
          <div class="field">
            <label class="field__label">{{ t('newPassword') }}</label>
            <input v-model="pw.next" type="password" class="input" autocomplete="new-password" required />
          </div>
          <div class="field">
            <label class="field__label">{{ t('confirmPassword') }}</label>
            <input v-model="pw.confirm" type="password" class="input" autocomplete="new-password" required />
          </div>
        </div>

        <p v-if="pwError" class="form-error">{{ pwError }}</p>
        <p v-if="pwSuccess" class="form-success">{{ pwSuccess }}</p>

        <div class="settings__actions">
          <button type="button" class="btn btn--ghost" @click="resetPw">{{ t('cancel') }}</button>
          <button type="submit" class="btn btn--primary" :disabled="pwLoading">
            {{ pwLoading ? t('saving') : t('changePassword') }}
          </button>
        </div>
      </form>
    </section>

    <!-- Preferences -->
    <section class="glass settings__card">
      <div class="settings__head">
        <h2 class="settings__title">{{ t('preferences') }}</h2>
      </div>

      <div class="settings__pref">
        <div>
          <span class="settings__pref-label">{{ t('appearance') }}</span>
          <span class="muted settings__pref-hint">{{ theme === 'dark' ? t('dark') : t('light') }}</span>
        </div>
        <button class="btn btn--ghost btn--sm" @click="toggleTheme">
          {{ theme === 'dark' ? t('light') : t('dark') }}
        </button>
      </div>

      <div class="settings__pref">
        <div>
          <span class="settings__pref-label">{{ t('language') }}</span>
          <span class="muted settings__pref-hint">{{ currentLocaleLabel }}</span>
        </div>
        <select class="select settings__lang" :value="locale" @change="setLocale($event.target.value)">
          <option v-for="l in locales" :key="l.code" :value="l.code">{{ l.label }}</option>
        </select>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useAuth } from '../auth'
import { useI18n } from '../i18n'
import { useTheme } from '../theme'
import { roleLabel } from '../roles'
import { api } from '../api'

const { t } = useI18n()
const { user } = useAuth()
const { theme, toggleTheme } = useTheme()
const { locale, setLocale, locales } = useI18n()

const currentRole = computed(() => roleLabel(user.value))
const initials = computed(() =>
  (user.value?.username || 'U').slice(0, 2).toUpperCase()
)

const currentLocaleLabel = computed(
  () => locales.find((l) => l.code === locale.value)?.label || 'English'
)

const pw = reactive({ current: '', next: '', confirm: '' })
const pwError = ref('')
const pwSuccess = ref('')
const pwLoading = ref(false)

function resetPw() {
  pw.current = pw.next = pw.confirm = ''
  pwError.value = ''
  pwSuccess.value = ''
}

async function submitPassword() {
  pwError.value = ''
  pwSuccess.value = ''

  if (pw.next !== pw.confirm) {
    pwError.value = t('passwordMismatch')
    return
  }
  if (pw.next.length < 6) {
    pwError.value = t('passwordTooShort')
    return
  }

  pwLoading.value = true
  try {
    await api.changePassword(pw.current, pw.next)
    pwSuccess.value = t('passwordChanged')
    pw.current = pw.next = pw.confirm = ''
  } catch (e) {
    pwError.value = e?.message || t('wrongCurrentPassword')
  } finally {
    pwLoading.value = false
  }
}
</script>

<style scoped>
.settings {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
  align-items: start;
}

.settings__card { padding: 22px; }

.settings__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.settings__title { font-size: 1rem; font-weight: 700; }

.settings__profile {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  border: 1px solid var(--hairline);
  border-radius: var(--radius-md);
  background: var(--surface-2);
  margin-bottom: 16px;
}

.settings__avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.95rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-gradient);
  box-shadow: 0 4px 14px -4px var(--accent-glow);
  flex-shrink: 0;
}

.settings__id { display: flex; flex-direction: column; min-width: 0; }
.settings__name { font-weight: 700; }
.settings__email { font-size: 0.82rem; overflow: hidden; text-overflow: ellipsis; }

.settings__grid { display: flex; flex-direction: column; }
.settings__row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 10px 2px;
  border-bottom: 1px solid var(--hairline-2);
  font-size: 0.88rem;
}
.settings__row:last-child { border-bottom: none; }
.settings__row dt { font-size: 0.8rem; }
.settings__row dd { margin: 0; font-weight: 600; }

.settings__form { display: flex; flex-direction: column; gap: 14px; }
.settings__form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-error {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--danger);
  background: var(--danger-soft);
  border: 1px solid var(--danger);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}

.form-success {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--success);
  background: var(--success-soft);
  border: 1px solid var(--success);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}

.settings__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.settings__pref {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 2px;
  border-bottom: 1px solid var(--hairline-2);
}
.settings__pref:last-child { border-bottom: none; }
.settings__pref-label { display: block; font-size: 0.88rem; font-weight: 600; }
.settings__pref-hint { font-size: 0.78rem; }

.settings__lang { width: auto; min-width: 130px; }
</style>
