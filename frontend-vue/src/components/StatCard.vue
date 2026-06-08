<template>
  <div class="stat-card hg-panel" :style="{ '--accent': accent }">
    <div class="stat-icon">
      <el-icon :size="24"><component :is="icon" /></el-icon>
    </div>
    <div class="stat-body">
      <div class="stat-value">
        <span class="num">{{ displayValue }}</span>
        <span v-if="suffix" class="suffix">{{ suffix }}</span>
      </div>
      <div class="stat-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  value: { type: [Number, String], default: 0 },
  suffix: { type: String, default: '' },
  icon: { type: [String, Object], default: 'DataLine' },
  accent: { type: String, default: '#2f7dff' },
  percent: { type: Boolean, default: false },
})

const displayValue = computed(() => {
  if (props.percent) {
    const n = Number(props.value) || 0
    return (n * 100).toFixed(0) + '%'
  }
  if (typeof props.value === 'number') {
    return props.value.toLocaleString('en-US')
  }
  return props.value
})
</script>

<style scoped>
.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
  overflow: hidden;
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 0;
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, var(--accent), color-mix(in srgb, var(--accent) 55%, #22d3ee));
  flex-shrink: 0;
}
.stat-body {
  flex: 1;
  min-width: 0;
}
.stat-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.num {
  font-size: 28px;
  font-weight: 700;
  color: var(--hg-text);
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}
.suffix {
  font-size: 13px;
  color: var(--hg-text-2);
}
.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: var(--hg-text-2);
}
</style>
