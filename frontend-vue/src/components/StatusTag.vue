<template>
  <el-tag :type="info.type" effect="dark" size="small" round>
    {{ info.text }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'
import { processStatusInfo } from '@/utils/constants'

const props = defineProps({
  status: { type: String, default: '' },
  text: { type: String, default: '' },
})

const info = computed(() => {
  const base = processStatusInfo(props.status, props.text)
  return props.text ? { ...base, text: props.text } : base
})
</script>
