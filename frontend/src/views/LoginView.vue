<template>
  <div class="login-stage">
    <div class="login-card glass glass--strong">
      <div class="login-card__glow" aria-hidden="true"></div>

      <div class="brand-mark">
        <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </svg>
      </div>

      <h1 class="login-title">{{ isRegister ? 'Create account' : 'Welcome back' }}</h1>
      <p class="login-subtitle muted">
        {{ isRegister ? 'Set up your company workspace in seconds' : 'Sign in to the WorkSight management portal' }}
      </p>

      <!-- Sign in -->
      <form v-if="!isRegister" class="login-form" @submit.prevent="submitLogin">
        <div class="field">
          <label class="field__label" for="li-username">Username</label>
          <input
            id="li-username"
            v-model="loginForm.username"
            class="input"
            type="text"
            placeholder="e.g. alice"
            autocomplete="username"
            required
          />
        </div>

        <div class="field">
          <label class="field__label" for="li-password">Password</label>
          <input
            id="li-password"
            v-model="loginForm.password"
            class="input"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button class="btn btn--primary login-submit" type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <!-- Register -->
      <form v-else class="login-form" @submit.prevent="submitRegister">
        <div class="field">
          <label class="field__label" for="rg-company">Company name <span class="muted">(optional)</span></label>
          <input
            id="rg-company"
            v-model="registerForm.company_name"
            class="input"
            type="text"
            placeholder="e.g. Acme Ltd"
            autocomplete="organization"
          />
        </div>

        <div class="field">
          <label class="field__label" for="rg-username">Username</label>
          <input
            id="rg-username"
            v-model="registerForm.username"
            class="input"
            type="text"
            placeholder="Choose a username"
            autocomplete="username"
            required
          />
        </div>

        <div class="field">
          <label class="field__label" for="rg-email">Email</label>
          <input
            id="rg-email"
            v-model="registerForm.email"
            class="input"
            type="email"
            placeholder="you@company.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label class="field__label" for="rg-password">Password</label>
          <input
            id="rg-password"
            v-model="registerForm.password"
            class="input"
            type="password"
            placeholder="At least 6 characters"
            autocomplete="new-password"
            minlength="6"
            required
          />
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button class="btn btn--primary login-submit" type="submit" :disabled="loading">
          {{ loading ? 'Creating account…' : 'Create account' }}
        </button>
      </form>

      <p class="login-switch">
        <template v-if="!isRegister">
          Don't have an account?
          <button type="button" class="link-btn" @click="switchMode(true)">Create one</button>
        </template>
        <template v-else>
          Already have an account?
          <button type="button" class="link-btn" @click="switchMode(false)">Sign in</button>
        </template>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../auth'

const router = useRouter()
const { login, register, loading } = useAuth()

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
    error.value = e.message || 'Login failed'
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
    error.value = e.message || 'Registration failed'
  }
}
</script>

<style scoped>
.login-stage {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 42px 38px;
  overflow: hidden;
}

/* iridescent liquid sheen sweeping the top corner */
.login-card__glow {
  position: absolute;
  top: -80px;
  right: -80px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(
    circle at center,
    rgba(91, 124, 255, 0.35) 0%,
    rgba(165, 236, 255, 0.25) 45%,
    transparent 70%
  );
  filter: blur(30px);
  pointer-events: none;
}

.brand-mark {
  width: 52px;
  height: 52px;
  border-radius: 17px;
  display: grid;
  place-items: center;
  margin-bottom: 22px;
  background: linear-gradient(135deg, #5b7cff, #2f4ce0);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.5),
    4px 6px 18px rgba(61, 91, 238, 0.45);
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

.link-btn:hover {
  text-decoration: underline;
}
</style>
