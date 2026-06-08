<template>
  <el-dialog
    v-model="visible"
    fullscreen
    :show-close="false"
    :append-to-body="true"
    class="viewer-dialog"
    @opened="onOpened"
  >
    <template #header>
      <div class="viewer-head">
        <div class="vh-left">
          <el-icon><ZoomIn /></el-icon>
          <span class="vh-title">监控帧 · 放大查看</span>
          <span class="vh-zoom">{{ Math.round(scale * 100) }}%</span>
        </div>
        <div class="vh-tools">
          <el-button-group>
            <el-button :icon="ZoomOut" @click="zoomBy(-0.2)" />
            <el-button :icon="ZoomIn" @click="zoomBy(0.2)" />
            <el-button :icon="FullScreen" @click="reset">适应</el-button>
          </el-button-group>
          <el-button :icon="Close" circle class="vh-close" @click="visible = false" />
        </div>
      </div>
    </template>

    <div
      ref="stage"
      class="viewer-stage"
      :class="{ grabbing }"
      @wheel.prevent="onWheel"
      @mousedown="onDown"
      @dblclick="reset"
    >
      <div
        class="viewer-canvas"
        :style="{ transform: `translate(${tx}px, ${ty}px) scale(${scale})` }"
      >
        <AnnotatedFrame
          :src="src"
          :image-width="imageWidth"
          :image-height="imageHeight"
          :detections="detections"
          :fences="fences"
          :timestamp="timestamp"
        />
      </div>

      <div class="viewer-hint">
        滚轮缩放 · 拖拽平移 · 双击复位
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ZoomIn, ZoomOut, FullScreen, Close } from '@element-plus/icons-vue'
import AnnotatedFrame from '@/components/AnnotatedFrame.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  src: { type: String, default: '' },
  imageWidth: { type: Number, default: 1280 },
  imageHeight: { type: Number, default: 720 },
  detections: { type: Array, default: () => [] },
  fences: { type: Array, default: () => [] },
  timestamp: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
watch(() => props.modelValue, (v) => (visible.value = v))
watch(visible, (v) => {
  emit('update:modelValue', v)
  if (!v) reset()
})

const stage = ref(null)
const scale = ref(1)
const tx = ref(0)
const ty = ref(0)
const grabbing = ref(false)

const MIN = 0.5
const MAX = 6

function clamp(v, min, max) {
  return Math.min(max, Math.max(min, v))
}

function reset() {
  scale.value = 1
  tx.value = 0
  ty.value = 0
}

function onOpened() {
  reset()
}

function zoomBy(delta) {
  scale.value = clamp(scale.value + delta, MIN, MAX)
}

// 以鼠标位置为中心缩放
function onWheel(e) {
  if (!stage.value) return
  const rect = stage.value.getBoundingClientRect()
  const cx = e.clientX - rect.left - rect.width / 2
  const cy = e.clientY - rect.top - rect.height / 2
  const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15
  const next = clamp(scale.value * factor, MIN, MAX)
  const ratio = next / scale.value
  // 保持鼠标指向的内容点不动
  tx.value = cx - (cx - tx.value) * ratio
  ty.value = cy - (cy - ty.value) * ratio
  scale.value = next
}

// 拖拽平移
let startX = 0
let startY = 0
let baseTx = 0
let baseTy = 0
function onDown(e) {
  grabbing.value = true
  startX = e.clientX
  startY = e.clientY
  baseTx = tx.value
  baseTy = ty.value
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}
function onMove(e) {
  tx.value = baseTx + (e.clientX - startX)
  ty.value = baseTy + (e.clientY - startY)
}
function onUp() {
  grabbing.value = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', onUp)
}
</script>

<style scoped>
.viewer-dialog :deep(.el-dialog) {
  background: #05080f;
}
.viewer-dialog :deep(.el-dialog__header) {
  padding: 0;
  margin: 0;
  border-bottom: 1px solid var(--hg-border);
}
.viewer-dialog :deep(.el-dialog__body) {
  padding: 0;
  height: calc(100vh - 58px);
}

.viewer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 58px;
  padding: 0 20px;
  background: linear-gradient(90deg, #0c1626, #122036);
}
.vh-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--hg-text);
}
.vh-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
}
.vh-zoom {
  font-family: var(--hg-mono);
  font-size: 13px;
  color: var(--hg-primary-2);
  padding: 2px 8px;
  border: 1px solid var(--hg-border);
}
.vh-tools {
  display: flex;
  align-items: center;
  gap: 14px;
}
.vh-close {
  background: rgba(255, 77, 79, 0.12);
  border-color: rgba(255, 77, 79, 0.4);
  color: #ff7875;
}

.viewer-stage {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: grid;
  place-items: center;
  cursor: grab;
  background:
    radial-gradient(1200px 700px at 50% 45%, rgba(20, 34, 58, 0.5), transparent 70%),
    #05080f;
}
.viewer-stage.grabbing {
  cursor: grabbing;
}
.viewer-canvas {
  width: min(80vw, 1280px);
  transform-origin: center center;
  transition: transform 0.04s linear;
  will-change: transform;
}
.viewer-canvas :deep(.frame-wrap) {
  border-radius: 0;
}
.viewer-hint {
  position: absolute;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: var(--hg-text-3);
  background: rgba(6, 12, 24, 0.7);
  padding: 6px 14px;
  border: 1px solid var(--hg-border);
  letter-spacing: 1px;
  pointer-events: none;
}
</style>
