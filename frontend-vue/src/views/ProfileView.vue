<template>
  <div class="profile">
    <div class="profile-head hg-panel">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <h2 class="head-title">个人设置</h2>
    </div>

    <el-row :gutter="16">
      <!-- 左：用户名片 -->
      <el-col :xs="24" :lg="8">
        <div class="hg-panel user-card">
          <div class="avatar-wrap">
            <div class="avatar-big" :style="avatarBgStyle">
              <img v-if="userStore.avatarImage" :src="userStore.avatarImage" class="avatar-img" alt="avatar" />
              <span v-else>{{ avatarChar }}</span>
            </div>
          </div>
          <div class="user-name">{{ form.displayName || userStore.displayName }}</div>
          <div class="user-account">@{{ userStore.user?.username }}</div>
          <el-tag effect="dark" :type="roleTagType" size="small" class="role-chip">
            {{ roleText }}
          </el-tag>

          <div class="meta-list">
            <div class="meta-row">
              <el-icon><Message /></el-icon>
              <span>{{ form.email || '未设置邮箱' }}</span>
            </div>
            <div class="meta-row">
              <el-icon><Iphone /></el-icon>
              <span>{{ form.phone || '未设置手机' }}</span>
            </div>
            <div class="meta-row">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ form.dept || '未设置部门' }}</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右：设置标签页 -->
      <el-col :xs="24" :lg="16">
        <div class="hg-panel setting-panel">
          <el-tabs v-model="activeTab" class="setting-tabs">
            <!-- 基本资料 -->
            <el-tab-pane label="基本资料" name="profile">
              <el-form
                :model="form"
                label-width="92px"
                class="setting-form"
                :rules="profileRules"
                ref="profileFormRef"
              >
                <el-form-item label="显示名称" prop="displayName">
                  <el-input v-model="form.displayName" maxlength="20" show-word-limit />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="form.email" placeholder="name@example.com" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="form.phone" maxlength="11" />
                </el-form-item>
                <el-form-item label="所属部门" prop="dept">
                  <el-input v-model="form.dept" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="savingProfile" @click="saveProfile">
                    保存资料
                  </el-button>
                  <el-button @click="resetProfile">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 修改密码 -->
            <el-tab-pane label="修改密码" name="password">
              <el-form
                :model="pwd"
                label-width="92px"
                class="setting-form"
                :rules="pwdRules"
                ref="pwdFormRef"
              >
                <el-form-item label="原密码" prop="oldPassword">
                  <el-input v-model="pwd.oldPassword" type="password" show-password />
                </el-form-item>
                <el-form-item label="新密码" prop="newPassword">
                  <el-input v-model="pwd.newPassword" type="password" show-password />
                </el-form-item>
                <el-form-item label="确认新密码" prop="confirmPassword">
                  <el-input v-model="pwd.confirmPassword" type="password" show-password />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="savingPwd" @click="savePassword">
                    修改密码
                  </el-button>
                  <el-button @click="resetPwd">清空</el-button>
                </el-form-item>
                <div class="pwd-tip">提示：演示账号 admin 初始密码 admin123，修改为内存生效，重启后端恢复。</div>
              </el-form>
            </el-tab-pane>

            <!-- 偏好设置 -->
            <el-tab-pane label="偏好设置" name="prefs">
              <div class="prefs">
                <div class="pref-block">
                  <h4 class="pref-title">头像图片</h4>
                  <div class="avatar-upload-row">
                    <!-- 预览 -->
                    <div class="avatar-preview" :style="avatarBgStyle">
                      <img v-if="userStore.avatarImage" :src="userStore.avatarImage" class="avatar-img" alt="avatar" />
                      <span v-else>{{ avatarChar }}</span>
                    </div>
                    <div class="avatar-upload-actions">
                      <el-button :icon="Upload" @click="triggerUpload">选择图片</el-button>
                      <el-button v-if="userStore.avatarImage" :icon="Delete" type="danger" plain @click="removeAvatar">移除头像</el-button>
                      <input
                        ref="fileInputRef"
                        type="file"
                        accept="image/*"
                        class="file-input-hidden"
                        @change="onFileChange"
                      />
                      <p class="upload-tip">支持 JPG / PNG / GIF，建议 200×200px 以上</p>
                    </div>
                  </div>
                </div>
                <div class="pref-block">
                  <h4 class="pref-title">界面偏好</h4>
                  <div class="pref-switch">
                    <span>侧边栏默认折叠</span>
                    <el-switch v-model="prefs.collapsed" @change="savePrefs" />
                  </div>
                </div>
                <el-button type="primary" plain @click="savePrefs">保存偏好</el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  Message,
  Iphone,
  OfficeBuilding,
  Upload,
  Delete,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateProfile, updatePassword } from '@/api/profile'

const router = useRouter()
const userStore = useUserStore()

const PREFS_KEY = 'hg_prefs'

const activeTab = ref('profile')
const savingProfile = ref(false)
const savingPwd = ref(false)
const profileFormRef = ref(null)
const pwdFormRef = ref(null)
const fileInputRef = ref(null)

const form = reactive({
  displayName: '',
  email: '',
  phone: '',
  dept: '',
})

const pwd = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const prefs = reactive({
  collapsed: false,
})

