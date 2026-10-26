<template>
  <div class="coach-profile p-card">
    <h3>我的教练资料</h3>
    <p class="coach-profile__desc">这些资料将展示在教练主页（M2 后续版本上线公开页）。</p>

    <el-form v-if="!loading" :model="form" label-position="top" style="max-width:560px;">
      <el-form-item label="展示名" required>
        <el-input v-model="form.display_name" maxlength="64" placeholder="学员看到的教练名字" />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="执教年限">
            <el-input-number v-model="form.years" :min="0" :max="60" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="头像">
            <div class="avatar-upload">
              <img v-if="form.avatar_url" :src="fullUrl(form.avatar_url)" class="avatar-upload__img" alt="头像" />
              <input ref="avatarInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="onAvatar" />
              <el-button size="small" @click="avatarInput?.click()">{{ form.avatar_url ? "更换" : "上传" }}</el-button>
            </div>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="专长标签">
        <el-input v-model="form.specialties" maxlength="256" placeholder="逗号分隔，如：增肌,减脂,体态矫正" />
      </el-form-item>
      <el-form-item label="个人简介">
        <el-input v-model="form.bio" type="textarea" :rows="4" maxlength="500" show-word-limit />
      </el-form-item>
      <el-button type="primary" :loading="saving" @click="save">保存修改</el-button>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
import axios from "axios"
import { getCoachProfile, updateCoachProfile } from "@/api/coach"
import { getToken, API_BASE_URL } from "@/api"

const loading = ref(true)
const saving = ref(false)
const avatarInput = ref<HTMLInputElement>()
const form = reactive({
  display_name: "",
  years: 0,
  bio: "",
  specialties: "",
  avatar_url: "",
})

const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, "")
function fullUrl(path: string) {
  if (!path) return ""
  if (path.startsWith("http")) return path
  return API_ORIGIN + path
}

onMounted(load)

async function load() {
  try {
    const res = await getCoachProfile()
    const d = res.data
    if (d) {
      form.display_name = d.display_name || ""
      form.years = d.years ?? 0
      form.bio = d.bio || ""
      form.specialties = d.specialties || ""
      form.avatar_url = d.avatar_url || ""
    }
  } catch (e: any) {
    ElMessage.error(e?.message || "加载失败")
  } finally {
    loading.value = false
  }
}

async function onAvatar(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error("头像大小不能超过 2MB")
    input.value = ""
    return
  }
  const fd = new FormData()
  fd.append("file", file)
  try {
    const token = getToken()
    const res = await axios.post(API_BASE_URL + "/upload", fd, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: token ? "Bearer " + token : "",
      },
    })
    const url = res.data.data?.url || res.data.url
    if (url) {
      form.avatar_url = url
      ElMessage.success("头像已上传，保存资料后生效")
    }
  } catch (e: any) {
    ElMessage.error(e?.message || "上传失败")
  } finally {
    input.value = ""
  }
}

async function save() {
  if (!form.display_name.trim()) {
    ElMessage.error("展示名不能为空")
    return
  }
  saving.value = true
  try {
    await updateCoachProfile({ ...form })
    ElMessage.success("资料已更新")
  } catch (e: any) {
    ElMessage.error(e?.message || "保存失败")
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.coach-profile { padding: 24px 28px; }
.coach-profile h3 { font-size: 17px; font-weight: 500; color: #1a1a1a; margin-bottom: 6px; }
.coach-profile__desc { font-size: 13px; color: #999; margin-bottom: 20px; }
.avatar-upload { display: flex; align-items: center; gap: 10px; }
.avatar-upload__img { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; border: 1px solid #e5e5e5; }
</style>
