<template>
  <div class="cat-page">
    <!-- 顶部统计 -->
    <div class="stat-row">
      <div class="hg-panel stat-card">
        <div class="stat-num">{{ list.length }}</div>
        <div class="stat-label">违章类别总数</div>
      </div>
      <div class="hg-panel stat-card">
        <div class="stat-num green">{{ enabledCount }}</div>
        <div class="stat-label">已启用</div>
      </div>
      <div class="hg-panel stat-card">
        <div class="stat-num red">{{ highCount }}</div>
        <div class="stat-label">高危类别</div>
      </div>
      <div class="hg-panel stat-card">
        <div class="stat-num cyan">{{ totalTrigger }}</div>
        <div class="stat-label">累计触发次数</div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="hg-panel table-panel">
      <div class="table-head">
        <h3 class="hg-section-title">违章类别管理</h3>
        <span class="hint">开关可启用/停用对应识别类别</span>
      </div>

      <el-table :data="list" v-loading="loading" element-loading-background="rgba(11,18,32,0.6)">
        <el-table-column type="index" label="#" width="56" align="center" />
        <el-table-column prop="name" label="违章类别" min-width="190" />
        <el-table-column prop="code" label="类别编码" width="210">
          <template #default="{ row }">
            <span class="mono">{{ row.code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="违章等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="levelType(row.level)" effect="dark" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="relatedScene" label="关联场景" width="130" />
        <el-table-column label="累计触发" width="120" align="center">
          <template #default="{ row }">
            <span class="trigger-num">{{ row.count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="desc" label="描述" min-width="220" show-overflow-tooltip />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              :loading="row._saving"
              @change="(v) => onToggle(row, v)"
            />
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCategoryAdmin, updateCategory } from '@/api/violation'
import { violationLevelType } from '@/utils/constants'

const levelType = violationLevelType
const loading = ref(false)
const list = ref([])

const enabledCount = computed(() => list.value.filter((c) => c.enabled).length)
const highCount = computed(() => list.value.filter((c) => c.level === '高').length)
const totalTrigger = computed(() =>
  list.value.reduce((s, c) => s + (c.count || 0), 0)
)

async function load() {
  loading.value = true
  try {
    const data = await getCategoryAdmin()
    list.value = (data || []).map((c) => ({ ...c, _saving: false }))
  } catch {
    // 已提示
  } finally {
    loading.value = false
  }
}

async function onToggle(row, val) {
  row._saving = true
  try {
    await updateCategory(row.code, { enabled: val })
    ElMessage.success(`${row.name} 已${val ? '启用' : '停用'}`)
  } catch {
    row.enabled = !val // 回滚
  } finally {
    row._saving = false
  }
}

onMounted(load)
</script>

<style scoped>
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.stat-card {
  padding: 18px 20px;
}
.stat-num {
  font-size: 28px;
  font-weight: 800;
  font-family: var(--hg-mono);
  color: var(--hg-text);
}
.stat-num.green { color: var(--hg-success); }
.stat-num.red { color: var(--hg-danger); }
.stat-num.cyan { color: var(--hg-primary-2); }
.stat-label {
  margin-top: 4px;
  font-size: 13px;
  color: var(--hg-text-2);
}

.table-panel {
  padding: 16px 18px 18px;
}
.table-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 12px;
}
.hint {
  font-size: 12px;
  color: var(--hg-text-3);
}
.mono {
  font-family: var(--hg-mono);
  font-size: 12px;
  color: var(--hg-text-2);
}
.trigger-num {
  font-family: var(--hg-mono);
  font-weight: 700;
  color: var(--hg-primary-2);
}

@media (max-width: 900px) {
  .stat-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
