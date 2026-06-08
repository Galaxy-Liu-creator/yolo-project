<template>
  <div class="fence-page">
    <div class="hg-panel page-head">
      <div class="ph-left">
        <h3 class="hg-section-title">电子围栏配置</h3>
        <span class="count-text">共 <b>{{ list.length }}</b> 条围栏 · <b class="green">{{ enabledCount }}</b> 启用中</span>
      </div>
    </div>

    <div v-loading="loading" element-loading-background="rgba(11,18,32,0.6)" class="grid">
      <div v-for="f in list" :key="f.id" class="hg-panel fence-card" :class="{ disabled: !f.enabled }">
        <div class="fc-head">
          <span class="fc-name">{{ f.name }}</span>
          <el-tag size="small" effect="dark" :type="f.type === 'area' ? 'warning' : 'primary'">
            {{ f.typeText }}
          </el-tag>
        </div>

        <!-- mini 预览：1280x720 等比缩放到 240x135 -->
        <div class="fc-preview">
          <svg viewBox="0 0 1280 720" preserveAspectRatio="none" class="prev-svg">
            <defs>
              <pattern :id="`grid-${f.id}`" width="80" height="80" patternUnits="userSpaceOnUse">
                <path d="M 80 0 L 0 0 0 80" fill="none" stroke="rgba(120,160,220,0.12)" stroke-width="1" />
              </pattern>
            </defs>
            <rect width="1280" height="720" :fill="`url(#grid-${f.id})`" />
            <polyline
              :points="ptsStr(f.points)"
              :stroke="f.enabled ? (f.color || '#ff00ff') : '#5a6b86'"
              stroke-width="6"
              fill="none"
            />
            <circle
              v-for="(p, i) in f.points"
              :key="i"
              :cx="p[0]"
              :cy="p[1]"
              r="8"
              :fill="f.enabled ? (f.color || '#ff00ff') : '#5a6b86'"
            />
          </svg>
        </div>

        <div class="fc-meta">
          <div class="meta-item">
            <el-icon><Location /></el-icon><span>{{ f.scene }}</span>
          </div>
          <div class="meta-item">
            <el-icon><VideoCamera /></el-icon><span class="mono">{{ f.camera }}</span>
          </div>
        </div>

        <div class="fc-foot">
          <span class="created mono">{{ formatDateTime(f.createdAt) }}</span>
          <el-tag size="small" :type="f.enabled ? 'success' : 'info'" effect="plain">
            {{ f.enabled ? '启用' : '停用' }}
          </el-tag>
        </div>
      </div>

      <el-empty v-if="!loading && !list.length" description="暂无电子围栏" :image-size="90" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Location, VideoCamera } from '@element-plus/icons-vue'
import { getFences } from '@/api/violation'
import { formatDateTime } from '@/utils/format'

const loading = ref(false)
const list = ref([])
const enabledCount = computed(() => list.value.filter((f) => f.enabled).length)

function ptsStr(points) {
  return (points || []).map((p) => p.join(',')).join(' ')
}

async function load() {
  loading.value = true
  try {
    list.value = (await getFences()) || []
  } catch {
    // 已提示
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page-head {
  padding: 14px 18px;
  margin-bottom: 16px;
}
.ph-left {
  display: flex;
  align-items: baseline;
  gap: 14px;
}
.count-text {
  font-size: 13px;
  color: var(--hg-text-2);
}
.count-text b {
  color: var(--hg-primary-2);
  font-family: var(--hg-mono);
}
.count-text b.green {
  color: var(--hg-success);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  min-height: 200px;
}
.fence-card {
  padding: 14px 16px;
  transition: border-color 0.15s;
}
.fence-card:hover {
  border-color: var(--hg-primary);
}
.fence-card.disabled {
  opacity: 0.62;
}
.fc-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.fc-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--hg-text);
}
.fc-preview {
  height: 130px;
  background: #06080f;
  border: 1px solid var(--hg-border);
  overflow: hidden;
}
.prev-svg {
  width: 100%;
  height: 100%;
  display: block;
}
.fc-meta {
  display: flex;
  gap: 18px;
  margin-top: 12px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--hg-text-2);
}
.meta-item .el-icon {
  color: var(--hg-primary-2);
}
.mono {
  font-family: var(--hg-mono);
}
.fc-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--hg-border);
}
.created {
  font-size: 11px;
  color: var(--hg-text-3);
}
</style>
