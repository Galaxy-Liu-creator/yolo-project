<template>
  <div class="login-page">
    <!-- 实景背景图：油田工业吊装场景 -->
    <div class="bg-photo"></div>
    <!-- 从左到右渐变遮罩：左侧深色保证登录框可读性，右侧渐亮露出实景 -->
    <div class="bg-overlay"></div>
    <div class="bg-grid"></div>
    <div class="bg-vignette"></div>

    <!-- 顶部品牌条 -->
    <header class="brand-bar">
      <div class="brand-mark">
        <img src="/logo-512.png" alt="擎安智吊" class="brand-logo" />
      </div>
      <div class="brand-meta">
        <span class="brand-text">{{ SYSTEM_SHORT }}</span>
        <span class="brand-sub">AEGISLIFT · SAFETY VISION</span>
      </div>
    </header>

    <!-- 登录面板（直角工业风） -->
    <main class="login-panel">
      <div class="panel-stripe"></div>
      <div class="panel-body">
        <h1 class="login-title">{{ SYSTEM_NAME }}</h1>
        <p class="login-subtitle">请登录您的账户</p>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              autocomplete="username"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
              autocomplete="current-password"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <div class="panel-foot">{{ COPYRIGHT }}</div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, Lock, Cpu } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login as loginApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { SYSTEM_NAME, SYSTEM_SHORT, COPYRIGHT } from '@/utils/constants'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const data = await loginApi({
      username: form.username,
      password: form.password,
    })
    userStore.setSession({ token: data.token, user: data.user })
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/dashboard'
    router.replace(redirect)
  } catch {
    // 错误信息已由拦截器统一提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ---- 背景实景图 ---- */
.bg-photo {
  position: absolute;
  inset: 0;
  background-image: url('/login-bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* ---- 从左到右渐变：左侧浓重遮罩 → 右侧透明露出实景 ---- */
.bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(4, 8, 18, 0.88) 0%,
    rgba(6, 12, 24, 0.72) 30%,
    rgba(8, 14, 26, 0.42) 56%,
    rgba(10, 15, 26, 0.12) 78%,
    rgba(12, 16, 28, 0.02) 100%
  );
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(90, 140, 210, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(90, 140, 210, 0.05) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: linear-gradient(90deg, rgba(0,0,0,0.6) 0%, transparent 55%);
}

.bg-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 100% at 25% 50%, transparent 45%, rgba(3, 6, 14, 0.38) 100%);
}

/* ---- 品牌条 ---- */
.brand-bar {
  position: absolute;
  top: 26px;
  left: 36px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 5;
}
.brand-mark {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  padding: 6px;
  background: linear-gradient(135deg, rgba(47, 125, 255, 0.15), rgba(34, 211, 238, 0.08));
  border: 1px solid rgba(90, 140, 210, 0.35);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}
.brand-mark:hover {
  background: linear-gradient(135deg, rgba(47, 125, 255, 0.25), rgba(34, 211, 238, 0.15));
  border-color: var(--hg-primary-2);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
}
.brand-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 8px rgba(34, 211, 238, 0.4));
}
.brand-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}
.brand-text {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #eaf2ff;
}
.brand-sub {
  font-size: 10px;
  letter-spacing: 3px;
  color: #6f86a8;
  font-family: var(--hg-mono);
}

/* ---- 登录面板（直角） ---- */
.login-panel {
  position: relative;
  z-index: 4;
  width: 408px;
  background: rgba(13, 22, 38, 0.88);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(90, 130, 200, 0.32);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.6);
}
.panel-stripe {
  height: 4px;
  background: linear-gradient(90deg, var(--hg-primary), var(--hg-primary-2) 60%, transparent);
}
.panel-body {
  padding: 38px 40px 22px;
}
.login-panel::before,
.login-panel::after {
  content: '';
  position: absolute;
  width: 14px;
  height: 14px;
  border-color: var(--hg-primary-2);
  border-style: solid;
}
.login-panel::before {
  top: 12px;
  left: 12px;
  border-width: 2px 0 0 2px;
}
.login-panel::after {
  bottom: 12px;
  right: 12px;
  border-width: 0 2px 2px 0;
}

.login-title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.4;
  text-align: center;
  color: #f1f6ff;
  letter-spacing: 1px;
}
.login-subtitle {
  margin: 0 0 28px;
  text-align: center;
  color: var(--hg-text-2);
  font-size: 13px;
  letter-spacing: 1px;
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  letter-spacing: 8px;
  font-weight: 600;
  border: none;
  border-radius: 0;
  background: linear-gradient(135deg, #2f7dff, #22d3ee);
  color: #061018;
}
.login-btn:hover {
  filter: brightness(1.1);
}

.panel-foot {
  padding: 12px 0;
  text-align: center;
  font-size: 11px;
  color: var(--hg-text-3);
  border-top: 1px solid rgba(90, 130, 200, 0.14);
}

/* 输入框始终与卡片融合，仅文字白色 */
:deep(.el-input__wrapper),
:deep(.el-input__wrapper:hover),
:deep(.el-input__wrapper.is-focus) {
  border-radius: 0;
  background: transparent !important;
  box-shadow: 0 0 0 1px rgba(90, 130, 200, 0.35) inset;
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--hg-primary-2) inset;
}
:deep(.el-input__inner) {
  color: #f1f6ff;
  background: transparent !important;
}
/* 浏览器自动填充时去除黄色/蓝色背景 */
:deep(.el-input__inner:-webkit-autofill),
:deep(.el-input__inner:-webkit-autofill:hover),
:deep(.el-input__inner:-webkit-autofill:focus) {
  -webkit-box-shadow: 0 0 0 1000px transparent inset !important;
  -webkit-text-fill-color: #f1f6ff !important;
  transition: background-color 9999s ease-in-out 0s;
}
:deep(.el-input__prefix .el-icon) {
  color: #6f86a8;
}
:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>

