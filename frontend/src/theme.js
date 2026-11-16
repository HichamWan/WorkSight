import { ref } from 'vue'

const THEME_KEY = 'worksight_theme'
const MOTION_KEY = 'worksight_motion'

// Dark (deep navy + electric blue) is the default, like the BizNext reference
const theme = ref(localStorage.getItem(THEME_KEY) || 'dark')
const motion = ref(localStorage.getItem(MOTION_KEY) || 'on')

function applyTheme() {
  document.documentElement.dataset.theme = theme.value
}

function applyMotion() {
  document.documentElement.dataset.motion = motion.value
}

applyTheme()
applyMotion()

export function useTheme() {
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem(THEME_KEY, theme.value)
    applyTheme()
  }

  function setTheme(next) {
    theme.value = next === 'light' ? 'light' : 'dark'
    localStorage.setItem(THEME_KEY, theme.value)
    applyTheme()
  }

  function toggleMotion() {
    motion.value = motion.value === 'on' ? 'off' : 'on'
    localStorage.setItem(MOTION_KEY, motion.value)
    applyMotion()
  }

  return { theme, motion, toggleTheme, setTheme, toggleMotion }
}
