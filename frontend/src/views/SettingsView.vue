<template>
  <div class="settings">
    <!-- Profile -->
    <section class="glass settings__card settings__card--profile">
      <div class="settings__head">
        <h2 class="settings__title">{{ t('profile') }}</h2>
        <span class="chip chip--accent">{{ currentRole }}</span>
      </div>

      <div class="settings__profile">
        <div class="settings__avatar-wrap">
          <img
            v-if="avatarSrc"
            :src="avatarSrc"
            :alt="user?.username"
            class="settings__avatar settings__avatar--photo"
          />
          <img
            v-else
            src="/logo-sm.png"
            alt="WorkSight"
            class="settings__avatar settings__avatar--photo settings__avatar--default"
          />
          <button
            class="settings__avatar-overlay"
            :title="t('changePhoto')"
            :disabled="avatarBusy"
            @click="$refs.avatarInput.click()"
          >
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
              <circle cx="12" cy="13" r="3"/>
            </svg>
            <span>{{ avatarBusy ? t('loading') : t('changePhoto') }}</span>
          </button>
          <input
            ref="avatarInput"
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            class="settings__avatar-input"
            @change="onAvatarPicked"
          />
        </div>
        <div class="settings__id">
          <span class="settings__name">{{ user?.username || 'User' }}</span>
          <span class="muted settings__email">{{ user?.email || '—' }}</span>
        </div>
        <div class="settings__id-actions">
          <button class="btn btn--ghost btn--sm" @click="startEmailEdit">
            {{ t('editEmail') }}
          </button>
          <button
            v-if="avatarSrc"
            class="btn btn--ghost btn--sm"
            :disabled="avatarBusy"
            @click="removePhoto"
          >
            {{ t('removePhoto') }}
          </button>
        </div>
      </div>

      <p v-if="avatarMsg" class="form-error">{{ avatarMsg }}</p>
      <p v-if="avatarOkMsg" class="form-success">{{ avatarOkMsg }}</p>

      <form v-if="emailEdit" class="settings__email-form" @submit.prevent="saveEmail">
        <div class="field">
          <label class="field__label">{{ t('newEmail') }}</label>
          <input v-model="emailForm.value" type="email" class="input" :placeholder="user?.email" required />
        </div>
        <p v-if="emailMsg.error" class="form-error">{{ emailMsg.error }}</p>
        <p v-if="emailMsg.ok" class="form-success">{{ emailMsg.ok }}</p>
        <div class="settings__actions">
          <button type="button" class="btn btn--ghost" @click="cancelEmailEdit">{{ t('cancel') }}</button>
          <button type="submit" class="btn btn--primary" :disabled="emailForm.loading">
            {{ emailForm.loading ? t('saving') : t('save') }}
          </button>
        </div>
      </form>

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
          <dt class="muted">{{ t('role') }}</dt>
          <dd>{{ currentRole }}</dd>
        </div>
      </dl>
    </section>

    <!-- Company -->
    <section class="glass settings__card">
      <div class="settings__head">
        <h2 class="settings__title">{{ t('companyInfo') }}</h2>
        <span v-if="profile" class="chip">{{ profile.company?.code || '—' }}</span>
      </div>

      <dl class="settings__grid">
        <div class="settings__row">
          <dt class="muted">{{ t('companyName') }}</dt>
          <dd>{{ profile?.company?.name || '—' }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('companyCode') }}</dt>
          <dd>{{ profile?.company?.code || '—' }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('memberSince') }}</dt>
          <dd>{{ memberSince }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('employees') }}</dt>
          <dd>{{ profile?.stats?.employees ?? '—' }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('departments') }}</dt>
          <dd>{{ profile?.stats?.departments ?? '—' }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('attendanceRecords') }}</dt>
          <dd>{{ profile?.stats?.attendance_records ?? '—' }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('pendingLeaves') }}</dt>
          <dd>
            <span class="chip" :class="pendingTone">{{ profile?.stats?.pending_leaves ?? '—' }}</span>
          </dd>
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

        <div v-if="pw.next" class="strength">
          <div class="strength__bars">
            <span
              v-for="i in 4"
              :key="i"
              class="strength__bar"
              :class="i <= strength.score ? `strength__bar--${strength.tone}` : ''"
            ></span>
          </div>
          <span class="strength__label" :class="`strength__label--${strength.tone}`">
            {{ t('passwordStrength') }}: {{ strength.label }}
          </span>
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

      <div class="settings__pref">
        <div>
          <span class="settings__pref-label">{{ t('motionEffects') }}</span>
          <span class="muted settings__pref-hint">{{ motion === 'on' ? t('enabled') : t('disabled') }}</span>
        </div>
        <button
          class="switch"
          :class="{ 'switch--on': motion === 'on' }"
          role="switch"
          :aria-checked="motion === 'on'"
          @click="toggleMotion"
        >
          <span class="switch__thumb"></span>
        </button>
      </div>
    </section>

    <!-- System -->
    <section class="glass settings__card">
      <div class="settings__head">
        <h2 class="settings__title">{{ t('systemStatus') }}</h2>
        <span v-if="conn.status" class="chip" :class="conn.status === 'ok' ? 'chip--success' : 'chip--danger'">
          {{ conn.status === 'ok' ? t('connectionOk') : t('connectionFail') }}
        </span>
      </div>

      <dl class="settings__grid">
        <div class="settings__row">
          <dt class="muted">{{ t('apiEndpoint') }}</dt>
          <dd class="settings__mono">{{ apiBase }}</dd>
        </div>
        <div class="settings__row">
          <dt class="muted">{{ t('version') }}</dt>
          <dd>{{ version || '—' }}</dd>
        </div>
      </dl>

      <div class="settings__actions">
        <button class="btn btn--ghost btn--sm" :disabled="conn.loading" @click="testConnection">
          {{ conn.loading ? t('loading') : t('checkConnection') }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useAuth } from '../auth'
