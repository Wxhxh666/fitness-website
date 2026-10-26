<template>
  <div class="p-card coach-auth">
    <h3 class="coach-auth__title">教练认证</h3>
    <p class="coach-auth__desc">成为 FITLUXE 认证教练后，将解锁教练工作台。提交身份证与教练资质凭证，由管理员人工审核。</p>

    <!-- ============ 已是教练 ============ -->
    <el-result v-if="isCoach" icon="success" title="你已是认证教练"
      sub-title="前往教练工作台管理个人资料与学员服务">
      <template #extra>
        <el-button type="primary" @click="$router.push('/coach/dashboard')">进入教练工作台</el-button>
      </template>
    </el-result>

    <!-- ============ 审核中 / 已通过 / 已驳回 ============ -->
    <template v-else-if="application">
      <el-alert v-if="application.status === 'pending'" type="warning" :closable="false" show-icon
        title="申请正在审核中" description="管理员通常会在 1-3 个工作日内完成审核，请耐心等待。" />
      <el-alert v-else-if="application.status === 'approved'" type="success" :closable="false" show-icon
        title="认证已通过" description="刷新页面后即可看到教练身份生效。" />
      <el-alert v-else type="error" :closable="false" show-icon
        :title="'申请被驳回' + (application.reject_reason ? '：' + application.reject_reason : '')"
        description="你可以修改资料后重新提交申请。" />

      <el-descriptions :column="2" border style="margin-top:16px;">
        <el-descriptions-item label="真实姓名">{{ application.real_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ application.phone }}</el-descriptions-item>
        <el-descriptions-item label="资质类型">{{ certLabel(application.cert_type) }}</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ fmtTime(application.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="个人简介" :span="2">{{ application.bio || "-" }}</el-descriptions-item>
        <el-descriptions-item label="专长标签" :span="2">{{ application.specialties || "-" }}</el-descriptions-item>
      </el-descriptions>

      <el-button v-if="application.status === 'rejected'" type="primary" style="margin-top:16px;"
        @click="startForm">重新提交申请</el-button>
    </template>

    <!-- ============ 申请表单 ============ -->
    <template v-else>
      <el-alert type="info" :closable="false" show-icon style="margin-bottom:16px;"
        title="证件信息仅用于资质审核"
        description="证件照片加密存储，只有审核管理员可以查看，审核通过后不会公开展示；可随时联系我们删除。" />

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="real_name">
              <el-input v-model="form.real_name" placeholder="需与身份证一致" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="方便审核有问题时联系你" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="资质类型" prop="cert_type">
              <el-select v-model="form.cert_type" placeholder="选择你的教练资质" style="width:100%">
                <el-option label="国家职业资格（国职）" value="national" />
                <el-option label="ACE 认证" value="ace" />
                <el-option label="NSCA-CPT 认证" value="nssa" />
                <el-option label="其他资质" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专长标签" prop="specialties">
              <el-input v-model="form.specialties" placeholder="如：增肌,减脂,体态矫正" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="个人简介">
          <el-input v-model="form.bio" type="textarea" :rows="3" maxlength="500" show-word-limit
            placeholder="介绍你的执教经历与风格（选填）" />
        </el-form-item>

        <el-form-item label="身份证人像面" required>
          <div class="cred-upload">
            <input ref="frontInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="e => onFile(e, 'id_card_front')" />
            <div v-if="previews.id_card_front" class="cred-upload__thumb">
              <img :src="previews.id_card_front" alt="身份证人像面" />
              <el-button text size="small" @click="frontInput?.click()">重新选择</el-button>
            </div>
            <el-button v-else @click="frontInput?.click()"><el-icon><Plus /></el-icon> 上传人像面</el-button>
          </div>
        </el-form-item>
        <el-form-item label="身份证国徽面" required>
          <div class="cred-upload">
            <input ref="backInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="e => onFile(e, 'id_card_back')" />
            <div v-if="previews.id_card_back" class="cred-upload__thumb">
              <img :src="previews.id_card_back" alt="身份证国徽面" />
              <el-button text size="small" @click="backInput?.click()">重新选择</el-button>
            </div>
            <el-button v-else @click="backInput?.click()"><el-icon><Plus /></el-icon> 上传国徽面</el-button>
          </div>
        </el-form-item>
        <el-form-item label="教练资质凭证" required>
          <div class="cred-upload">
            <input ref="certInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="e => onFile(e, 'cert_file')" />
            <div v-if="previews.cert_file" class="cred-upload__thumb">
              <img :src="previews.cert_file" alt="资质凭证" />
              <el-button text size="small" @click="certInput?.click()">重新选择</el-button>
            </div>
            <el-button v-else @click="certInput?.click()"><el-icon><Plus /></el-icon> 上传证书照片</el-button>
            <span class="cred-upload__hint">证书内页需清晰可见编号与姓名，jpg/png/webp，≤ 8MB</span>
          </div>
        </el-form-item>
      </el-form>

      <el-button type="primary" :loading="submitting" @click="submit">提交认证申请</el-button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { applyCoach, getMyApplication } from '@/api/coach'

const isCoach = ref(false)
const application = ref<any>(null)
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  real_name: '',
  phone: '',
  cert_type: '',
  bio: '',
  specialties: '',
  id_card_front: null as File | null,
  id_card_back: null as File | null,
  cert_file: null as File | null,
})
const previews = reactive<Record<string, string>>({})
const frontInput = ref<HTMLInputElement>()
const backInput = ref<HTMLInputElement>()
const certInput = ref<HTMLInputElement>()

