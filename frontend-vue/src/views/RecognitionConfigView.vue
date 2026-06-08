<template>
  <div class="reco-page">
    <div class="hg-panel page-head">
      <h3 class="hg-section-title">识别项配置</h3>
      <span class="count-text">共 <b>{{ list.length }}</b> 个识别项 · <b class="green">{{ enabledCount }}</b> 启用中</span>
    </div>

    <div v-loading="loading" element-loading-background="rgba(11,18,32,0.6)" class="reco-list">
      <div v-for="item in list" :key="item.id" class="hg-panel reco-card" :class="{ disabled: !item.enabled }">
        <div class="rc-left">
          <div class="rc-icon">
            <el-icon :size="22"><Aim /></el-icon>
          </div>
          <div class="rc-info">
            <div class="rc-name">{{ item.name }}</div>
            <div class="rc-sub">
              <span class="mono">{{ item.modelVersion }}</span>
              <el-tag size="small" effect="plain" :type="sensType(item.sensitivity)">
                灵敏度：{{ item.sensitivityText }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="rc-threshold">
          <div class="th-label">
            置信度阈值
            <span class="th-val mono">{{ Math.round(item.threshold * 100) }}%</span>
          </div>
          <el-slider
            v-model="item.threshold"
            :min="0.3"
            :max="0.99"
            :step="0.01"
            :show-tooltip="false"
            :disabled="!item.enabled"
            @change="(v) => onThreshold(item, v)"
          />
        </div>

        <div class="rc-action">
          <el-switch
            v-model="item.enabled"
            :loading="item._saving"
            @change="(v) => onToggle(item, v)"
          />
          <span class="state-text" :class="{ on: item.enabled }">
            {{ item.enabled ? '运行中' : '已停用' }}
          </span>
        </div>
      </div>

      <el-empty v-if="!loading && !list.length" description="暂无识别项" :image-size="90" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Aim } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getRecognitionItems, updateRecognitionItem } from '@/api/violation'

const loading = ref(false)
const list = ref([])
const enabledCount = computed(() => list.value.filter((i) => i.enabled).length)

function sensType(s) {
  return { high: 'danger', medium: 'warning', low: 'info' }[s] || 'info'
}

async function load() {
  loading.value = true
  try {
    const data = await getRecognitionItems()
    list.value = (data || []).map((i) => ({ ...i, _saving: false }))
  } catch {
    // 已提示
  } finally {
    loading.value = false
  }
}

async function onToggle(item, val) {
  item._saving = true
  try {
    await updateRecognitionItem(item.id, { enabled: val })
    ElMessage.success(`${item.name} 已${val ? '启用' : '停用'}`)
  } catch {
    item.enabled = !val
  } finally {
    item._saving = false
  }
}

let thTimer = null
async function onThreshold(item, val) {
  clearTimeout(thTimer)
  thTimer = setTimeout(async () => {
    try {
      await updateRecognitionItem(item.id, { threshold: val })
      ElMessage.success(`${item.name} 阈值已更新为 ${Math.round(val * 100)}%`)
    } catch {
      // 已提示
    }
  }, 200)
}

onMounted(load)
</script>

<style scoped>
.page-head {
  display: flex;
  align-items: baseline;
  gap: 14px;
  padding: 14px 18px;
  margin-bottom: 16px;
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

.reco-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}
.reco-card {
  display: grid;
  grid-template-columns: 1.3fr 1.4fr auto;
  align-items: center;
  gap: 24px;
  padding: 16px 20px;
  transition: border-color 0.15s;
}
.reco-card:hover {
  border-color: var(--hg-primary);
}
.reco-card.disabled {
  opacity: 0.6;
}

.rc-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.rc-icon {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  color: var(--hg-primary-2);
  background: rgba(34, 211, 238, 0.08);
  border: 1px solid var(--hg-border);
  flex-shrink: 0;
}
.rc-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--hg-text);
}
.rc-sub {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 6px;
}
.rc-sub .mono {
  font-family: var(--hg-mono);
  font-size: 12px;
  color: var(--hg-text-3);
}

.rc-threshold {
  min-width: 0;
}
.th-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: var(--hg-text-2);
  margin-bottom: 2px;
}
.th-val {
  color: var(--hg-primary-2);
  font-weight: 700;
}

.rc-action {
  display: flex;
  align-items: center;
  gap: 10px;
}
.state-text {
  font-size: 13px;
  color: var(--hg-text-3);
  width: 52px;
}
.state-text.on {
  color: var(--hg-success);
}

@media (max-width: 860px) {
  .reco-card {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}
</style>
