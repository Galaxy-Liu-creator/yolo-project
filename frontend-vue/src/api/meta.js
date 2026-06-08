import request from './request'

export function getCategories() {
  return request.get('/api/meta/categories')
}

export function getScenes() {
  return request.get('/api/meta/scenes')
}

export function getTeams() {
  return request.get('/api/meta/teams')
}

export function getVersions() {
  return request.get('/api/meta/versions')
}

export function getUnits() {
  return request.get('/api/meta/units')
}
