import request from './request'

// 更新个人资料
export function updateProfile(data) {
  return request.put('/api/auth/profile', data)
}

// 修改密码
export function updatePassword(data) {
  return request.put('/api/auth/password', data)
}
