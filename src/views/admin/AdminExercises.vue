<template>
  <div class="admin-page">
    <div class="admin-page__toolbar">
      <span class="admin-page__count">共 {{ total }} 个动作</span>
      <div style="flex:1"></div>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon> 新增动作
      </el-button>
    </div>
    <el-table :data="exercises" stripe style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="动作名称" width="140" />
      <el-table-column prop="category_label" label="部位" width="70" />
      <el-table-column prop="difficulty_label" label="难度" width="70" />
      <el-table-column prop="duration" label="建议组数" width="130" />
      <el-table-column label="封面图" width="100" align="center">
        <template #default="{ row }">
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
            <img v-if="row.cover_url" :src="fullUrl(row.cover_url)" style="width:50px;height:50px;object-fit:cover;border-radius:4px;border:1px solid #eee;" />
            <span v-else style="color:#ccc;font-size:11px;">无</span>
            <el-button size="small" text @click="uploadCover(row)">上传</el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="250">
        <template #default="{ row }">{{ row.desc || row.description }}</template>
      </el-table-column>
      <el-table-column label="视频" width="100" align="center">
        <template #default="{ row }">
          <el-button v-if="row.video_url" size="small" text type="primary" @click="previewVideo(row)">查看</el-button>
          <el-button size="small" text @click="uploadVideo(row)">上传</el-button>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small" style="margin-right:4px;">{{ row.is_active ? "上架" : "下架" }}</el-tag>
          <el-button size="small" text :type="row.is_active ? 'warning' : 'success'"
            @click="toggleStatus(row)" :loading="togglingId === row.id">
            {{ row.is_active ? "下架" : "上架" }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add Exercise Dialog -->
    <el-dialog v-model="showAddDialog" title="新增动作" width="560px" :close-on-click-modal="false">
      <el-form :model="form" label-position="top" ref="formRef" :rules="formRules">
        <el-form-item label="动作名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入动作名称" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部位分类" prop="category">
              <el-select v-model="form.category" placeholder="选择部位" style="width:100%">
                <el-option v-for="c in categories" :key="c.key" :label="c.label" :value="c.key" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度等级" prop="difficulty">
              <el-select v-model="form.difficulty" placeholder="选择难度" style="width:100%">
                <el-option label="入门" value="beginner" />
                <el-option label="中级" value="intermediate" />
                <el-option label="高级" value="advanced" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="建议组数" prop="duration">
          <el-input v-model="form.duration" placeholder="例如: 12-15 次 x 4组" />
        </el-form-item>
        <el-form-item label="动作描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="简要描述该动作" />
        </el-form-item>
        <el-form-item label="封面图 URL" prop="cover_url">
          <el-input v-model="form.cover_url" placeholder="可选，填写图片地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitExercise" :loading="submitting">提交创建</el-button>
      </template>
    </el-dialog>

    <!-- Video Preview Dialog -->
    <el-dialog v-model="showVideoDialog" title="教学视频" width="700px" :close-on-click-modal="false">
      <video v-if="videoPreviewUrl" :src="videoPreviewUrl" controls style="width:100%;max-height:480px;background:#000;" />
      <p v-else style="color:#999;text-align:center;padding:40px;">暂无视频</p>
    </el-dialog>

    <!-- Hidden file input for video upload -->
    <input type="file" ref="videoFileInput" accept="video/*" style="display:none" @change="onVideoFileSelected" />
    <!-- Hidden file input for cover image upload -->
    <input type="file" ref="coverFileInput" accept="image/*" style="display:none" @change="onCoverImageSelected" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { Plus } from "@element-plus/icons-vue"
import { getAdminExercises, getExerciseCategories, toggleExerciseStatus, createExercise, updateExercise } from "@/api"
import { ElMessage } from "element-plus"
import type { FormInstance } from "element-plus"
import axios from "axios"
import { getToken } from "@/api"

const exercises = ref<any[]>([])
const total = ref(0)
const loading = ref(true)
const togglingId = ref<number | null>(null)

const showAddDialog = ref(false)
const showVideoDialog = ref(false)
const videoPreviewUrl = ref("")
const videoUploadTarget = ref<any>(null)
const videoFileInput = ref<HTMLInputElement>()
const coverUploadTarget = ref<any>(null)
const coverFileInput = ref<HTMLInputElement>()
const submitting = ref(false)
const categories = ref<any[]>([])
const formRef = ref<FormInstance>()
const form = reactive({
  name: "",
  category: "",
  difficulty: "intermediate",
  duration: "",
  description: "",
  cover_url: "",
})
const formRules = {
  name: [{ required: true, message: "请输入动作名称", trigger: "blur" }],
  category: [{ required: true, message: "请选择部位分类", trigger: "change" }],
  difficulty: [{ required: true, message: "请选择难度等级", trigger: "change" }],
}

function fullUrl(path: string) {
  if (!path) return ""
  if (path.startsWith("http")) return path
  return "http://127.0.0.1:8000" + path
}

async function load() {
  loading.value = true
  try {
    const [exRes, catRes] = await Promise.all([
      getAdminExercises(),
      getExerciseCategories(),
    ])
    exercises.value = exRes.data.items
    total.value = exRes.data.total
    categories.value = catRes.data
  } catch { /* */ }
  finally { loading.value = false }
}

async function toggleStatus(row: any) {
  togglingId.value = row.id
  try {
    await toggleExerciseStatus(row.id)
    ElMessage.success(row.is_active ? "已下架" : "已上架")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  } finally {
    togglingId.value = null
  }
}

function uploadCover(row: any) {
  coverUploadTarget.value = row
  coverFileInput.value?.click()
}

function uploadVideo(row: any) {
  videoUploadTarget.value = row
  videoFileInput.value?.click()
}

async function onVideoFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !videoUploadTarget.value) return

  if (file.size > 200 * 1024 * 1024) {
    ElMessage.error("视频大小不能超过 200MB")
    return
  }

  const formData = new FormData()
  formData.append("file", file)
  formData.append("type", "video")

  try {
    const token = getToken()
    const res = await axios.post("http://127.0.0.1:8000/api/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        "Authorization": token ? "Bearer " + token : "",
      },
    })
    const url = res.data.data?.url || res.data.url
    if (url) {
      await updateExercise(videoUploadTarget.value.id, { video_url: url })
      ElMessage.success("视频上传成功")
      load()
    }
  } catch (e: any) {
    ElMessage.error(e?.message || "上传失败")
  } finally {
    videoUploadTarget.value = null
    target.value = ""
  }
}

