<template>
  <SpaceBackground />
  <router-view />
  <ToastHost />
</template>

<script setup>
import SpaceBackground from './components/SpaceBackground.vue'
import ToastHost from './components/ToastHost.vue'
</script>
