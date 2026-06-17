// 系统统一文案 / 常量
export const SYSTEM_NAME = '油田吊装作业安全视频智能分析系统'
export const SYSTEM_SHORT = '擎安智吊 · AegisLift'
export const COPYRIGHT = '© 2026 油田吊装作业安全视频智能分析系统 · V2025.01'

// 后端基础地址（用于拼接 /static 图片）。开发态走 vite 代理，留空即可走同源代理。
export const API_BASE = ''

// processStatus 字典：status -> { text, type(ElTag), color }
export const PROCESS_STATUS_MAP = {
  pending_review: { text: '待初审', type: 'warning' },
  unprocessed: { text: '未处理', type: 'info' },
  approved: { text: '初审通过', type: 'success' },
  rejected: { text: '初审未通过', type: 'danger' },
}

export function processStatusInfo(status, fallbackText) {
  return (
    PROCESS_STATUS_MAP[status] || {
      text: fallbackText || status || '未知',
      type: 'info',
    }
  )
}

// 违章等级 -> ElTag type
export const VIOLATION_LEVEL_MAP = {
  高: 'danger',
  中: 'warning',
  低: 'info',
}

export function violationLevelType(level) {
  return VIOLATION_LEVEL_MAP[level] || 'info'
}

// 审核结果按钮定义（详情页三按钮）
export const REVIEW_ACTIONS = [
  { result: 'correct', text: '识别正确', type: 'success' },
  { result: 'wrong', text: '识别错误', type: 'danger' },
  { result: 'experiment_correct', text: '实验正确', type: 'danger' },
]

// 拼接静态资源完整地址
export function resolveAssetUrl(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  return API_BASE + url
}