const rules: FormRules = {
  real_name: [{ required: true, message: '请填写真实姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请填写联系电话', trigger: 'blur' }],
  cert_type: [{ required: true, message: '请选择资质类型', trigger: 'change' }],
}

const CERT_LABELS: Record<string, string> = {
  national: '国家职业资格（国职）', ace: 'ACE', nssa: 'NSCA-CPT', other: '其他',
}
function certLabel(k: string) { return CERT_LABELS[k] || k }
function fmtTime(s?: string) { return s ? s.slice(0, 16).replace('T', ' ') : '-' }

onMounted(load)

async function load() {
  try {
    const res = await getMyApplication()
    isCoach.value = res.data.is_coach
    application.value = res.data.application
    if (res.data.is_coach) application.value = application.value || null
  } catch { /* 未登录等场景由守卫拦截 */ }
}

function startForm() {
  application.value = null
}

function onFile(e: Event, field: 'id_card_front' | 'id_card_back' | 'cert_file') {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 8 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 8MB')
    input.value = ''
    return
  }
  form[field] = file
  previews[field] = URL.createObjectURL(file)
  input.value = ''
}

async function submit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!form.id_card_front || !form.id_card_back || !form.cert_file) {
    ElMessage.error('请上传身份证正反面与资质凭证')
    return
  }
  submitting.value = true
  try {
    const res = await applyCoach({ ...form } as any)
    ElMessage.success(res.msg || '申请已提交')
    application.value = res.data
    Object.keys(previews).forEach(k => delete previews[k])
  } catch (e: any) {
    ElMessage.error(e?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.coach-auth { padding: 24px 28px; }
.coach-auth__title { font-size: 17px; font-weight: 500; color: #1a1a1a; margin-bottom: 8px; }
.coach-auth__desc { font-size: 13px; color: #999; margin-bottom: 20px; line-height: 1.7; }
.cred-upload { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.cred-upload__thumb { display: flex; align-items: center; gap: 8px; }
.cred-upload__thumb img {
  width: 120px; height: 76px; object-fit: cover; border-radius: 6px; border: 1px solid #e5e5e5;
}
.cred-upload__hint { font-size: 12px; color: #bbb; }
</style>