import { useI18n } from '../i18n'
import { useTheme } from '../theme'
import { roleLabel } from '../roles'
import { api } from '../api'

const { t } = useI18n()
const { user, setUser } = useAuth()
const { theme, motion, toggleTheme, toggleMotion } = useTheme()
const { locale, setLocale, locales } = useI18n()

const profile = ref(null)
const currentRole = computed(() => roleLabel(user.value))
const initials = computed(() => (user.value?.username || 'U').slice(0, 2).toUpperCase())

/* ------------------------------ avatar ---------------------------------- */
const avatarInput = ref(null)
const avatarBusy = ref(false)
const avatarMsg = ref('')
const avatarOkMsg = ref('')
const avatarSrc = computed(() => api.avatarUrl(user.value?.avatar))

async function onAvatarPicked(e) {
  avatarMsg.value = ''
  avatarOkMsg.value = ''
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    avatarMsg.value = t('photoTooLarge')
    return
  }
  avatarBusy.value = true
  try {
    const res = await api.uploadAvatar(file)
    if (res?.user) setUser({ ...user.value, ...res.user })
    avatarOkMsg.value = t('photoUpdated')
  } catch (err) {
    avatarMsg.value = err?.message || t('photoInvalid')
  } finally {
    avatarBusy.value = false
  }
}

async function removePhoto() {
  avatarMsg.value = ''
  avatarOkMsg.value = ''
  avatarBusy.value = true
  try {
    const res = await api.removeAvatar()
    if (res?.user) setUser({ ...user.value, ...res.user })
    avatarOkMsg.value = t('photoRemoved')
  } catch (err) {
    avatarMsg.value = err?.message || t('photoInvalid')
  } finally {
    avatarBusy.value = false
  }
}

const memberSince = computed(() => {
  const raw = profile.value?.company?.created_at
  if (!raw) return '—'
  const d = new Date(raw)
  return Number.isNaN(d.getTime()) ? raw : d.toLocaleDateString()
})

const pendingTone = computed(() => {
  const n = profile.value?.stats?.pending_leaves || 0
  return n > 0 ? 'chip--warning' : ''
})

const currentLocaleLabel = computed(
  () => locales.find((l) => l.code === locale.value)?.label || 'English'
)

/* ------------------------------- email edit ------------------------------ */
const emailEdit = ref(false)
const emailForm = reactive({ value: '', loading: false })
const emailMsg = reactive({ error: '', ok: '' })

function startEmailEdit() {
  emailForm.value = user.value?.email || ''
  emailMsg.error = emailMsg.ok = ''
  emailEdit.value = true
}

function cancelEmailEdit() {
  emailEdit.value = false
  emailForm.value = ''
}

