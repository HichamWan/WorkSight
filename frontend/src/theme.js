import { ref } from 'vue'

const THEME_KEY = 'worksight_theme'

// Light mode is the default
const theme = ref(localStorage.getItem(THEME_KEY) || 'light')

function applyTheme() {
  document.documentElement.dataset.theme = theme.value
}
applyTheme()

export function useTheme() {
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem(THEME_KEY, theme.value)
    applyTheme()
  }

  return { theme, toggleTheme }
}
