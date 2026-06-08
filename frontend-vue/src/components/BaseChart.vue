<template>
  <div ref="el" class="base-chart"></div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '300px' },
})

const el = ref(null)
let chart = null

function render() {
  if (!el.value) return
  if (!chart) {
    chart = echarts.init(el.value, 'dark')
  }
  chart.setOption(props.option || {}, true)
}

function resize() {
  chart && chart.resize()
}

onMounted(async () => {
  await nextTick()
  if (el.value) el.value.style.height = props.height
  render()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart && chart.dispose()
  chart = null
})

watch(
  () => props.option,
  () => render(),
  { deep: true }
)
</script>

<style scoped>
.base-chart {
  width: 100%;
}
/* echarts dark 主题背景透明化 */
:deep(canvas) {
  background: transparent !important;
}
</style>
