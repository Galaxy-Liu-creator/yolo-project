import request from './request'

export function getStats() {
  return request.get('/api/dashboard/stats')
}

export function getTrend() {
  return request.get('/api/dashboard/trend')
}

export function getCategoryDistribution() {
  return request.get('/api/dashboard/category-distribution')
}

export function getStatusDistribution() {
  return request.get('/api/dashboard/status-distribution')
}

export function getRecentAlarms() {
  return request.get('/api/dashboard/recent-alarms')
}
