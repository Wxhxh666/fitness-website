<template>
  <div class="profile-page">
    <section class="page-hero">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">MY PROFILE</span>
        <h1 class="page-hero__title">个人中心</h1>
        <p class="page-hero__desc">查看和管理你的个人资料</p>
      </div>
    </section>

    <section class="section section-light">
      <div class="container">
        <div class="profile-card" v-if="!loading">
          <!-- Avatar -->
          <div class="profile-row">
            <div class="profile-label">头像</div>
            <div class="profile-value">
              <div class="avatar-circle" @click="triggerFileInput" style="cursor:pointer;position:relative;">
              <img v-if="uploadedPreview" :src="uploadedPreview" class="avatar-preview-img" />
              <span v-else>{{ avatarLetter }}</span>
              <div class="avatar-overlay">点击更换</div>
            </div>
            <input type="file" ref="fileInput" accept="image/*" style="display:none" @change="onFileSelected" />
              <div class="avatar-input-row">
                <span v-if="uploading" style="color:#999;font-size:13px;">上传中...</span>
                <button v-else class="btn-primary-sm" :disabled="!uploadedPreview" @click="submitAvatar">确定修改</button>
                <span v-if="pendingInfo.avatar" class="badge-pending">正在审核中</span>
              </div>
            </div>
          </div>
          <!-- Nickname -->
          <div class="profile-row">
            <div class="profile-label">昵称</div>
            <div class="profile-value">
              <div class="avatar-input-row">
                <input v-model="editNickname" placeholder="输入新昵称" class="profile-input" />
                <button class="btn-primary-sm" @click="submitField('nickname')">提交修改</button>
                <span v-if="pendingInfo.nickname" class="badge-pending">正在审核中</span>
              </div>
              <div class="current-value" v-if="user.nickname && !pendingInfo.nickname">当前：{{ user.nickname }}</div>
            </div>
          </div>
          <!-- Email -->
          <div class="profile-row">
            <div class="profile-label">邮箱</div>
            <div class="profile-value"><span>{{ user.email || '未设置' }}</span></div>
          </div>
          <!-- Phone -->
          <div class="profile-row">
            <div class="profile-label">手机号</div>
            <div class="profile-value"><span>{{ user.phone || '未设置' }}</span></div>
          </div>
          <!-- Avatar display -->
          <div v-if="user.avatar_url" class="profile-row">
            <div class="profile-label">头像链接</div>
            <div class="profile-value"><span class="avatar-url">{{ user.avatar_url }}</span></div>
          </div>
        </div>
        <div v-if="loading" style="text-align:center;padding:60px;color:#999;">加载中...</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { getProfile, updateProfile, setUser, getUser } from "@/api"
import axios from "axios"
import { ElMessage } from "element-plus"

const user = ref<any>({})
const loading = ref(true)
const editNickname = ref("")
const editAvatar = ref("")
const pendingInfo = ref<any>({})

const avatarLetter = computed(() => {
  const n = user.value.nickname || user.value.email || "U"
  return n.charAt(0).toUpperCase()
})

const fileInput = ref<HTMLInputElement>()
const uploadedPreview = ref("")
const uploading = ref(false)

function triggerFileInput() {
  fileInput.value?.click()
}

async function onFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  
  // Validate size (2MB)
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error("图片大小不能超过 2MB")
    return
  }
  
  // Show preview
  uploadedPreview.value = URL.createObjectURL(file)
  
  // Upload
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append("file", file)
    const res = await axios.post("http://127.0.0.1:8000/api/upload", formData)
    const url = res.data.data?.url || res.data.url
    if (url) {
      editAvatar.value = url
    }
    ElMessage.success("上传成功，点击“确定修改”提交审核")
  } catch (e: any) {
    ElMessage.error(e?.message || "上传失败")
    uploadedPreview.value = ""
  } finally {
    uploading.value = false
  }
}

