<template>
  <div class="space-bg" aria-hidden="true">
    <!-- Hero photo layer (static) -->
    <div class="space-bg__photo"></div>
    <!-- Dark overlay so UI stays readable on top of the photo -->
    <div class="space-bg__shade"></div>
    <!-- Static soft glows (no motion) -->
    <div class="space-bg__glow space-bg__glow--a"></div>
    <div class="space-bg__glow space-bg__glow--b"></div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.space-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
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

/* Soft static color glows */
.space-bg__glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(110px);
}

.space-bg__glow--a {
  width: 640px;
  height: 640px;
  top: -180px;
  right: 4%;
  background: radial-gradient(circle, rgba(46, 125, 255, 0.30), transparent 65%);
}

.space-bg__glow--b {
  width: 560px;
  height: 560px;
  bottom: -160px;
  left: -100px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.16), transparent 65%);
}

/* Light theme: professional bright sky, photo hidden */
html[data-theme='light'] .space-bg__photo,
html[data-theme='light'] .space-bg__shade { display: none; }

html[data-theme='light'] .space-bg__glow--a {
  background: radial-gradient(circle, rgba(46, 125, 255, 0.14), transparent 65%);
}
html[data-theme='light'] .space-bg__glow--b {
  background: radial-gradient(circle, rgba(56, 189, 248, 0.10), transparent 65%);
}
</style>
