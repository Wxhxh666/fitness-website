<template>
  <div class="p-card fade-in">
    <h3 class="p-card__title"><el-icon><Setting /></el-icon>系统偏好设置</h3>

    <div class="pf-row">
      <div class="pf-label">默认 AI 模型</div>
      <div class="pf-value">
        <el-select v-model="form.ai_model" style="width: 260px">
          <el-option label="DeepSeek Flash（免费）" value="deepseek-flash" />
          <el-option label="Doubao Lite" value="doubao-lite" />
        </el-select>
        <p class="pf-tip">周复盘等 AI 功能使用此模型；Doubao 需在服务端配置方舟 API Key，未配置时自动回退 DeepSeek。</p>
      </div>
    </div>

    <div class="pf-row">
      <div class="pf-label">度量单位</div>
      <div class="pf-value">
        <el-radio-group v-model="form.unit_system">
          <el-radio-button value="metric">公制 cm/kg</el-radio-button>
          <el-radio-button value="imperial">英制 in/lb</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="pf-row">
      <div class="pf-label">通知提醒</div>
      <div class="pf-value">
        <el-switch v-model="form.notification_enabled" />
        <span class="pf-tip">开启后接收打卡与复盘提醒</span>
      </div>
    </div>

    <div class="pf-actions">
      <button class="btn-primary" :disabled="saving" @click="save">
        {{ saving ? '保存中…' : '保存偏好设置' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPreferences, updatePreferences } from '@/api'

const saving = ref(false)
const form = reactive({
  ai_model: 'deepseek-flash',
  unit_system: 'metric',
  notification_enabled: true,
})

async function loadPrefs() {
  try {
    const res = await getPreferences()
    Object.assign(form, res.data)
  } catch { /* 未登录等场景忽略 */ }
}

async function save() {
  saving.value = true
  try {
    const res = await updatePreferences({ ...form })
    Object.assign(form, res.data)
    ElMessage.success('偏好设置已保存')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadPrefs)
</script>

<style scoped>
.pf-row {
  display: flex;
  gap: 28px;
  padding: 22px 0;
  border-bottom: 1px solid rgba(184, 156, 102, 0.14);
}
.pf-label { width: 130px; flex-shrink: 0; font-size: 14px; color: var(--clr-gray); padding-top: 8px; letter-spacing: 1px; }
.pf-value { flex: 1; }
.pf-tip { margin-top: 8px; font-size: 12px; color: var(--clr-gray-light); line-height: 1.7; }
.pf-actions { margin-top: 24px; }
</style>
