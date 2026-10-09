<template>
  <div class="login-stage">
    <div class="login-controls">
      <LanguageSwitcher />
      <ThemeToggle />
    </div>

    <div class="login-card glass glass--strong">
      <div class="login-card__glow" aria-hidden="true"></div>

      <div class="brand-mark">
        <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </svg>
      </div>

      <h1 class="login-title">{{ isRegister ? t('createAccountTitle') : t('welcomeBack') }}</h1>
      <p class="login-subtitle muted">
        {{ isRegister ? t('signUpSubtitle') : t('signInSubtitle') }}
      </p>

      <!-- Sign in -->
      <form v-if="!isRegister" class="login-form" @submit.prevent="submitLogin">
        <div class="field">
          <label class="field__label" for="li-username">{{ t('username') }}</label>
          <input
            id="li-username"
            v-model="loginForm.username"
            class="input"
            type="text"
            :placeholder="t('usernamePlaceholder')"
            autocomplete="username"
            required
          />
        </div>

        <div class="field">
          <label class="field__label" for="li-password">{{ t('password') }}</label>
          <input
            id="li-password"
            v-model="loginForm.password"
            class="input"
            type="password"
            :placeholder="t('passwordPlaceholder')"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button class="btn btn--primary login-submit" type="submit" :disabled="loading">
          {{ loading ? t('signingIn') : t('signIn') }}
        </button>
      </form>

      <!-- Register -->
      <form v-else class="login-form" @submit.prevent="submitRegister">
        <div class="field">
          <label class="field__label" for="rg-company">{{ t('companyNameOptional') }}</label>
          <input
            id="rg-company"
            v-model="registerForm.company_name"
            class="input"
            type="text"
            :placeholder="t('companyName')"
            autocomplete="organization"
          />
        </div>

        <div class="field">
          <label class="field__label" for="rg-username">{{ t('username') }}</label>
          <input
            id="rg-username"
            v-model="registerForm.username"
            class="input"
            type="text"
            :placeholder="t('chooseUsername')"
            autocomplete="username"
            required
          />
        </div>

        <div class="field">
          <label class="field__label" for="rg-email">{{ t('email') }}</label>
          <input
            id="rg-email"
            v-model="registerForm.email"
            class="input"
            type="email"
            :placeholder="t('emailPlaceholder')"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label class="field__label" for="rg-password">{{ t('password') }}</label>
          <input
            id="rg-password"
            v-model="registerForm.password"
            class="input"
            type="password"
            :placeholder="t('passwordHint')"
            autocomplete="new-password"
            minlength="6"
            required
          />
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button class="btn btn--primary login-submit" type="submit" :disabled="loading">
          {{ loading ? t('creatingAccount') : t('createAccount') }}
        </button>
      </form>

      <p class="login-switch">
        <template v-if="!isRegister">
          {{ t('noAccount') }}
          <button type="button" class="link-btn" @click="switchMode(true)">{{ t('createOne') }}</button>
        </template>
        <template v-else>
          {{ t('haveAccount') }}
          <button type="button" class="link-btn" @click="switchMode(false)">{{ t('signInLink') }}</button>
        </template>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../auth'
import { useI18n } from '../i18n'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import ThemeToggle from '../components/ThemeToggle.vue'

const router = useRouter()
const { login, register, loading } = useAuth()
const { t } = useI18n()

const isRegister = ref(false)
const error = ref('')

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ company_name: '', username: '', email: '', password: '' })

function switchMode(toRegister) {
  isRegister.value = toRegister
  error.value = ''
}

async function submitLogin() {
  error.value = ''
  try {
    await login(loginForm.username.trim(), loginForm.password)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message || t('loginFailed')
  }
}

async function submitRegister() {
  error.value = ''
  try {
    await register({
      username: registerForm.username.trim(),
      email: registerForm.email.trim(),
      password: registerForm.password,
      company_name: registerForm.company_name.trim() || null
    })
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message || t('registerFailed')
  }
}
</script>

<style scoped>
.login-stage {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  position: relative;
}

.login-controls {
  position: absolute;
  top: 22px;
  inset-inline-end: 26px;
  display: flex;
  gap: 10px;
  z-index: 10;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 42px 38px;
  overflow: hidden;
}

/* subtle accent edge on the corner — flat, no blur */
.login-card__glow {
  display: none;
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  margin-bottom: 22px;
  background: var(--accent);
  color: #fff;
}

.login-title {
  font-size: 1.55rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.login-subtitle {
  margin: 6px 0 26px;
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-error {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--danger);
  background: var(--danger-soft);
  border: 1px solid rgba(229, 72, 77, 0.25);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}

.login-submit {
  padding: 13px 22px;
  font-size: 0.95rem;
}

.login-switch {
  margin-top: 22px;
  text-align: center;
  font-size: 0.86rem;
  color: var(--text-secondary);
}

.link-btn {
  background: none;
  border: none;
  font: inherit;
  font-weight: 700;
  color: var(--accent-strong);
  cursor: pointer;
  padding: 0;
}

.link-btn:hover { text-decoration: underline; }
</style>
