<template>
  <div class="space-bg" aria-hidden="true">
    <!-- Hero photo layer -->
    <div class="space-bg__photo"></div>
    <!-- Dark overlay so UI stays readable on top of the photo -->
    <div class="space-bg__shade"></div>
    <!-- Nebula clouds -->
    <div class="space-bg__nebula space-bg__nebula--a"></div>
    <div class="space-bg__nebula space-bg__nebula--b"></div>
    <div class="space-bg__nebula space-bg__nebula--c"></div>
    <!-- 3D starfield -->
    <canvas ref="canvas" class="space-bg__canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvas = ref(null)

let raf = 0
let stars = []
let meteors = []
let mouse = { x: 0, y: 0 }
let target = { x: 0, y: 0 }
let width = 0
let height = 0
let dpr = 1
let lastMeteor = 0

function createStars() {
  const count = Math.min(320, Math.floor((width * height) / 4200))
  stars = Array.from({ length: count }, () => {
    // depth: 0 = far, 1 = near. Near stars are bigger, brighter, move more.
    const depth = Math.random()
    return {
      x: Math.random() * width,
      y: Math.random() * height,
      depth,
      r: 0.4 + depth * 1.6,
      baseAlpha: 0.25 + depth * 0.6,
      twinkleSpeed: 0.4 + Math.random() * 1.4,
      twinklePhase: Math.random() * Math.PI * 2,
      drift: 2 + depth * 10, // px per second-ish
      hue: Math.random() < 0.12 ? 210 : Math.random() < 0.08 ? 260 : 0 // a few blue/violet stars
    }
  })
}

function spawnMeteor(now) {
  const speed = 320 + Math.random() * 260
  const angle = Math.PI * (0.72 + Math.random() * 0.12) // down-left diagonal
  meteors.push({
    x: width * (0.35 + Math.random() * 0.6),
    y: -20,
    vx: Math.cos(angle) * speed,
    vy: Math.sin(angle) * speed,
    life: 0,
    maxLife: 0.9 + Math.random() * 0.6
  })
  lastMeteor = now
}

function resize() {
  const el = canvas.value
  if (!el) return
  dpr = Math.min(window.devicePixelRatio || 1, 2)
  width = window.innerWidth
  height = window.innerHeight
  el.width = width * dpr
  el.height = height * dpr
  el.style.width = `${width}px`
  el.style.height = `${height}px`
  createStars()
}

function onMouseMove(e) {
  target.x = (e.clientX / width - 0.5) * 2  // -1 .. 1
  target.y = (e.clientY / height - 0.5) * 2
}

let prev = 0

function frame(now) {
  const el = canvas.value
  if (!el) return
  const ctx = el.getContext('2d')
  const dt = Math.min((now - prev) / 1000, 0.05)
  prev = now

  // Smooth parallax easing
  mouse.x += (target.x - mouse.x) * 0.04
  mouse.y += (target.y - mouse.y) * 0.04

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, width, height)

  // ---- Stars (far to near for proper layering) ----
  const sorted = stars
  for (const s of sorted) {
    // slow drift upward-left, wraps around edges
    s.x -= s.drift * dt
    s.y -= s.drift * 0.35 * dt
    if (s.x < -4) s.x = width + 4
    if (s.y < -4) s.y = height + 4

    // 3D parallax: near stars shift more with the mouse
    const px = s.x + mouse.x * (4 + s.depth * 26)
    const py = s.y + mouse.y * (3 + s.depth * 18)

    // twinkle
    const tw = 0.72 + 0.28 * Math.sin(now / 1000 * s.twinkleSpeed * 2 + s.twinklePhase)
    const alpha = s.baseAlpha * tw

    ctx.beginPath()
    if (s.hue) {
      ctx.fillStyle = `hsla(${s.hue}, 90%, 75%, ${alpha})`
    } else {
      ctx.fillStyle = `rgba(235, 242, 255, ${alpha})`
    }
    ctx.arc(px, py, s.r, 0, Math.PI * 2)
    ctx.fill()

    // glow on the nearest, biggest stars
    if (s.depth > 0.85) {
      ctx.beginPath()
      ctx.fillStyle = `rgba(160, 200, 255, ${alpha * 0.18})`
      ctx.arc(px, py, s.r * 3.2, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // ---- Shooting stars ----
  if (now - lastMeteor > 5500 + Math.random() * 5000) spawnMeteor(now)
  meteors = meteors.filter((m) => m.life < m.maxLife)
  for (const m of meteors) {
    m.life += dt
    m.x += m.vx * dt
    m.y += m.vy * dt
    const fade = 1 - m.life / m.maxLife
    const tailX = m.x - m.vx * 0.09
    const tailY = m.y - m.vy * 0.09
    const grad = ctx.createLinearGradient(m.x, m.y, tailX, tailY)
    grad.addColorStop(0, `rgba(190, 220, 255, ${0.9 * fade})`)
    grad.addColorStop(1, 'rgba(190, 220, 255, 0)')
    ctx.strokeStyle = grad
    ctx.lineWidth = 1.6
    ctx.beginPath()
    ctx.moveTo(m.x, m.y)
    ctx.lineTo(tailX, tailY)
    ctx.stroke()
  }

  raf = requestAnimationFrame(frame)
}

onMounted(() => {
  resize()
  prev = performance.now()
  lastMeteor = performance.now() - 3000
  raf = requestAnimationFrame(frame)
  window.addEventListener('resize', resize)
  window.addEventListener('mousemove', onMouseMove, { passive: true })
})

onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', onMouseMove)
})
</script>

