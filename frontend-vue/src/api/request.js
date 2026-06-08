import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 统一响应包裹：{ code, message, data }
const service = axios.create({
  baseURL: '/', // 走 vite 代理；接口路径自带 /api 前缀
  timeout: 15000,
})

// 请求拦截：附加 Bearer token
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截：解包统一结构
service.interceptors.response.use(
  (response) => {
    const res = response.data

    // 非统一结构（极少数情况，如直接返回文件）原样返回
    if (res == null || typeof res !== 'object' || !('code' in res)) {
      return res
    }

    if (res.code === 0) {
      return res.data
    }

    // 业务错误
    if (res.code === 1001) {
      handleUnauthorized()
      return Promise.reject(new Error(res.message || '未登录或登录已过期'))
    }

    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || 'Error'))
  },
  (error) => {
    const status = error?.response?.status
    const body = error?.response?.data

    if (status === 401 || body?.code === 1001) {
      handleUnauthorized()
      return Promise.reject(error)
    }

    const msg =
      body?.message ||
      error?.message ||
      `网络错误（${status || '无响应'}）`
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

let redirecting = false
function handleUnauthorized() {
  const userStore = useUserStore()
  userStore.clear()
  ElMessage.error('登录已过期，请重新登录')
  if (!redirecting) {
    redirecting = true
    const current = router.currentRoute.value
    router
      .replace({
        path: '/login',
        query: current.path !== '/login' ? { redirect: current.fullPath } : {},
      })
      .finally(() => {
        redirecting = false
      })
  }
}

export default service
