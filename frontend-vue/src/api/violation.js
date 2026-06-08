import request from './request'

// 违章类别管理
export function getCategoryAdmin() {
  return request.get('/api/violation/categories')
}
export function updateCategory(code, data) {
  return request.put(`/api/violation/categories/${code}`, data)
}

// 审核记录
export function getReviewLogs(params) {
  return request.get('/api/violation/review-logs', { params })
}

// 电子围栏
export function getFences() {
  return request.get('/api/violation/fences')
}

// 识别项配置
export function getRecognitionItems() {
  return request.get('/api/violation/recognition-items')
}
export function updateRecognitionItem(id, data) {
  return request.put(`/api/violation/recognition-items/${id}`, data)
}
