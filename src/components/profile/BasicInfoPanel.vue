<template>
  <div class="p-card fade-in">
    <h3 class="p-card__title"><el-icon><User /></el-icon>基础资料</h3>

    <!-- 头像 -->
    <div class="bi-row">
      <div class="bi-label">头像</div>
      <div class="bi-value">
        <div class="bi-avatar" @click="chooseFile">
          <img v-if="displayAvatar" :src="displayAvatar" class="bi-avatar__img" alt="头像" />
          <span v-else>{{ avatarLetter }}</span>
          <div class="bi-avatar__overlay">点击更换</div>
        </div>
        <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileSelected" />
        <div class="bi-inline">
          <span v-if="pendingInfo.avatar" class="bi-pending">头像修改审核中</span>
          <span v-if="uploading" class="bi-muted">上传中...</span>
        </div>
      </div>
    </div>

    <!-- 昵称 -->
    <div class="bi-row">
      <div class="bi-label">昵称</div>
      <div class="bi-value">
        <div class="bi-inline">
          <el-input v-model="nickname" placeholder="输入新昵称" style="width: 220px" />
          <button class="btn-primary" @click="submitNickname">提交修改</button>
          <span v-if="pendingInfo.nickname" class="bi-pending">审核中</span>
        </div>
        <div v-if="user.nickname" class="bi-current">当前：{{ user.nickname }}</div>
      </div>
    </div>

    <!-- 邮箱（只展示） -->
    <div class="bi-row">
      <div class="bi-label">邮箱</div>
      <div class="bi-value"><span>{{ user.email || '未设置' }}</span></div>
    </div>

    <!-- 手机号绑定 -->
    <div class="bi-row">
      <div class="bi-label">手机号</div>
      <div class="bi-value">
        <div class="bi-inline">
          <span v-if="user.phone">{{ user.phone }}</span>
          <span v-else class="bi-muted">未绑定</span>
          <el-input v-model="phone" placeholder="11位手机号" style="width: 180px" />
          <button class="btn-primary" @click="submitPhone">绑定</button>
        </div>
      </div>
    </div>

    <!-- 修改登录密码 -->
    <div class="bi-row bi-row--last">
      <div class="bi-label">修改密码</div>
      <div class="bi-value">
        <div class="bi-pw-form">
          <el-input v-model="oldPassword" type="password" show-password placeholder="原密码" style="width: 200px" />
          <el-input v-model="newPassword" type="password" show-password placeholder="新密码（至少6位）" style="width: 200px" />
          <el-input v-model="confirmPassword" type="password" show-password placeholder="确认新密码" style="width: 200px" />
          <button class="btn-primary" @click="submitPassword">确认修改</button>
        </div>
      </div>
    </div>

    <!-- 头像裁切弹窗 -->
    <AvatarCropDialog v-model="cropVisible" :src="cropSrc" :fallback-file="selectedFile" @cropped="onCropped" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import AvatarCropDialog from './AvatarCropDialog.vue'
import { getProfile, updateProfile, bindPhone, changePassword, API_BASE_URL, getToken, getUser, setUser } from '@/api'

const user = ref<any>({})
const pendingInfo = ref<any>({})
const nickname = ref('')
const phone = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const fileInput = ref<HTMLInputElement | null>(null)
const cropVisible = ref(false)
const cropSrc = ref('')
const selectedFile = ref<File | null>(null)
const uploadedPreview = ref('')
const uploading = ref(false)

const avatarLetter = computed(() => {
  const n = user.value.nickname || user.value.email || 'U'
  return n.charAt(0).toUpperCase()
})

const displayAvatar = computed(() => uploadedPreview.value || fullUrl(user.value.avatar_url))

/** 将后端返回的 /static/... 相对路径补全为完整 URL */
function fullUrl(path?: string) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return API_BASE_URL.replace(/\/api$/, '') + path
}

async function loadProfile() {
  try {
    const res = await getProfile()
    user.value = res.data
    pendingInfo.value = res.data.pending_changes || {}
    // 同步到 localStorage，让导航栏等组件能拿到最新头像/昵称
    const stored = getUser()
    if (stored) {
      Object.assign(stored, res.data)
      setUser(stored)
    }
  } catch { /* 未登录等场景由父级处理 */ }
}

onMounted(loadProfile)

function chooseFile() {
  fileInput.value?.click()
}

function onFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }
  cropSrc.value = URL.createObjectURL(file)
  selectedFile.value = file
  cropVisible.value = true
  target.value = ''
}

/** 裁切完成后上传原图到 /api/upload，再走资料审核流提交头像 */
async function onCropped(blob: Blob) {
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', blob, 'avatar.png')
    const token = getToken()
    const res = await axios.post(API_BASE_URL + '/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data', Authorization: token ? 'Bearer ' + token : '' },
    })
    const url = res.data.data?.url || res.data.url
    if (!url) throw new Error('上传失败')
    uploadedPreview.value = fullUrl(url)
    await updateProfile('avatar', url)
    ElMessage.success('头像修改申请已提交，等待审核')
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

/** 昵称修改：沿用原有审核流 */
async function submitNickname() {
  const value = nickname.value.trim()
  if (!value) {
    ElMessage.warning('请输入新昵称')
    return
  }
  try {
    await updateProfile('nickname', value)
    ElMessage.success('昵称修改申请已提交，等待审核')
    nickname.value = ''
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

/** 手机号绑定：直接写入用户表 */
async function submitPhone() {
  const value = phone.value.trim()
  if (!/^\d{11}$/.test(value)) {
    ElMessage.warning('请输入11位手机号')
    return
  }
  try {
    const res = await bindPhone(value)
    ElMessage.success(res.msg || '绑定成功')
    phone.value = ''
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.message || '绑定失败')
  }
}

/** 修改登录密码 */
async function submitPassword() {
  if (newPassword.value.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  try {
    const res = await changePassword(oldPassword.value, newPassword.value)
    ElMessage.success(res.msg || '密码修改成功')
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (e: any) {
    ElMessage.error(e?.message || '修改失败')
  }
}
</script>

<style scoped>
.bi-row {
  display: flex;
  gap: 28px;
  padding: 22px 0;
  border-bottom: 1px solid rgba(12, 216, 160, 0.14);
}
.bi-row--last { border-bottom: none; }
.bi-label { width: 96px; flex-shrink: 0; font-size: 14px; color: var(--clr-gray); padding-top: 8px; letter-spacing: 1px; }
.bi-value { flex: 1; }
.bi-inline { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.bi-avatar {
  width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(135deg, #B6FF3C, #0CD8A0);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; color: #fff; font-weight: 500;
  position: relative; overflow: hidden; cursor: pointer;
  margin-bottom: 8px;
}
.bi-avatar__img { width: 100%; height: 100%; object-fit: cover; }
.bi-avatar__overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: rgba(0, 0, 0, 0.5); color: #fff;
  font-size: 11px; text-align: center; padding: 3px 0; letter-spacing: 1px;
}
.bi-pending {
  font-size: 12px; color: var(--clr-gold-dark);
  padding: 3px 10px; border: 1px solid rgba(12, 216, 160, 0.45); border-radius: 6px;
}
.bi-muted { font-size: 12px; color: var(--clr-gray-light); }
.bi-current { font-size: 12px; color: var(--clr-gray-light); margin-top: 6px; }
.bi-pw-form { display: flex; flex-direction: column; gap: 12px; max-width: 420px; }
</style>