<style scoped>
.space-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
  background:
    radial-gradient(1300px 900px at 78% -12%, rgba(46, 90, 200, 0.22) 0%, transparent 55%),
    radial-gradient(1000px 750px at 12% 112%, rgba(88, 48, 190, 0.16) 0%, transparent 52%),
    linear-gradient(165deg, #03081a 0%, #060f28 48%, #040a1e 100%);
}

/* WorkSight hero photo as the base layer */
.space-bg__photo {
  position: absolute;
  inset: 0;
  background: url('../assets/hero-bg.png') center / cover no-repeat;
  opacity: 0.85;
}

/* Darken + tint the photo so glass cards and text stay legible */
.space-bg__shade {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(100deg, rgba(3, 8, 26, 0.88) 0%, rgba(4, 10, 32, 0.55) 45%, rgba(4, 10, 30, 0.35) 100%),
    radial-gradient(1200px 800px at 80% -10%, rgba(46, 90, 200, 0.25), transparent 55%),
    linear-gradient(0deg, rgba(2, 6, 20, 0.5), rgba(2, 6, 20, 0.25));
}

.space-bg__nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(110px);
  opacity: 0.5;
  will-change: transform;
}

.space-bg__nebula--a {
  width: 640px;
  height: 640px;
  top: -180px;
  right: 4%;
  background: radial-gradient(circle, rgba(46, 125, 255, 0.42), transparent 65%);
  animation: nebula-a 34s ease-in-out infinite alternate;
}

.space-bg__nebula--b {
  width: 560px;
  height: 560px;
  bottom: -160px;
  left: -100px;
  background: radial-gradient(circle, rgba(120, 70, 255, 0.30), transparent 65%);
  animation: nebula-b 42s ease-in-out infinite alternate;
}

.space-bg__nebula--c {
  width: 460px;
  height: 460px;
  top: 38%;
  left: 40%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.20), transparent 65%);
  animation: nebula-c 48s ease-in-out infinite alternate;
}

@keyframes nebula-a { to { transform: translate(-110px, 90px) scale(1.15); } }
@keyframes nebula-b { to { transform: translate(130px, -80px) scale(1.1); } }
@keyframes nebula-c { to { transform: translate(-90px, -110px) scale(1.2); } }

.space-bg__canvas {
  position: absolute;
  inset: 0;
}

@media (prefers-reduced-motion: reduce) {
  .space-bg__nebula { animation: none; }
}

/* Light theme: professional bright sky, photo hidden, stars kept very subtle */
html[data-theme='light'] .space-bg {
  background:
    radial-gradient(1300px 900px at 78% -12%, rgba(46, 125, 255, 0.14) 0%, transparent 55%),
    radial-gradient(1000px 750px at 12% 112%, rgba(56, 189, 248, 0.12) 0%, transparent 52%),
    linear-gradient(165deg, #f2f6fe 0%, #e9eefb 48%, #f0f4fc 100%);
}
html[data-theme='light'] .space-bg__photo,
html[data-theme='light'] .space-bg__shade { display: none; }
html[data-theme='light'] .space-bg__nebula { opacity: 0.3; }
html[data-theme='light'] .space-bg__canvas { opacity: 0.35; }
</style>
