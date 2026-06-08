import request from './request'

// 分页查询违章记录
export function getRecords(params) {
  return request.get('/api/records', { params })
}

// 详情
export function getRecordDetail(id) {
  return request.get(`/api/records/${id}`)
}

// 提交审核
export function reviewRecord(id, data) {
  return request.post(`/api/records/${id}/review`, data)
}

// 删除单条
export function deleteRecord(id) {
  return request.delete(`/api/records/${id}`)
}

// 批量删除
export function batchDeleteRecords(ids) {
  return request.post('/api/records/batch-delete', { ids })
}
