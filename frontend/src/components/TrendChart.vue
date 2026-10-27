<template>
  <div class="chart-wrap">
    <Line v-if="hasData" :data="chartData" :options="chartOptions" />
    <p v-else class="chart-empty muted">No trend data available</p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { useTheme } from '../theme'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

const props = defineProps({
  /** Array of { date, present, late, absent } */
  trend: { type: Array, default: () => [] }
})

const { theme } = useTheme()

// Chart.js cannot read CSS variables, so resolve them from the active theme.
const palette = ref(readPalette())

function readPalette() {
  if (typeof window === 'undefined') return fallbackPalette()
  const styles = getComputedStyle(document.documentElement)
  const read = (name, fallback) => (styles.getPropertyValue(name) || fallback).trim()
  return {
    accent: read('--accent', '#2e7dff'),
    warning: read('--warning', '#fbbf24'),
    neutral: read('--border-strong', '#82aaff'),
    text: read('--text-secondary', '#a9b8dc'),
    grid: read('--border', 'rgba(120, 160, 255, 0.18)')
  }
}

function fallbackPalette() {
  return {
    accent: '#2e7dff',
    warning: '#fbbf24',
    neutral: '#82aaff',
    text: '#a9b8dc',
    grid: 'rgba(120, 160, 255, 0.18)'
  }
}

// Re-read the palette whenever the user switches light/dark mode.
watch(theme, () => {
  requestAnimationFrame(() => {
    palette.value = readPalette()
  })
})

const hasData = computed(() => props.trend.length > 0)

function shortDate(iso) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const chartData = computed(() => ({
  labels: props.trend.map((day) => shortDate(day.date)),
  datasets: [
    {
      label: 'Present',
      data: props.trend.map((day) => day.present ?? 0),
      borderColor: palette.value.accent,
      backgroundColor: `${palette.value.accent}22`,
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointHoverRadius: 5
    },
    {
      label: 'Late',
      data: props.trend.map((day) => day.late ?? 0),
      borderColor: palette.value.warning,
      backgroundColor: `${palette.value.warning}22`,
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointHoverRadius: 5
    },
    {
      label: 'Absent',
      data: props.trend.map((day) => day.absent ?? 0),
      borderColor: palette.value.neutral,
      backgroundColor: `${palette.value.neutral}22`,
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointHoverRadius: 5
    }
  ]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      labels: { color: palette.value.text, usePointStyle: true, boxWidth: 8 }
    },
    tooltip: {
      backgroundColor: 'rgba(20, 24, 20, 0.92)',
      titleColor: '#fff',
      bodyColor: '#fff',
      padding: 10,
      displayColors: true
    }
  },
  scales: {
    x: {
      grid: { color: palette.value.grid, drawBorder: false },
      ticks: { color: palette.value.text }
    },
    y: {
      beginAtZero: true,
      grid: { color: palette.value.grid, drawBorder: false },
      ticks: { color: palette.value.text, precision: 0 }
    }
  }
}))
</script>

<style scoped>
.chart-wrap {
  position: relative;
  height: 260px;
  width: 100%;
}

.chart-empty {
  display: grid;
  place-items: center;
  height: 100%;
  font-size: 0.85rem;
}
</style>
