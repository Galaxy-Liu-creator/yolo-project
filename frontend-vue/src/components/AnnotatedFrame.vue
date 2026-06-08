<template>
  <div ref="wrap" class="frame-wrap">
    <img
      ref="imgEl"
      :src="src"
      class="frame-img"
      @load="onImgLoad"
      @error="onImgError"
      alt="监控帧"
    />

    <!-- 覆盖层：检测框 + 围栏 + 时间戳，按渲染尺寸等比缩放 -->
    <div
      class="overlay"
      :style="{ width: render.w + 'px', height: render.h + 'px', left: render.left + 'px', top: render.top + 'px' }"
      v-show="ready"
    >
      <!-- 电子围栏（SVG 折线） -->
      <svg class="fence-svg" :width="render.w" :height="render.h">
        <polyline
          v-for="f in scaledFences"
          :key="f.id"
          :points="f.pointsStr"
          :stroke="f.color || '#ff00ff'"
          stroke-width="2.5"
          fill="none"
          stroke-dasharray="2 0"
        />
        <text
          v-for="f in scaledFences"
          :key="f.id + '-t'"
          :x="f.labelX"
          :y="f.labelY"
          :fill="f.color || '#ff00ff'"
          class="fence-label"
        >
          {{ f.name }}
        </text>
      </svg>

      <!-- 检测框 -->
      <div
        v-for="d in scaledDetections"
        :key="d.id"
        class="det-box"
        :style="{
          left: d.x + 'px',
          top: d.y + 'px',
          width: d.w + 'px',
          height: d.h + 'px',
          borderColor: d.color,
        }"
      >
        <span
          class="det-label"
          :style="{ background: d.color }"
        >
          {{ d.labelText }} {{ d.confText }}
        </span>
      </div>

      <!-- 时间戳 -->
      <div v-if="timestamp" class="timestamp">{{ timestamp }}</div>
    </div>

    <div v-if="!ready && !error" class="frame-loading">
      <el-icon class="is-loading"><Loading /></el-icon> 加载中...
    </div>
    <div v-if="error" class="frame-error">
      <el-icon><PictureFilled /></el-icon>
      <span>图片加载失败</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Loading, PictureFilled } from '@element-plus/icons-vue'
import { formatConfidence } from '@/utils/format'

const props = defineProps({
  src: { type: String, default: '' },
  imageWidth: { type: Number, default: 1280 },
  imageHeight: { type: Number, default: 720 },
  detections: { type: Array, default: () => [] },
  fences: { type: Array, default: () => [] },
  timestamp: { type: String, default: '' },
})

const wrap = ref(null)
const imgEl = ref(null)
const ready = ref(false)
const error = ref(false)

// 图片在容器内的实际渲染区域（object-fit: contain 计算）
const render = reactive({ w: 0, h: 0, left: 0, top: 0 })

// 原始坐标系尺寸
const natW = computed(() => props.imageWidth || 1280)
const natH = computed(() => props.imageHeight || 720)

const scaleX = computed(() => (natW.value ? render.w / natW.value : 1))
const scaleY = computed(() => (natH.value ? render.h / natH.value : 1))

const scaledDetections = computed(() =>
  (props.detections || []).map((d) => {
    const [x, y, w, h] = d.bbox || [0, 0, 0, 0]
    return {
      id: d.id,
      color: d.color || '#ff4d4f',
      labelText: d.labelText || d.label || '',
      confText: d.confidence != null ? formatConfidence(d.confidence) : '',
      x: x * scaleX.value,
      y: y * scaleY.value,
      w: w * scaleX.value,
      h: h * scaleY.value,
    }
  })
)

const scaledFences = computed(() =>
  (props.fences || []).map((f) => {
    const pts = (f.points || []).map(([px, py]) => [
      px * scaleX.value,
      py * scaleY.value,
    ])
    const first = pts[0] || [0, 0]
    return {
      id: f.id,
      name: f.name || '',
      color: f.color || '#ff00ff',
      pointsStr: pts.map((p) => p.join(',')).join(' '),
      labelX: first[0] + 6,
      labelY: Math.max(first[1] - 6, 12),
    }
  })
)

function computeRender() {
  if (!wrap.value || !imgEl.value) return
  const cw = wrap.value.clientWidth
  const ch = wrap.value.clientHeight
  const iw = imgEl.value.naturalWidth || natW.value
  const ih = imgEl.value.naturalHeight || natH.value
  if (!cw || !ch || !iw || !ih) return
  // object-fit: contain
  const scale = Math.min(cw / iw, ch / ih)
  render.w = iw * scale
  render.h = ih * scale
  render.left = (cw - render.w) / 2
  render.top = (ch - render.h) / 2
}

function onImgLoad() {
  error.value = false
  ready.value = true
  nextTick(computeRender)
}
function onImgError() {
  error.value = true
  ready.value = false
}

let ro = null
onMounted(() => {
  if (window.ResizeObserver && wrap.value) {
    ro = new ResizeObserver(() => computeRender())
    ro.observe(wrap.value)
  }
  window.addEventListener('resize', computeRender)
})
onBeforeUnmount(() => {
  ro && ro.disconnect()
  window.removeEventListener('resize', computeRender)
})
</script>

<style scoped>
.frame-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #06080f;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--hg-border);
}
.frame-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}
.overlay {
  position: absolute;
  pointer-events: none;
}
.fence-svg {
  position: absolute;
  left: 0;
  top: 0;
  overflow: visible;
}
.fence-label {
  font-size: 12px;
  font-weight: 600;
  paint-order: stroke;
  stroke: rgba(0, 0, 0, 0.6);
  stroke-width: 2px;
}
.det-box {
  position: absolute;
  border: 2px solid #ff4d4f;
  border-radius: 2px;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.35);
}
.det-label {
  position: absolute;
  left: -2px;
  top: -22px;
  padding: 1px 6px;
  font-size: 12px;
  line-height: 18px;
  color: #fff;
  white-space: nowrap;
  border-radius: 3px;
  font-weight: 600;
}
.timestamp {
  position: absolute;
  left: 12px;
  top: 10px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 20px;
  font-weight: 700;
  color: #5dff5d;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.8), 1px 1px 2px #000;
  letter-spacing: 1px;
}
.frame-loading,
.frame-error {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--hg-text-2);
  font-size: 14px;
}
.frame-error {
  flex-direction: column;
  gap: 10px;
}
.frame-error .el-icon {
  font-size: 40px;
}
</style>
