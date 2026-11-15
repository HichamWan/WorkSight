<template>
  <div v-if="totalPages > 1" class="pager">
    <span class="pager__info muted">{{ total }} records</span>
    <div class="pager__controls">
      <button class="btn btn--sm btn--ghost" :disabled="page <= 1" @click="emit('change', page - 1)">
        Prev
      </button>
      <button
        v-for="p in visiblePages"
        :key="p"
        class="btn btn--sm"
        :class="p === page ? 'btn--primary' : 'btn--ghost'"
        @click="emit('change', p)"
      >
        {{ p }}
      </button>
      <button class="btn btn--sm btn--ghost" :disabled="page >= totalPages" @click="emit('change', page + 1)">
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  total: { type: Number, default: 0 }
})

const emit = defineEmits(['change'])

// Show at most 5 page buttons around the current page.
const visiblePages = computed(() => {
  const max = 5
  if (props.totalPages <= max) {
    return Array.from({ length: props.totalPages }, (_, i) => i + 1)
  }
  let start = Math.max(1, props.page - 2)
  const end = Math.min(props.totalPages, start + max - 1)
  start = Math.max(1, end - max + 1)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})
</script>

<style scoped>
.pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding-top: 16px;
  flex-wrap: wrap;
}

.pager__info {
  font-size: 0.8rem;
}

.pager__controls {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

@media (max-width: 600px) {
  .pager { justify-content: center; }
}
</style>
