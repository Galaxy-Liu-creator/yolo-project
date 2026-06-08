import { defineStore } from 'pinia'

const TOKEN_KEY = 'hg_token'
const USER_KEY = 'hg_user'
const AVATAR_KEY = 'hg_avatar'

// 清除旧的 localStorage 残留，确保重启后不会复用旧会话
localStorage.removeItem(TOKEN_KEY)
localStorage.removeItem(USER_KEY)

function loadUser() {
  try {
    const raw = sessionStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: sessionStorage.getItem(TOKEN_KEY) || '',
    user: loadUser(),
    // 头像图片（base64），持久化在 localStorage，与会话无关
    avatarImage: localStorage.getItem(AVATAR_KEY) || '',
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    displayName: (state) =>
      state.user?.displayName || state.user?.username || '用户',
    role: (state) => state.user?.role || '',
  },

  actions: {
    setToken(token) {
      this.token = token || ''
      if (token) sessionStorage.setItem(TOKEN_KEY, token)
      else sessionStorage.removeItem(TOKEN_KEY)
    },
    setUser(user) {
      this.user = user || null
      if (user) sessionStorage.setItem(USER_KEY, JSON.stringify(user))
      else sessionStorage.removeItem(USER_KEY)
    },
    setSession({ token, user }) {
      this.setToken(token)
      this.setUser(user)
    },
    setAvatarImage(dataUrl) {
      this.avatarImage = dataUrl || ''
      if (dataUrl) localStorage.setItem(AVATAR_KEY, dataUrl)
      else localStorage.removeItem(AVATAR_KEY)
    },
    clear() {
      this.setToken('')
      this.setUser(null)
    },
  },
})

