<template>
  <div class="review-page">
    <div class="hg-panel filter-bar">
      <div class="fb-left">
        <h3 class="hg-section-title">审核记录</h3>
        <span class="count-text">共 <b>{{ total }}</b> 条审核流水</span>
      </div>
      <div class="fb-right">
        <el-select v-model="resultFilter" placeholder="全部结论" clearable @change="onFilter" style="width: 160px">
          <el-option label="识别正确" value="correct" />
          <el-option label="识别错误" value="wrong" />
          <el-option label="实验正确" value="experiment_correct" />
        </el-select>
        <el-button :icon="RefreshLeft" @click="onReset">重置</el-button>
      </div>
    </div>

    <div class="hg-panel table-panel">
      <el-table :data="list" v-loading="loading" element-loading-background="rgba(11,18,32,0.6)">
        <el-table-column label="审核时间" width="180">
          <template #default="{ row }">
            <span class="mono">{{ formatDateTime(row.time) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="审核人" width="130">
          <template #default="{ row }">
            <div class="operator">
              <span class="op-dot"></span>{{ row.operator }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="记录ID" width="120">
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="goRecord(row.recordId)">
              {{ row.recordId }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="违章类别" min-width="170" show-overflow-tooltip />
        <el-table-column label="状态流转" width="200">
          <template #default="{ row }">
            <span class="flow">
              <el-tag size="small" effect="plain" type="info">{{ row.fromStatusText }}</el-tag>
              <el-icon class="arrow"><Right /></el-icon>
              <el-tag size="small" effect="dark" :type="toType(row.toStatus)">{{ row.toStatusText }}</el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="审核结论" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="resultType(row.result)" effect="dark" size="small">{{ row.resultText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140">
          <template #default="{ row }">
            <span :class="{ muted: !row.remark }">{{ row.remark || '—' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="load"
          @size-change="onSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RefreshLeft, Right } from '@element-plus/icons-vue'
import { getReviewLogs } from '@/api/violation'
import { formatDateTime } from '@/utils/format'

const router = useRouter()
const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const resultFilter = ref('')

function resultType(r) {
  return { correct: 'success', wrong: 'danger', experiment_correct: 'warning' }[r] || 'info'
}
function toType(s) {
  return { approved: 'success', rejected: 'danger' }[s] || 'info'
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, pageSize: pageSize.value }
    if (resultFilter.value) params.result = resultFilter.value
    const data = await getReviewLogs(params)
    list.value = data.items || []
    total.value = data.total || 0
  } catch {
    // 已提示
  } finally {
    loading.value = false
  }
}

function onFilter() {
  page.value = 1
  load()
}
function onReset() {
  resultFilter.value = ''
  page.value = 1
  load()
}
function onSizeChange() {
  page.value = 1
  load()
}
function goRecord(id) {
  router.push(`/records/${id}`)
}

onMounted(load)
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  margin-bottom: 16px;
}
.fb-left {
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
.fb-right {
  display: flex;
  gap: 10px;
}

.table-panel {
  padding: 16px 18px 18px;
}
.mono {
  font-family: var(--hg-mono);
  font-size: 12px;
  color: var(--hg-text-2);
}
.operator {
  display: flex;
  align-items: center;
  gap: 8px;
}
.op-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--hg-primary-2);
}
.flow {
  display: flex;
  align-items: center;
  gap: 8px;
}
.arrow {
  color: var(--hg-text-3);
}
.muted {
  color: var(--hg-text-3);
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
