import request from './request'

// 登录
export function login(data) {
  return request.post('/api/auth/login', data)
}

// 当前用户
export function getProfile() {
  return request.get('/api/auth/me')
}

// 登出
export function logout() {
  return request.post('/api/auth/logout')
}