async function submitAvatar() {
  if (!editAvatar.value) { ElMessage.warning("请先上传图片"); return }
  try {
    await updateProfile("avatar", editAvatar.value)
    ElMessage.success("申请已提交，等待审核")
    editAvatar.value = ""
    uploadedPreview.value = ""
    const res = await getProfile()
    pendingInfo.value = res.data.pending_changes || {}
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  }
}

onMounted(async () => {
  try {
    const res = await getProfile()
    user.value = res.data
    pendingInfo.value = res.data.pending_changes || {}
    // Sync localStorage so NavHeader shows latest avatar_url etc.
    const stored = getUser()
    if (stored) { Object.assign(stored, res.data); setUser(stored) }
  } catch { /* */ }
  finally { loading.value = false }
})

async function submitField(field: string) {
  const value = field === "nickname" ? editNickname.value.trim() : editAvatar.value.trim()
  if (!value) { ElMessage.warning("\u8bf7\u8f93\u5165\u503c"); return }
  try {
    await updateProfile(field, value)
    ElMessage.success("\u7533\u8bf7\u5df2\u63d0\u4ea4\uff0c\u7b49\u5f85\u5ba1\u6838")
    if (field === "nickname") editNickname.value = ""
    else editAvatar.value = ""
    const res = await getProfile()
    pendingInfo.value = res.data.pending_changes || {}
  } catch (e: any) {
    ElMessage.error(e?.message || "\u64cd\u4f5c\u5931\u8d25")
  }
}
</script>

<style scoped>
.page-hero { position:relative; padding:160px 0 80px; background:var(--clr-black); overflow:hidden; }
.page-hero__bg { position:absolute; inset:0; background:radial-gradient(ellipse at 30% 60%,rgba(201,169,110,0.05),transparent 50%); }
.page-hero__content { position:relative; z-index:1; }
.page-hero__label { font-size:11px; letter-spacing:4px; color:var(--clr-gold); margin-bottom:16px; display:inline-block; }
.page-hero__title { font-family:var(--font-display); font-size:48px; font-weight:400; color:var(--clr-cream); margin-bottom:16px; letter-spacing:2px; }
.page-hero__desc { font-size:15px; color:var(--clr-gray-light); max-width:500px; }
.profile-card { max-width:640px; margin:0 auto; background:#fff; border:1px solid rgba(0,0,0,0.05); padding:40px; }
.profile-row { display:flex; align-items:flex-start; padding:20px 0; border-bottom:1px solid rgba(0,0,0,0.04); gap:24px; }
.profile-row:last-child { border-bottom:none; }
.profile-label { width:100px; flex-shrink:0; font-size:14px; color:#666; letter-spacing:1px; padding-top:4px; }
.profile-value { flex:1; }
.profile-input { padding:8px 12px; border:1px solid #ddd; font-size:13px; width:240px; outline:none; }
.profile-input:focus { border-color:#c9a96e; }
.avatar-circle { width:64px; height:64px; border-radius:50%; background:linear-gradient(135deg,#c9a96e,#b8954a); display:flex; align-items:center; justify-content:center; font-size:24px; color:#fff; font-weight:500; margin-bottom:12px; }
.avatar-input-row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.btn-primary-sm { padding:8px 16px; background:#c9a96e; border:none; color:#fff; font-size:12px; letter-spacing:1px; cursor:pointer; transition:all .2s; }
.btn-primary-sm:hover { background:#b8954a; }
.badge-pending { font-size:11px; color:#c9a96e; letter-spacing:1px; padding:4px 8px; border:1px solid #c9a96e; }
.current-value { font-size:12px; color:#999; margin-top:4px; }
.avatar-url { font-size:12px; color:#999; word-break:break-all; }
@media (max-width:768px) { .page-hero__title { font-size:32px; } .profile-row { flex-direction:column; gap:8px; } .profile-input { width:100%; } }
.avatar-circle { position:relative; overflow:hidden; }
.avatar-preview-img { width:100%;height:100%;object-fit:cover; }
.avatar-overlay { position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.5);color:#fff;font-size:11px;text-align:center;padding:4px 0;letter-spacing:1px; }
</style>
