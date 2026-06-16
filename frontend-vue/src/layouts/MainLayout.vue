<template>
  <el-container class="layout">
    <!-- 侧边栏 -->
    <el-aside :width="collapsed ? '64px' : '232px'" class="sidebar">
      <div class="logo" :class="{ collapsed }">
        <div class="logo-mark">
          <img src="/logo-512.png" alt="吊装卫士" class="logo-img" />
        </div>
        <span v-show="!collapsed" class="logo-text">吊装卫士</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :collapse-transition="false"
        background-color="transparent"
        text-color="#a4b1c7"
        active-text-color="#ffffff"
        router
        class="side-menu"
      >
        <template v-for="item in menuItems" :key="item.path || item.group">
          <!-- 分组 -->
          <el-sub-menu v-if="item.children" :index="item.group">
            <template #title>
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </template>
            <el-menu-item
              v-for="child in item.children"
              :key="child.path"
              :index="child.path"
            >
              <el-icon><component :is="child.icon" /></el-icon>
              <template #title>{{ child.title }}</template>
            </el-menu-item>
          </el-sub-menu>
          <!-- 单项 -->
          <el-menu-item v-else :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>

      <div v-show="!collapsed" class="sidebar-foot">
        <div class="sys-status">
          <span class="dot online"></span> 系统在线
        </div>
      </div>
    </el-aside>

    <el-container>
      <!-- 顶栏 -->
      <el-header class="topbar">
        <div class="topbar-left">
          <el-icon class="collapse-btn" @click="collapsed = !collapsed">
            <Fold v-if="!collapsed" />
            <Expand v-else />
          </el-icon>
          <h1 class="sys-title">{{ SYSTEM_NAME }}</h1>
        </div>

        <div class="topbar-right">
          <el-tooltip :content="isDark ? '切换日间模式' : '切换夜间模式'" placement="bottom">
            <el-icon class="theme-toggle-btn" @click="toggleTheme">
              <Sunny v-if="isDark" />
              <Moon v-else />
            </el-icon>
          </el-tooltip>
          <el-dropdown trigger="click" @command="onCommand">
            <span class="user-chip">
              <el-avatar :size="30" class="user-avatar" :src="userStore.avatarImage || undefined">
                {{ avatarChar }}
              </el-avatar>
              <span class="user-name">{{ userStore.displayName }}</span>
              <el-tag size="small" effect="plain" class="role-tag">
                {{ roleText }}
              </el-tag>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile" :icon="Setting">
                  个人设置
                </el-dropdown-item>
                <el-dropdown-item command="account" :icon="UserFilled" disabled>
                  {{ userStore.user?.username }}
                </el-dropdown-item>
                <el-dropdown-item command="logout" :icon="SwitchButton" divided>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        <footer class="page-foot">{{ COPYRIGHT }}</footer>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Aim,
  Fold,
  Expand,
  ArrowDown,
  UserFilled,
  SwitchButton,
  Odometer,
  VideoCamera,
  Warning,
  List,
  Checked,
  Crop,
  Setting,
  Sunny,
  Moon,
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { logout as logoutApi } from '@/api/auth'
import { SYSTEM_NAME, COPYRIGHT } from '@/utils/constants'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const collapsed = ref(false)
const isDark = computed(() => themeStore.isDark)

function toggleTheme() {
  themeStore.toggle()
}

onMounted(() => {
  themeStore.init()
})

const menuItems = [
  { path: '/dashboard', title: '首页看板', icon: Odometer },
  {
    group: 'violation',
    title: '违章管理',
    icon: Warning,
    children: [
      { path: '/records', title: '监控记录', icon: VideoCamera },
      { path: '/categories', title: '违章类别', icon: List },
      { path: '/review', title: '审核记录', icon: Checked },
      { path: '/fence', title: '电子围栏', icon: Crop },
      { path: '/recognition-config', title: '识别项配置', icon: Setting },
    ],
  },
]

const activeMenu = computed(() => route.meta?.activeMenu || route.path)

const avatarChar = computed(() =>
  (userStore.displayName || 'U').slice(0, 1).toUpperCase()
)