async function onCoverImageSelected(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !coverUploadTarget.value) return

  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error("图片大小不能超过 2MB")
    return
  }

  const formData = new FormData()
  formData.append("file", file)

  try {
    const token = getToken()
    const res = await axios.post("http://127.0.0.1:8000/api/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        "Authorization": token ? "Bearer " + token : "",
      },
    })
    const url = res.data.data?.url || res.data.url
    if (url) {
      await updateExercise(coverUploadTarget.value.id, { cover_url: url })
      ElMessage.success("封面图上传成功")
      load()
    }
  } catch (e: any) {
    ElMessage.error(e?.message || "上传失败")
  } finally {
    coverUploadTarget.value = null
    target.value = ""
  }
}

function previewVideo(row: any) {
  videoPreviewUrl.value = row.video_url
  if (videoPreviewUrl.value && videoPreviewUrl.value.startsWith('/')) {
    videoPreviewUrl.value = 'http://127.0.0.1:8000' + videoPreviewUrl.value
  }
  showVideoDialog.value = true
}

async function submitExercise() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await createExercise({ ...form })
    ElMessage.success("动作创建成功")
    showAddDialog.value = false
    form.name = ""; form.category = ""; form.difficulty = "intermediate"
    form.duration = ""; form.description = ""; form.cover_url = ""
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "创建失败")
  } finally {
    submitting.value = false
  }
}

onMounted(() => load())
</script>

<style scoped>
.admin-page__toolbar { margin-bottom: 16px; display: flex; align-items: center; gap: 12px; }
.admin-page__count { font-size: 13px; color: #999; }
:deep(.el-table th) { background: #fafafa !important; color: #555; font-weight: 500; font-size: 13px; }
</style>



