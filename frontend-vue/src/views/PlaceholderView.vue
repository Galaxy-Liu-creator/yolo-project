<template>
  <div class="placeholder hg-panel">
    <div class="ph-icon">
      <el-icon :size="40"><Tools /></el-icon>
    </div>
    <h2 class="ph-title">{{ title }}</h2>
    <p class="ph-desc">该模块为系统规划功能，演示版本以「监控记录」与「首页看板」为核心展示。</p>
    <el-button type="primary" plain @click="$router.push('/records')">
      前往监控记录
    </el-button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Tools } from '@element-plus/icons-vue'

const route = useRoute()
const title = computed(() => route.meta?.title || '功能模块')
</script>

<style scoped>
.placeholder {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  text-align: center;
}
.ph-icon {
  width: 84px;
  height: 84px;
  display: grid;
  place-items: center;
  color: var(--hg-primary-2);
  background: rgba(34, 211, 238, 0.08);
  border: 1px solid var(--hg-border);
}
.ph-title {
  margin: 0;
  font-size: 20px;
  color: var(--hg-text);
  letter-spacing: 1px;
}
.ph-desc {
  margin: 0;
  max-width: 420px;
  color: var(--hg-text-2);
  font-size: 13px;
  line-height: 1.7;
}
</style>
