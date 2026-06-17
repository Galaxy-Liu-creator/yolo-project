<template>
  <div class="records">
    <!-- 筛选区 -->
    <div class="hg-panel filter-panel">
      <el-form :model="filters" class="filter-form">
        <div class="filter-grid">
          <el-form-item label="违章类别">
            <el-select v-model="filters.categoryCode" placeholder="全部" clearable filterable>
              <el-option
                v-for="o in meta.categories"
                :key="o.code"
                :label="o.name"
                :value="o.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="处理状态">
            <el-select v-model="filters.processStatus" placeholder="全部" clearable>
              <el-option
                v-for="o in statusOptions"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="运行版本">
            <el-select v-model="filters.version" placeholder="全部" clearable>
              <el-option v-for="v in meta.versions" :key="v" :label="v" :value="v" />
            </el-select>
          </el-form-item>

          <el-form-item label="二级单位">
            <el-select v-model="filters.unit" placeholder="全部" clearable filterable>
              <el-option
                v-for="o in meta.units"
                :key="o.code"
                :label="o.name"
                :value="o.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="井队">
            <el-select v-model="filters.team" placeholder="全部" clearable filterable>
              <el-option
                v-for="o in meta.teams"
                :key="o.code"
                :label="o.name"
                :value="o.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="场景">
            <el-select v-model="filters.sceneCode" placeholder="全部" clearable>
              <el-option
                v-for="o in meta.scenes"
                :key="o.code"
                :label="o.name"
                :value="o.code"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="创建时间" class="time-item">
            <el-date-picker
              v-model="timeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              value-format="YYYY-MM-DDTHH:mm:ss"
              :teleported="true"
            />
          </el-form-item>

          <el-form-item label="关键字">
            <el-input
              v-model="filters.keyword"
              placeholder="检测ID / 类别"
              clearable
              @keyup.enter="onSearch"
            />
          </el-form-item>
        </div>

        <div class="filter-actions">
          <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
          <el-button :icon="RefreshLeft" @click="onReset">重置</el-button>
          <el-button
            type="danger"
            plain
            :icon="Delete"
            :disabled="selectedIds.length === 0"
            @click="onBatchDelete"
          >
            批量删除<span v-if="selectedIds.length">（{{ selectedIds.length }}）</span>
          </el-button>
        </div>
      </el-form>
    </div>

    <!-- 表格 -->
    <div class="hg-panel table-panel">
      <div class="table-head">
        <h3 class="hg-section-title">监控记录</h3>
        <div class="count-text">
          一共 <span class="count-num">{{ total }}</span> 条违章数据
        </div>
      </div>

      <el-table
        ref="tableRef"
        :data="list"
        v-loading="loading"
        element-loading-background="rgba(11,18,32,0.6)"
        row-key="id"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="46" />
        <el-table-column prop="category" label="违章类别" min-width="170" show-overflow-tooltip />
        <el-table-column prop="team" label="井队" width="120" />
        <el-table-column prop="workCondition" label="工况" width="110" />
        <el-table-column label="图片" width="92">
          <template #default="{ row }">
            <el-image
              :src="resolveAssetUrl(row.thumbnailUrl)"
              :preview-src-list="[resolveAssetUrl(row.imageUrl)]"
              :preview-teleported="true"
              fit="cover"
              class="thumb"
            >
              <template #error>
                <div class="thumb-err"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            <span class="muted">{{ formatDateTime(row.createdAt) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="scene" label="场景" width="100" />
        <el-table-column label="处理状态" width="106" align="center">
          <template #default="{ row }">
            <StatusTag :status="row.processStatus" :text="row.processStatusText" />
          </template>
        </el-table-column>
        <el-table-column label="违章等级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="levelType(row.violationLevel)" effect="dark" size="small">
              {{ row.violationLevel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alarmType" label="报警类别" width="100" />
        <el-table-column prop="version" label="运行版本" width="116" />
        <el-table-column label="操作" width="158" fixed="right">
          <template #default="{ row }">
            <el-button
              text
              type="danger"
              size="small"
              :icon="Delete"
              @click="onDelete(row)"
            >
              删除
            </el-button>
            <el-button
              text
              type="primary"
              size="small"
              :icon="View"
              @click="goDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无违章数据" :image-size="90" />
        </template>
      </el-table>

      <div class="pager">
        <div class="count-text">
          一共 <span class="count-num">{{ total }}</span> 条违章数据
        </div>
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="fetchList"
          @size-change="onSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import {
  Search,
  RefreshLeft,
  Delete,
  View,
  Picture,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StatusTag from '@/components/StatusTag.vue'
import { formatDateTime } from '@/utils/format'
import { resolveAssetUrl, violationLevelType, PROCESS_STATUS_MAP } from '@/utils/constants'
import {
  getRecords,
  deleteRecord,
  batchDeleteRecords,
} from '@/api/records'
import {
  getCategories,
  getScenes,
  getTeams,
  getVersions,
  getUnits,
} from '@/api/meta'

const DEFAULT_FILTERS = {
  categoryCode: '',
  processStatus: '',
  version: '',
  unit: '',
  team: '',
  sceneCode: '',
  keyword: '',
}

const RECORDS_VIEW_STORAGE_KEY = 'aegislift.recordsViewState'

const recordsViewCache = {
  initialized: false,
  page: 1,
  pageSize: 10,
  filters: { ...DEFAULT_FILTERS },
  timeRange: [],
  scrollTop: 0,
}

const router = useRouter()
const levelType = violationLevelType

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const tableRef = ref(null)
const selectedIds = ref([])

const meta = reactive({
  categories: [],
  scenes: [],
  teams: [],
  versions: [],
  units: [],
})

const statusOptions = Object.entries(PROCESS_STATUS_MAP).map(([value, v]) => ({
  value,
  label: v.text,
}))

const filters = reactive({ ...DEFAULT_FILTERS })
const timeRange = ref([])

const shouldRestoreScroll = ref(false)

function getScrollContainer() {
  return document.querySelector('.main') || document.scrollingElement || document.documentElement
}

function saveViewState() {
  const scroller = getScrollContainer()
  const state = {
    initialized: true,
    page: page.value,
    pageSize: pageSize.value,
    filters: { ...filters },
    timeRange: Array.isArray(timeRange.value) ? [...timeRange.value] : [],
    scrollTop: scroller?.scrollTop || 0,
  }
  Object.assign(recordsViewCache, state)
  sessionStorage.setItem(RECORDS_VIEW_STORAGE_KEY, JSON.stringify(state))
}

function restoreViewState() {
  const raw = sessionStorage.getItem(RECORDS_VIEW_STORAGE_KEY)
  if (raw) {
    try {
      Object.assign(recordsViewCache, JSON.parse(raw))
    } catch {
      sessionStorage.removeItem(RECORDS_VIEW_STORAGE_KEY)
    }
  }
  if (!recordsViewCache.initialized) return
  page.value = recordsViewCache.page || 1
  pageSize.value = recordsViewCache.pageSize || 10
  Object.assign(filters, DEFAULT_FILTERS, recordsViewCache.filters || {})
  timeRange.value = Array.isArray(recordsViewCache.timeRange)
    ? [...recordsViewCache.timeRange]
    : []
  shouldRestoreScroll.value = true
}

async function restoreScrollPosition() {
  if (!shouldRestoreScroll.value) return
  await nextTick()
  await new Promise((resolve) => requestAnimationFrame(resolve))
  const scroller = getScrollContainer()
  if (scroller) scroller.scrollTop = recordsViewCache.scrollTop || 0
  window.setTimeout(() => {
    const delayedScroller = getScrollContainer()
    if (delayedScroller) delayedScroller.scrollTop = recordsViewCache.scrollTop || 0
  }, 120)
  shouldRestoreScroll.value = false
}

function scrollToTop() {
  const scroller = getScrollContainer()
  if (scroller) scroller.scrollTop = 0
}

function buildParams() {
  const params = { page: page.value, pageSize: pageSize.value }
  for (const [k, val] of Object.entries(filters)) {
    if (val) params[k] = val
  }
  if (timeRange.value && timeRange.value.length === 2) {
    params.startTime = timeRange.value[0]
    params.endTime = timeRange.value[1]
  }
  return params
}

async function fetchList() {
  loading.value = true
  try {
    const data = await getRecords(buildParams())
    list.value = data.items || []
    total.value = data.total || 0
    await restoreScrollPosition()
  } catch {
    // 拦截器已提示
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  recordsViewCache.scrollTop = 0
  shouldRestoreScroll.value = false
  scrollToTop()
  fetchList()
}

function onReset() {
  Object.assign(filters, DEFAULT_FILTERS)
  timeRange.value = []
  page.value = 1
  recordsViewCache.scrollTop = 0
  shouldRestoreScroll.value = false
  scrollToTop()
  fetchList()
}

function onSizeChange() {
  page.value = 1
  recordsViewCache.scrollTop = 0
  shouldRestoreScroll.value = false
  scrollToTop()
  fetchList()
}

function onSelectionChange(rows) {
  selectedIds.value = rows.map((r) => r.id)
}

function goDetail(row) {
  saveViewState()
  router.push(`/records/${row.id}`)
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除该违章记录（${row.category}）？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await deleteRecord(row.id)
    ElMessage.success('删除成功')
    if (list.value.length === 1 && page.value > 1) page.value -= 1
    fetchList()
  } catch {
    // 已提示
  }
}

async function onBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确认批量删除选中的 ${selectedIds.value.length} 条记录？`,
      '批量删除',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    const res = await batchDeleteRecords(selectedIds.value)
    ElMessage.success(`已删除 ${res?.deleted ?? selectedIds.value.length} 条`)
    selectedIds.value = []
    page.value = 1
    fetchList()
  } catch {
    // 已提示
  }
}

async function loadMeta() {
  try {
    const [categories, scenes, teams, versions, units] = await Promise.all([
      getCategories(),
      getScenes(),
      getTeams(),
      getVersions(),
      getUnits(),
    ])
    meta.categories = categories || []
    meta.scenes = scenes || []
    meta.teams = teams || []
    meta.versions = versions || []
    meta.units = units || []
  } catch {
    // 已提示
  }
}

onMounted(() => {
  restoreViewState()
  loadMeta()
  fetchList()
})

onBeforeRouteLeave(() => {
  saveViewState()
})
</script>

<style scoped>
.filter-panel {
  padding: 18px 18px 8px;
  margin-bottom: 16px;
}
.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0 18px;
}
.filter-form :deep(.el-form-item) {
  margin-bottom: 14px;
}
.filter-form :deep(.el-form-item__label) {
  color: var(--hg-text-2);
  width: 76px;
}
.filter-form :deep(.el-select),
.filter-form :deep(.el-input),
.filter-form :deep(.el-date-editor) {
  width: 100%;
}
.time-item {
  grid-column: span 2;
}
.filter-actions {
  display: flex;
  gap: 10px;
  padding-top: 4px;
  border-top: 1px dashed var(--hg-border);
  margin-top: 4px;
  padding-top: 14px;
}

.table-panel {
  padding: 16px 18px 18px;
}
.table-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.count-text {
  font-size: 13px;
  color: var(--hg-text-2);
}
.count-num {
  color: var(--hg-primary-2);
  font-weight: 700;
  font-size: 15px;
  margin: 0 2px;
}

.thumb {
  width: 64px;
  height: 40px;
  border-radius: 2px;
  border: 1px solid var(--hg-border);
}
.thumb-err {
  width: 64px;
  height: 40px;
  display: grid;
  place-items: center;
  background: var(--hg-bg-soft);
  color: var(--hg-text-3);
  border-radius: 2px;
}
.muted {
  color: var(--hg-text-2);
  font-size: 12px;
}

.pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
}
</style>