async function saveEmail() {
  emailMsg.error = emailMsg.ok = ''
  const value = emailForm.value.trim()
  if (!value || !value.includes('@')) return
  emailForm.loading = true
  try {
    const res = await api.updateProfile(value)
    if (res?.user) setUser({ ...user.value, ...res.user })
    emailMsg.ok = t('emailUpdated')
    emailEdit.value = false
    await loadProfile()
  } catch (e) {
    emailMsg.error = e?.message || t('emailTaken')
  } finally {
    emailForm.loading = false
  }
}

/* ------------------------------- password -------------------------------- */
const pw = reactive({ current: '', next: '', confirm: '' })
const pwError = ref('')
const pwSuccess = ref('')
const pwLoading = ref(false)

const strength = computed(() => {
  const v = pw.next
  if (!v) return { score: 0, tone: 'weak', label: '' }
  let score = 0
  if (v.length >= 6) score++
  if (v.length >= 10) score++
  if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score++
  if (/\d/.test(v) && /[^A-Za-z0-9]/.test(v)) score++
  score = Math.min(4, Math.max(1, score))
  const tones = ['weak', 'fair', 'good', 'strong']
  const tone = tones[score - 1]
  return { score, tone, label: t(`strength${tone[0].toUpperCase()}${tone.slice(1)}`) }
})

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

/* ------------------------------- system ---------------------------------- */
const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const conn = reactive({ status: '', loading: false })
const version = ref('')

async function testConnection() {
  conn.loading = true
  conn.status = ''
  try {
    const res = await api.health()
    conn.status = res?.status === 'ok' ? 'ok' : 'fail'
    version.value = res?.version || ''
  } catch {
    conn.status = 'fail'
  } finally {
    conn.loading = false
  }
}

/* ------------------------------- loading --------------------------------- */
async function loadProfile() {
  try {
    profile.value = await api.profile()
  } catch {
    profile.value = null
  }
}

onMounted(() => {
  loadProfile()
  testConnection()
})
</script>

<style scoped>
.settings {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
  align-items: start;
}

.settings__card { padding: 22px; }
.settings__card--profile { grid-column: 1 / -1; }

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

.settings__avatar-wrap {
  position: relative;
  width: 56px;
  height: 56px;
  flex-shrink: 0;
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

.settings__avatar--photo {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border: 2px solid var(--accent-border);
}

.settings__avatar--default {
  background: #070d20;
  border-color: var(--border-strong);
}

.settings__avatar-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border: none;
  border-radius: 50%;
  background: rgba(4, 10, 26, 0.72);
  color: #fff;
  font-size: 0.5rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.settings__avatar-wrap:hover .settings__avatar-overlay,
.settings__avatar-overlay:focus-visible {
  opacity: 1;
}

.settings__avatar-overlay:hover { transform: scale(1.05); }
.settings__avatar-overlay:disabled { opacity: 0.6; cursor: wait; }

.settings__avatar-input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.settings__id { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.settings__id-actions { display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }
.settings__name { font-weight: 700; }
.settings__email { font-size: 0.82rem; overflow: hidden; text-overflow: ellipsis; }

.settings__email-form { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }

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
.settings__row dd { margin: 0; font-weight: 600; text-align: end; }
.settings__mono { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.78rem; }

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

/* password strength meter */
.strength { display: flex; flex-direction: column; gap: 6px; }
.strength__bars { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.strength__bar {
  height: 6px;
  border-radius: 999px;
  background: var(--surface-3);
  border: 1px solid var(--hairline);
  transition: background 0.2s ease, border-color 0.2s ease;
}
.strength__bar--weak { background: var(--danger); border-color: var(--danger); }
.strength__bar--fair { background: var(--warning); border-color: var(--warning); }
.strength__bar--good { background: var(--accent); border-color: var(--accent); }
.strength__bar--strong { background: var(--success); border-color: var(--success); }
.strength__label { font-size: 0.76rem; font-weight: 600; color: var(--text-muted); }
.strength__label--weak { color: var(--danger); }
.strength__label--fair { color: var(--warning); }
.strength__label--good { color: var(--accent-strong); }
.strength__label--strong { color: var(--success); }

/* toggle switch */
.switch {
  width: 44px;
  height: 24px;
  padding: 2px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface-3);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
  flex-shrink: 0;
}
.switch__thumb {
  display: block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: transform 0.22s cubic-bezier(0.34, 1.4, 0.64, 1), background 0.2s ease;
}
.switch--on { background: var(--accent-soft); border-color: var(--accent-border); }
.switch--on .switch__thumb {
  transform: translateX(20px);
  background: var(--accent);
  box-shadow: 0 2px 8px var(--accent-glow);
}
</style>
