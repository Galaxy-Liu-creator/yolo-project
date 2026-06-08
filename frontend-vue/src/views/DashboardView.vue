<template>
  <div class="dashboard" v-loading="loading" element-loading-background="rgba(11,18,32,0.6)">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="12" :md="6" v-for="c in statCards" :key="c.label">
        <StatCard
          :label="c.label"
          :value="c.value"
          :suffix="c.suffix"
          :icon="c.icon"
          :accent="c.accent"
          :percent="c.percent"
        />
      </el-col>
    </el-row>

    <!-- 趋势 + 类别 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="15">
        <div class="hg-panel chart-panel">
          <div class="panel-head">
            <h3 class="hg-section-title">近 7 天违章趋势</h3>
            <el-tag size="small" effect="plain" type="info">实时统计</el-tag>
          </div>
          <BaseChart :option="trendOption" height="320px" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="9">
        <div class="hg-panel chart-panel">
          <div class="panel-head">
            <h3 class="hg-section-title">违章类别分布</h3>
          </div>
          <BaseChart :option="categoryOption" height="320px" />
        </div>
      </el-col>
    </el-row>

    <!-- 状态分布 + 最新告警 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="9">
        <div class="hg-panel chart-panel">
          <div class="panel-head">
            <h3 class="hg-section-title">处理状态分布</h3>
          </div>
          <BaseChart :option="statusOption" height="300px" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="15">
        <div class="hg-panel chart-panel">
          <div class="panel-head">
            <h3 class="hg-section-title">最新告警</h3>
            <el-button
              text
              type="primary"
              size="small"
              @click="$router.push('/records')"
            >
              查看全部
            </el-button>
          </div>
          <el-table
            :data="recentAlarms"
            size="small"
            class="alarm-table"
            @row-click="goDetail"
          >
            <el-table-column type="index" label="#" width="46" />
            <el-table-column prop="category" label="违章类别" min-width="180" show-overflow-tooltip />
            <el-table-column prop="team" label="井队" width="120" />
            <el-table-column prop="scene" label="场景" width="100" />
            <el-table-column label="违章等级" width="92" align="center">
              <template #default="{ row }">
                <el-tag :type="levelType(row.violationLevel)" effect="dark" size="small">
                  {{ row.violationLevel }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="处理状态" width="106" align="center">
              <template #default="{ row }">
                <StatusTag :status="row.processStatus" :text="row.processStatusText" />
              </template>
            </el-table-column>
            <el-table-column label="时间" width="160">
              <template #default="{ row }">
                <span class="time-cell">{{ formatDateTime(row.createdAt) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Warning,
  Bell,
  Clock,
  VideoCamera,
} from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import BaseChart from '@/components/BaseChart.vue'
import StatusTag from '@/components/StatusTag.vue'
import { formatDateTime } from '@/utils/format'
import { violationLevelType } from '@/utils/constants'
import { useThemeStore } from '@/stores/theme'
import {
  getStats,
  getTrend,
  getCategoryDistribution,
  getStatusDistribution,
  getRecentAlarms,
} from '@/api/dashboard'

const router = useRouter()
const themeStore = useThemeStore()
const loading = ref(false)

// 根据主题动态返回图表文字颜色
const chartTextColor = computed(() => themeStore.isDark ? '#a4b1c7' : '#4a5a72')
const chartLabelColor = computed(() => themeStore.isDark ? '#cdd8ec' : '#1a2535')
const chartLineColor = computed(() => themeStore.isDark ? '#3a4a66' : '#d0d9e6')
const chartBorderColor = computed(() => themeStore.isDark ? '#16223a' : '#ffffff')

const stats = reactive({
  totalViolations: 0,
  todayAlerts: 0,
  pendingReview: 0,
  onlineCameras: 0,
  totalCameras: 0,
  handledRate: 0,
})

const trend = reactive({ dates: [], series: [] })
const categoryData = ref([])
const statusData = ref([])
const recentAlarms = ref([])

const levelType = violationLevelType

const statCards = computed(() => [
  {
    label: '累计违章总数',
    value: stats.totalViolations,
    icon: Warning,
    accent: '#2f7dff',
  },
  {
    label: '今日告警',
    value: stats.todayAlerts,
    icon: Bell,
    accent: '#ff6b3d',
  },
  {
    label: '待审核',
    value: stats.pendingReview,
    icon: Clock,
    accent: '#faad14',
  },
  {
    label: '在线摄像头',
    value: stats.onlineCameras,
    suffix: `/ ${stats.totalCameras} 路`,
    icon: VideoCamera,
    accent: '#22c993',
  },
])

const baseGrid = { left: 48, right: 24, top: 50, bottom: 40 }

const trendOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  legend: {
    data: trend.series.map((s) => s.name),
    top: 8,
    textStyle: { color: chartTextColor.value },
  },
  grid: baseGrid,
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: trend.dates,
    axisLine: { lineStyle: { color: chartLineColor.value } },
    axisLabel: { color: chartTextColor.value },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: chartLineColor.value } },
    axisLabel: { color: chartTextColor.value },
  },
  series: trend.series.map((s, i) => ({
    name: s.name,
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 7,
    data: s.data,
    lineStyle: { width: 3 },
    areaStyle: { opacity: i === 0 ? 0.18 : 0.08 },
    itemStyle: { color: i === 0 ? '#2f7dff' : '#22d3ee' },
  })),
}))