const profileRules = {
  displayName: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  email: [
    {
      pattern: /^[^@\s]+@[^@\s]+\.[^@\s]+$/,
      message: '邮箱格式不正确',
      trigger: 'blur',
    },
  ],
  phone: [
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
}

const pwdRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_r, v, cb) =>
        v === pwd.newPassword ? cb() : cb(new Error('两次密码不一致')),
      trigger: 'blur',
    },
  ],
}

const avatarChar = computed(() =>
  (form.displayName || userStore.displayName || 'U').slice(0, 1).toUpperCase()
)

// 没有上传图片时显示渐变背景色
const avatarBgStyle = computed(() =>
  userStore.avatarImage
    ? { background: '#1a2535' }
    : { background: 'linear-gradient(135deg, #2f7dff, #22d3ee)' }
)

const roleText = computed(() => {
  const map = { admin: '管理员', auditor: '审核员' }
  return map[userStore.role] || userStore.role || '用户'
})
const roleTagType = computed(() =>
  userStore.role === 'admin' ? 'danger' : 'warning'
)

function fillForm() {
  const u = userStore.user || {}
  form.displayName = u.displayName || ''
  form.email = u.email || ''
  form.phone = u.phone || ''
  form.dept = u.dept || ''
}

function resetProfile() {
  fillForm()
}

async function saveProfile() {
  if (!profileFormRef.value) return
  try {
    await profileFormRef.value.validate()
  } catch {
    return
  }
  savingProfile.value = true
  try {
    const data = await updateProfile({
      displayName: form.displayName,
      email: form.email,
      phone: form.phone,
      dept: form.dept,
    })
    userStore.setUser(data)
    ElMessage.success('资料已保存')
  } catch {
    // 拦截器已提示
  } finally {
    savingProfile.value = false
  }
}

function resetPwd() {
  pwd.oldPassword = ''
  pwd.newPassword = ''
  pwd.confirmPassword = ''
}

async function savePassword() {
  if (!pwdFormRef.value) return
  try {
    await pwdFormRef.value.validate()
  } catch {
    return
  }
  savingPwd.value = true
  try {
    await updatePassword({
      oldPassword: pwd.oldPassword,
      newPassword: pwd.newPassword,
    })
    ElMessage.success('密码修改成功')
    resetPwd()
  } catch {
    // 拦截器已提示
  } finally {
    savingPwd.value = false
  }
}

// ---- 头像上传 ----
function triggerUpload() {
  fileInputRef.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片不能超过 2MB')
    return
  }
  const reader = new FileReader()
  reader.onload = (ev) => {
    userStore.setAvatarImage(ev.target.result)
    ElMessage.success('头像已更新')
  }
  reader.readAsDataURL(file)
  // 清空 input，允许重复选同一文件
  e.target.value = ''
}

function removeAvatar() {
  userStore.setAvatarImage('')
  ElMessage.success('头像已移除')
}

// ---- 偏好 ----
function savePrefs() {
  localStorage.setItem(PREFS_KEY, JSON.stringify(prefs))
  ElMessage.success('偏好已保存')
}

function loadPrefs() {
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    if (raw) Object.assign(prefs, JSON.parse(raw))
  } catch {
    // ignore
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/dashboard')
}

onMounted(() => {
  fillForm()
  loadPrefs()
})
</script>

<style scoped>
.profile-head {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 18px;
  margin-bottom: 16px;
}
.head-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

/* 用户名片 */
.user-card {
  padding: 28px 22px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.avatar-wrap {
  position: relative;
}
.avatar-big {
  width: 88px;
  height: 88px;
  display: grid;
  place-items: center;
  font-size: 38px;
  font-weight: 700;
  color: #fff;
  clip-path: polygon(0 0, 100% 0, 100% 78%, 78% 100%, 0 100%);
  overflow: hidden;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.user-name {
  margin-top: 16px;
  font-size: 18px;
  font-weight: 700;
  color: var(--hg-text);
}
.user-account {
  margin-top: 4px;
  font-size: 13px;
  color: var(--hg-text-3);
  font-family: var(--hg-mono);
}
.role-chip {
  margin-top: 10px;
}
.meta-list {
  width: 100%;
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid var(--hg-border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--hg-text-2);
}
.meta-row .el-icon {
  color: var(--hg-primary-2);
}

/* 设置面板 */
.setting-panel {
  padding: 10px 22px 22px;
  min-height: 360px;
}
.setting-form {
  max-width: 460px;
  margin-top: 12px;
}
.pwd-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--hg-text-3);
}

.prefs {
  margin-top: 12px;
  max-width: 480px;
}
.pref-block {
  margin-bottom: 24px;
}
.pref-title {
  margin: 0 0 12px;
  font-size: 14px;
  color: var(--hg-text);
}

/* 头像上传 */
.avatar-upload-row {
  display: flex;
  align-items: center;
  gap: 22px;
}
.avatar-preview {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  clip-path: polygon(0 0, 100% 0, 100% 78%, 78% 100%, 0 100%);
  overflow: hidden;
}
.avatar-upload-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}
.file-input-hidden {
  display: none;
}
.upload-tip {
  margin: 0;
  font-size: 12px;
  color: var(--hg-text-3);
}

.pref-switch {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 260px;
  font-size: 14px;
  color: var(--hg-text-2);
}
</style>
