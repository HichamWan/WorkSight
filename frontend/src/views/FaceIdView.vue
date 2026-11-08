<template>
  <div class="face">
    <!-- Mode tabs -->
    <div class="face__tabs glass">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="face__tab"
        :class="{ 'face__tab--active': mode === tab.id }"
        @click="switchMode(tab.id)"
      >
        <span v-html="tab.icon"></span>{{ tab.label }}
      </button>
    </div>

    <!-- ============ ENROLL ============ -->
    <div v-if="mode === 'enroll'" class="face__grid">
      <section class="glass face__card">
        <h2 class="face__title">{{ t('enrollFace') }}</h2>
        <p class="muted face__hint">{{ t('enrollHint') }}</p>

        <div class="field">
          <label class="field__label">{{ t('selectEmployee') }}</label>
          <select v-model="selectedId" class="select">
            <option :value="null" disabled>{{ t('selectEmployee') }}</option>
            <option v-for="e in employees" :key="e.id" :value="e.id">
              {{ e.first_name }} {{ e.last_name }} · {{ e.employee_code }}
              <span v-if="e.face_registered"> ✓</span>
            </option>
          </select>
        </div>

        <div class="face__camera">
          <video ref="video" class="face__video" autoplay playsinline muted></video>
          <canvas ref="canvas" class="hidden"></canvas>
          <div v-if="!cameraReady" class="face__placeholder">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/>
            </svg>
            <span class="muted">{{ cameraError || t('cameraOff') }}</span>
          </div>
        </div>

        <div class="face__actions">
          <button class="btn btn--ghost" @click="startCamera">{{ t('startCamera') }}</button>
          <button
            class="btn btn--primary"
            :disabled="!cameraReady || !selectedId || busy"
            @click="captureAndRegister"
          >
            {{ busy ? t('processing') : t('captureEnroll') }}
          </button>
        </div>

        <p v-if="enrollError" class="form-error">{{ enrollError }}</p>
      </section>

      <section class="glass face__card">
        <h2 class="face__title">{{ t('enrollmentStatus') }}</h2>
        <p class="muted face__hint">{{ enrolledCount }} / {{ employees.length }} {{ t('employeesEnrolled') }}</p>

        <div class="face__progress">
          <div class="face__progress-bar" :style="{ width: enrollPct + '%' }"></div>
        </div>

        <div class="table-wrap face__table">
          <table class="table">
            <thead>
              <tr>
                <th>{{ t('employee') }}</th>
                <th>{{ t('department') }}</th>
                <th>{{ t('faceId') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in employees" :key="e.id">
                <td>{{ e.first_name }} {{ e.last_name }}</td>
                <td>{{ e.department || '—' }}</td>
                <td>
                  <span class="chip" :class="e.face_registered ? 'chip--success' : 'chip--warning'">
                    {{ e.face_registered ? t('registered') : t('notSet') }}
                  </span>
                </td>
              </tr>
              <tr v-if="!employees.length">
                <td colspan="3" class="muted">{{ t('loadingEmployees') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <!-- ============ VERIFY ============ -->
    <div v-else class="face__grid">
      <section class="glass face__card">
        <h2 class="face__title">{{ t('faceKiosk') }}</h2>
        <p class="muted face__hint">{{ t('kioskHint') }}</p>

        <div class="face__camera face__camera--lg">
          <video ref="video" class="face__video" autoplay playsinline muted></video>
          <canvas ref="canvas" class="hidden"></canvas>
          <div v-if="!cameraReady" class="face__placeholder">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/>
            </svg>
            <span class="muted">{{ cameraError || t('cameraOff') }}</span>
          </div>
        </div>

        <div class="face__actions">
          <button class="btn btn--ghost" @click="startCamera">{{ t('startCamera') }}</button>
          <button class="btn btn--primary" :disabled="!cameraReady || busy" @click="captureAndVerify">
            {{ busy ? t('processing') : t('scanFace') }}
          </button>
        </div>

        <p v-if="verifyError" class="form-error">{{ verifyError }}</p>
      </section>

      <section class="glass face__card">
        <h2 class="face__title">{{ t('scanResult') }}</h2>

        <div v-if="!result" class="face__result-empty">
          <p class="muted">{{ t('noScanYet') }}</p>
        </div>

        <div v-else-if="result.matched" class="face__result">
          <div class="face__result-head">
            <div class="face__result-avatar">{{ resultInitials }}</div>
            <div>
              <h3 class="face__result-name">{{ result.employee_name }}</h3>
              <span class="chip chip--success">{{ t('matchConfidence') }}: {{ confidencePct }}%</span>
            </div>
          </div>

          <div class="face__actions face__actions--wide">
            <button class="btn btn--primary" :disabled="busy" @click="recordCheck('in')">
              {{ t('checkInAction') }}
            </button>
            <button class="btn btn--ghost" :disabled="busy" @click="recordCheck('out')">
              {{ t('checkOutAction') }}
            </button>
          </div>
        </div>

        <div v-else class="face__result">
          <div class="face__result-head">
            <div class="face__result-avatar face__result-avatar--fail">?</div>
            <div>
              <h3 class="face__result-name">{{ t('noMatch') }}</h3>
              <span class="chip chip--danger">{{ t('tryAgain') }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import { useI18n } from '../i18n'
import { useToast } from '../toast'

const { t } = useI18n()
const toast = useToast()
const route = useRoute()

const mode = ref('enroll')
const tabs = computed(() => [
  {
    id: 'enroll',
    label: t('enrollFace'),
    icon: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/></svg>'
  },
  {
    id: 'verify',
    label: t('faceKiosk'),
    icon: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="3.2"/></svg>'
  }
])

const employees = ref([])
const selectedId = ref(null)
const video = ref(null)
const canvas = ref(null)
const cameraReady = ref(false)
const cameraError = ref('')
const busy = ref(false)
const enrollError = ref('')
const verifyError = ref('')
const result = ref(null)

let stream = null

const enrolledCount = computed(() => employees.value.filter((e) => e.face_registered).length)
const enrollPct = computed(() =>
  employees.value.length ? Math.round((enrolledCount.value / employees.value.length) * 100) : 0
)
const resultInitials = computed(() =>
  (result.value?.employee_name || '?')
    .split(' ')
    .map((p) => p[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()
)
const confidencePct = computed(() => Math.round((result.value?.confidence || 0) * 100))

async function loadEmployees() {
  try {
    const res = await api.employees()
    employees.value = res?.employees || []
    const preset = Number(route.query.employee)
    if (preset && employees.value.some((e) => e.id === preset)) selectedId.value = preset
    else if (!selectedId.value && employees.value.length) {
      selectedId.value = (employees.value.find((e) => !e.face_registered) || employees.value[0]).id
    }
  } catch (e) {
    toast.error(e.message)
  }
}
loadEmployees()

async function startCamera() {
  cameraError.value = ''
  try {
    stopCamera()
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
      audio: false
    })
    await new Promise((r) => requestAnimationFrame(r))
    if (video.value) {
      video.value.srcObject = stream
      await video.value.play().catch(() => {})
    }
    cameraReady.value = true
  } catch (e) {
    cameraReady.value = false
    cameraError.value = e?.name === 'NotAllowedError' ? t('cameraDenied') : t('cameraUnavailable')
  }
}

function stopCamera() {
  stream?.getTracks().forEach((track) => track.stop())
  stream = null
  cameraReady.value = false
}

function snapshot() {
  const el = video.value
  const cv = canvas.value
  if (!el || !cv) return null
  cv.width = el.videoWidth || 640
  cv.height = el.videoHeight || 480
  cv.getContext('2d').drawImage(el, 0, 0, cv.width, cv.height)
  return new Promise((resolve) => cv.toBlob(resolve, 'image/jpeg', 0.92))
}

async function captureAndRegister() {
  enrollError.value = ''
  const blob = await snapshot()
  if (!blob) return
  busy.value = true
  try {
    const file = new File([blob], 'face.jpg', { type: 'image/jpeg' })
    await api.registerFace(selectedId.value, file)
    const emp = employees.value.find((e) => e.id === selectedId.value)
    if (emp) emp.face_registered = true
    toast.success(t('faceEnrolled'))
  } catch (e) {
    enrollError.value = e.message
    toast.error(e.message)
  } finally {
    busy.value = false
  }
}

async function captureAndVerify() {
  verifyError.value = ''
  result.value = null
  const blob = await snapshot()
  if (!blob) return
  busy.value = true
  try {
    const file = new File([blob], 'scan.jpg', { type: 'image/jpeg' })
    result.value = await api.verifyFace(file)
  } catch (e) {
    verifyError.value = e.message
    toast.error(e.message)
  } finally {
    busy.value = false
  }
}

async function recordCheck(kind) {
  if (!result.value?.employee_id) return
  busy.value = true
  try {
    const payload = { employee_id: result.value.employee_id, timestamp: new Date().toISOString() }
    if (kind === 'in') await api.checkIn(payload)
    else await api.checkOut(payload)
    toast.success(kind === 'in' ? t('checkInDone') : t('checkOutDone'))
  } catch (e) {
    toast.error(e.message)
  } finally {
    busy.value = false
  }
}

async function switchMode(next) {
  mode.value = next
  result.value = null
  enrollError.value = ''
  verifyError.value = ''
  await startCamera()
}

onBeforeUnmount(() => stopCamera())
</script>

<style scoped>
.face {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* Tabs */
.face__tabs {
  display: flex;
  gap: 6px;
  padding: 6px;
}

.face__tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background: transparent;
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-2);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, box-shadow 0.15s ease;
}
.face__tab:hover { background: var(--row-hover); color: var(--text); }
.face__tab--active {
  background: var(--accent-soft);
  border-color: var(--accent-border);
  color: var(--accent-strong);
  box-shadow: var(--shadow-soft);
}

.face__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 18px;
  align-items: start;
}

.face__card { padding: 22px; }
.face__title { font-size: 1rem; font-weight: 700; }
.face__hint { font-size: 0.84rem; margin: 4px 0 16px; }

/* Camera */
.face__camera {
  position: relative;
  margin: 16px 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgba(4, 10, 28, 0.6);
  border: 1px solid var(--border);
  aspect-ratio: 4 / 3;
}
.face__camera--lg { aspect-ratio: 4 / 3; }

.face__video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.face__placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--text-muted);
  text-align: center;
  padding: 20px;
  font-size: 0.84rem;
}

.face__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.face__actions--wide { margin-top: 18px; }
.face__actions--wide .btn { flex: 1; }

.form-error {
  margin-top: 14px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--danger);
  background: var(--danger-soft);
  border: 1px solid var(--danger);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}

/* Enrollment progress */
.face__progress {
  height: 8px;
  border-radius: var(--radius-pill);
  background: var(--surface-2);
  border: 1px solid var(--hairline);
  overflow: hidden;
  margin-bottom: 16px;
}
.face__progress-bar {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: var(--radius-pill);
  transition: width 0.4s ease;
}

.face__table { max-height: 320px; overflow-y: auto; }

/* Result */
.face__result-empty {
  display: grid;
  place-items: center;
  min-height: 180px;
  text-align: center;
  font-size: 0.86rem;
}

.face__result-head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.face__result-avatar {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-gradient);
  box-shadow: 0 6px 18px -6px var(--accent-glow);
  flex-shrink: 0;
}
.face__result-avatar--fail { background: var(--danger); box-shadow: none; }

.face__result-name { font-size: 1.05rem; font-weight: 700; margin-bottom: 6px; }
</style>