const palette = ['#2f7dff', '#22d3ee', '#faad14', '#ff6b3d', '#52c41a', '#a78bfa', '#ff4d4f']

const categoryOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'item', formatter: '{b}<br/>{c} ({d}%)' },
  legend: {
    type: 'scroll',
    orient: 'horizontal',
    bottom: 0,
    textStyle: { color: chartTextColor.value, fontSize: 11 },
  },
  series: [
    {
      type: 'pie',
      radius: ['42%', '66%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: chartBorderColor.value, borderWidth: 2, borderRadius: 4 },
      label: { color: chartLabelColor.value, fontSize: 11 },
      data: categoryData.value.map((d, i) => ({
        ...d,
        itemStyle: { color: palette[i % palette.length] },
      })),
    },
  ],
}))

const statusColorMap = {
  待初审: '#faad14',
  未处理: '#8c9bb5',
  初审通过: '#52c41a',
  初审未通过: '#ff4d4f',
}

const statusOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 70, right: 24, top: 20, bottom: 30 },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: chartLineColor.value } },
    axisLabel: { color: chartTextColor.value },
  },
  yAxis: {
    type: 'category',
    data: statusData.value.map((d) => d.name),
    axisLine: { lineStyle: { color: chartLineColor.value } },
    axisLabel: { color: chartLabelColor.value },
  },
  series: [
    {
      type: 'bar',
      barWidth: 18,
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: (p) => statusColorMap[p.name] || '#2f7dff',
      },
      data: statusData.value.map((d) => d.value),
      label: { show: true, position: 'right', color: chartLabelColor.value },
    },
  ],
}))

function goDetail(row) {
  if (row?.id) router.push(`/records/${row.id}`)
}

async function loadAll() {
  loading.value = true
  try {
    const [s, t, cat, st, alarms] = await Promise.all([
      getStats(),
      getTrend(),
      getCategoryDistribution(),
      getStatusDistribution(),
      getRecentAlarms(),
    ])
    Object.assign(stats, s)
    trend.dates = t.dates || []
    trend.series = t.series || []
    categoryData.value = cat || []
    statusData.value = st || []
    recentAlarms.value = alarms || []
  } catch {
    // 拦截器已提示
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.stat-row {
  margin-bottom: 16px;
}
.stat-row .el-col {
  margin-bottom: 16px;
}
.chart-row {
  margin-bottom: 0;
}
.chart-row .el-col {
  margin-bottom: 16px;
}
.chart-panel {
  padding: 16px 18px 18px;
  height: 100%;
}
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.alarm-table {
  background: transparent;
  cursor: pointer;
}
.time-cell {
  color: var(--hg-text-2);
  font-size: 12px;
}
</style>