const roleText = computed(() => {
  const map = { admin: '管理员', auditor: '审核员' }
  return map[userStore.role] || userStore.role || '用户'
})

async function onCommand(cmd) {
  if (cmd === 'profile') {
    router.push('/profile')
    return
  }
  if (cmd === 'logout') {
    try {
      await ElMessageBox.confirm('确认退出登录？', '提示', {
        type: 'warning',
        confirmButtonText: '退出',
        cancelButtonText: '取消',
      })
    } catch {
      return
    }
    try {
      await logoutApi()
    } catch {
      // 忽略后端登出错误，前端清 token 即可
    }
    userStore.clear()
    ElMessage.success('已退出登录')
    router.replace('/login')
  }
}
</script>

<style scoped>
.layout {
  height: 100vh;
}

/* 侧边栏 */
.sidebar {
  position: relative;
  background: var(--hg-sidebar-bg, linear-gradient(180deg, #0e1830 0%, #0a1324 100%));
  border-right: 1px solid var(--hg-border);
  transition: width 0.2s ease, background 0.2s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.logo.collapsed {
  justify-content: center;
  padding: 0;
}
.logo-mark {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  padding: 5px;
  background: linear-gradient(135deg, rgba(47, 125, 255, 0.18), rgba(34, 211, 238, 0.1));
  border: 1px solid rgba(90, 140, 210, 0.3);
  backdrop-filter: blur(6px);
  flex-shrink: 0;
  transition: all 0.3s ease;
}
.logo-mark:hover {
  background: linear-gradient(135deg, rgba(47, 125, 255, 0.28), rgba(34, 211, 238, 0.18));
  border-color: var(--hg-primary-2);
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.25);
}
.logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 6px rgba(34, 211, 238, 0.35));
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #eaf2ff;
}

.side-menu {
  border-right: none;
  padding: 10px 10px;
  flex: 1;
}
.side-menu :deep(.el-menu-item),
.side-menu :deep(.el-sub-menu__title) {
  border-radius: 0;
  height: 46px;
  border-left: 2px solid transparent;
}
.side-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(47, 125, 255, 0.22), rgba(34, 211, 238, 0.06));
  border-left: 2px solid var(--hg-primary-2);
  color: #fff;
}
.side-menu :deep(.el-menu-item:hover),
.side-menu :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.05);
}
.side-menu :deep(.el-sub-menu .el-menu-item) {
  min-width: 0;
  padding-left: 46px !important;
}

.sidebar-foot {
  padding: 14px 22px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.sys-status {
  font-size: 12px;
  color: var(--hg-text-2);
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.dot.online {
  background: var(--hg-success);
  box-shadow: 0 0 8px var(--hg-success);
}

/* 顶栏 */
.topbar {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px;
  background: var(--hg-topbar-bg, linear-gradient(90deg, #102038, #16243e));
  border-bottom: 1px solid var(--hg-border);
  transition: background 0.2s ease;
}
.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.collapse-btn {
  font-size: 20px;
  color: #a4b1c7;
  cursor: pointer;
}
.collapse-btn:hover {
  color: #fff;
}
.sys-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(90deg, #eaf2ff, #8fd3ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
}
.theme-toggle-btn {
  font-size: 20px;
  color: var(--hg-text-2);
  cursor: pointer;
  transition: color 0.15s;
}
.theme-toggle-btn:hover {
  color: #fff;
}
.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 2px;
  color: #e6edf7;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: background 0.15s;
}
.user-chip:hover {
  background: rgba(255, 255, 255, 0.14);
}
.user-avatar {
  background: linear-gradient(135deg, var(--hg-primary), var(--hg-primary-2));
  font-weight: 600;
}
.user-name {
  font-size: 14px;
  color: #e6edf7;
}
.role-tag {
  border-color: rgba(255, 255, 255, 0.2);
  color: #a4b1c7;
  background: transparent;
}

/* 内容 */
.main {
  background: var(--hg-bg);
  padding: 20px;
  overflow-y: auto;
}
.page-foot {
  margin-top: 24px;
  text-align: center;
  font-size: 12px;
  color: var(--hg-text-3);
}
</style>
