<template>
  <div class="detail" v-loading="loading" element-loading-background="rgba(11,18,32,0.6)">
    <!-- 顶部操作条 -->
    <div class="detail-head hg-panel">
      <div class="head-left">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2 class="head-title">监控详情</h2>
        <el-tag v-if="record.id" effect="plain" type="info" size="small">
          ID：{{ record.id }}
        </el-tag>
      </div>
      <el-button :icon="Clock" @click="historyVisible = true">历史记录</el-button>
    </div>

    <el-row :gutter="16" v-if="record.id">
      <!-- 左：标注帧 + 审核按钮 -->
      <el-col :xs="24" :lg="16">
        <div class="hg-panel frame-panel">
          <div class="frame-box">
            <AnnotatedFrame
              :src="frameUrl"
              :image-width="record.imageWidth"
              :image-height="record.imageHeight"
              :detections="record.detections"
              :fences="record.fences"
              :timestamp="frameTimestamp"
            />
            <!-- 放大入口 -->
            <button class="zoom-btn" title="全屏放大查看" @click="viewerVisible = true">
              <el-icon><ZoomIn /></el-icon>
              <span>放大</span>
            </button>
            <div class="zoom-hint" @click="viewerVisible = true">点击图片可放大查看</div>
          </div>

          <div class="review-bar">
            <div class="review-status">
              <span class="rs-label">当前结论：</span>
              <el-tag
                v-if="record.reviewResultText"
                :type="reviewTagType"
                effect="dark"
              >
                {{ record.reviewResultText }}
              </el-tag>
              <el-tag v-else type="info" effect="plain">尚未审核</el-tag>
            </div>
            <div class="review-actions">
              <el-button
                v-for="a in REVIEW_ACTIONS"
                :key="a.result"
                :type="a.type"
                :icon="actionIcon(a.result)"
                :loading="reviewing === a.result"
                @click="onReview(a)"
              >
                {{ a.text }}
              </el-button>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右：基本信息 -->
      <el-col :xs="24" :lg="8">
        <div class="hg-panel info-panel">
          <h3 class="hg-section-title">违章信息</h3>
          <el-descriptions :column="1" border class="info-desc">
            <el-descriptions-item label="违章类别">{{ record.category }}</el-descriptions-item>
            <el-descriptions-item label="违章等级">
              <el-tag :type="levelType(record.violationLevel)" effect="dark" size="small">
                {{ record.violationLevel }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="处理状态">
              <StatusTag :status="record.processStatus" :text="record.processStatusText" />
            </el-descriptions-item>
            <el-descriptions-item label="井队">{{ record.team }}</el-descriptions-item>
            <el-descriptions-item label="二级单位">{{ record.unit }}</el-descriptions-item>
            <el-descriptions-item label="场景">{{ record.scene }}</el-descriptions-item>
            <el-descriptions-item label="工况">{{ record.workCondition }}</el-descriptions-item>
            <el-descriptions-item label="报警类别">{{ record.alarmType }}</el-descriptions-item>
            <el-descriptions-item label="置信度">
              {{ formatConfidence(record.confidence) }}
            </el-descriptions-item>
            <el-descriptions-item label="运行版本">{{ record.version }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(record.createdAt) }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="det-list" v-if="record.detections && record.detections.length">
            <h4 class="sub-title">检测目标（{{ record.detections.length }}）</h4>
            <div
              v-for="d in record.detections"
              :key="d.id"
              class="det-item"
            >
              <span class="det-dot" :style="{ background: d.color }"></span>
              <span class="det-name">{{ d.labelText }}</span>
              <span class="det-conf">{{ formatConfidence(d.confidence) }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 历史记录抽屉 -->
    <el-drawer
      v-model="historyVisible"
      title="审核历史记录"
      size="420px"
      direction="rtl"
    >
      <el-timeline v-if="reviewHistory.length">
        <el-timeline-item
          v-for="(h, i) in reviewHistory"
          :key="i"
          :timestamp="formatDateTime(h.time)"
          :type="historyDotType(h.action)"
          placement="top"
        >
          <div class="hist-card">
            <div class="hist-row">
              <el-tag size="small" :type="historyDotType(h.action)" effect="dark">
                {{ h.actionText }}
              </el-tag>
              <span class="hist-op">操作人：{{ h.operator }}</span>
            </div>
            <div v-if="h.remark" class="hist-remark">备注：{{ h.remark }}</div>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无审核记录" :image-size="90" />
    </el-drawer>

    <!-- 全屏放大查看器 -->
    <FrameViewer
      v-model="viewerVisible"
      :src="frameUrl"
      :image-width="record.imageWidth"
      :image-height="record.imageHeight"
      :detections="record.detections"
      :fences="record.fences"
      :timestamp="frameTimestamp"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  Clock,
  CircleCheck,
  CircleClose,
  Operation,
  ZoomIn,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AnnotatedFrame from '@/components/AnnotatedFrame.vue'
import FrameViewer from '@/components/FrameViewer.vue'
import StatusTag from '@/components/StatusTag.vue'
import { formatDateTime, formatConfidence } from '@/utils/format'
import {
  resolveAssetUrl,
  violationLevelType,
  REVIEW_ACTIONS,
} from '@/utils/constants'
import { getRecordDetail, reviewRecord } from '@/api/records'

const route = useRoute()
const router = useRouter()
const levelType = violationLevelType

const loading = ref(false)
const reviewing = ref('')
const historyVisible = ref(false)
const viewerVisible = ref(false)
const record = reactive({})

const frameUrl = computed(() =>
  resolveAssetUrl(record.videoFrameUrl || record.imageUrl)
)
const frameTimestamp = computed(() => {
  if (!record.createdAt) return ''
  // 形如 2026-02-06 15:34:42
  return formatDateTime(record.createdAt)
})

const reviewHistory = computed(() => record.reviewHistory || [])

const reviewTagType = computed(() => {
  const map = {
    correct: 'success',
    wrong: 'danger',
    experiment_correct: 'warning',
  }
  return map[record.reviewResult] || 'info'
})

function actionIcon(result) {
  if (result === 'correct') return CircleCheck
  if (result === 'wrong') return CircleClose
  return Operation
}

function historyDotType(action) {
  const map = {
    correct: 'success',
    approved: 'success',
    wrong: 'danger',
    rejected: 'danger',
    experiment_correct: 'warning',
  }
  return map[action] || 'primary'
}

async function load() {
  const id = route.params.id
  loading.value = true
  try {
    const data = await getRecordDetail(id)
    Object.keys(record).forEach((k) => delete record[k])
    Object.assign(record, data)
  } catch {
    // 已提示
  } finally {
    loading.value = false
  }
}

async function onReview(action) {
  reviewing.value = action.result
  try {
    const data = await reviewRecord(record.id, { result: action.result, remark: '' })
    Object.assign(record, data)
    ElMessage.success(`已提交：${action.text}`)
  } catch {
    // 已提示
  } finally {
    reviewing.value = ''
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/records')
}

onMounted(load)
</script>

<style scoped>
.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  margin-bottom: 16px;
}
.head-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.head-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.frame-panel {
  padding: 16px;
}
.frame-box {
  position: relative;
}
.zoom-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  font-size: 13px;
  color: #eaf2ff;
  background: rgba(6, 12, 24, 0.66);
  border: 1px solid rgba(120, 160, 220, 0.4);
  cursor: pointer;
  transition: all 0.15s;
  z-index: 5;
}
.zoom-btn:hover {
  background: var(--hg-primary);
  border-color: var(--hg-primary);
}
.zoom-hint {
  position: absolute;
  bottom: 10px;
  right: 12px;
  font-size: 12px;
  color: var(--hg-text-2);
  background: rgba(6, 12, 24, 0.55);
  padding: 3px 10px;
  cursor: pointer;
  z-index: 5;
}
.review-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--hg-border);
}
.review-status {
  display: flex;
  align-items: center;
  gap: 8px;
}
.rs-label {
  color: var(--hg-text-2);
  font-size: 14px;
}
.review-actions {
  display: flex;
  gap: 10px;
}

.info-panel {
  padding: 16px 18px;
  height: 100%;
}
.info-desc {
  margin-top: 14px;
}
.info-desc :deep(.el-descriptions__label) {
  color: var(--hg-text-2);
  width: 92px;
}

.sub-title {
  margin: 18px 0 10px;
  font-size: 14px;
  color: var(--hg-text);
}
.det-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: var(--hg-bg-soft);
  margin-bottom: 8px;
}
.det-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.det-name {
  flex: 1;
  font-size: 13px;
}
.det-conf {
  font-size: 12px;
  color: var(--hg-primary-2);
  font-weight: 600;
}

.hist-card {
  background: var(--hg-bg-soft);
  border: 1px solid var(--hg-border);
  border-radius: 8px;
  padding: 10px 12px;
}
.hist-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.hist-op {
  font-size: 13px;
  color: var(--hg-text-2);
}
.hist-remark {
  margin-top: 6px;
  font-size: 12px;
  color: var(--hg-text-3);
}
</style>
