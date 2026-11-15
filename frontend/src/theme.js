import { ref } from 'vue'

const THEME_KEY = 'worksight_theme'

// Dark (deep navy + electric blue) is the default, like the BizNext reference
const theme = ref(localStorage.getItem(THEME_KEY) || 'dark')

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
