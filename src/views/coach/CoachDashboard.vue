<template>
  <div class="coach-dash">
    <div v-if="loading" style="text-align:center;padding:80px;color:#999;">加载中...</div>
    <template v-else>
      <div class="coach-dash__stats">
        <div v-for="s in stats" :key="s.key" class="stat-card">
          <div class="stat-card__icon" :style="{ background: s.bg }">
            <el-icon :size="24"><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">{{ s.value }}</span>
            <span class="stat-card__label">{{ s.label }}</span>
          </div>
        </div>
      </div>

      <div class="coach-dash__panel">
        <h3>执教信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="展示名">{{ profile?.display_name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="资质类型">{{ certLabel(profile?.cert_type) }}</el-descriptions-item>
          <el-descriptions-item label="执教年限">{{ profile?.years ?? 0 }} 年</el-descriptions-item>
          <el-descriptions-item label="执业状态">{{ profile?.status === 'paused' ? '已暂停' : '在岗' }}</el-descriptions-item>
          <el-descriptions-item label="专长标签" :span="2">{{ profile?.specialties || "-" }}</el-descriptions-item>
          <el-descriptions-item label="个人简介" :span="2">{{ profile?.bio || "-" }}</el-descriptions-item>
        </el-descriptions>
        <el-button type="primary" style="margin-top:16px;" @click="$router.push('/coach/profile')">
          编辑教练资料
        </el-button>
      </div>

      <el-alert type="info" :closable="false" show-icon style="margin-top:20px;"
        title="学员管理与教练计划发布即将上线"
        description="用户选择教练、学员训练数据查看、教练发布训练计划（管理员审核后上架）已在开发计划中，敬请期待。" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { getCoachDashboard } from "@/api/coach"
import { Medal, Timer, User, Notebook } from "@element-plus/icons-vue"

const loading = ref(true)
const profile = ref<any>(null)
const certifiedDays = ref<number | null>(null)

const CERT_LABELS: Record<string, string> = {
  national: "国家职业资格（国职）", ace: "ACE", nssa: "NSCA-CPT", other: "其他",
}
function certLabel(k?: string) { return k ? (CERT_LABELS[k] || k) : "-" }

const stats = computed(() => [
  { key: "days", icon: Medal, label: "认证天数", value: certifiedDays.value ?? "-", bg: "rgba(12,216,160,0.12)" },
  { key: "years", icon: Timer, label: "执教年限", value: (profile.value?.years ?? 0) + " 年", bg: "rgba(52,152,219,0.1)" },
  { key: "students", icon: User, label: "学员数", value: "即将上线", bg: "rgba(201,169,110,0.14)" },
  { key: "plans", icon: Notebook, label: "我的计划", value: "即将上线", bg: "rgba(155,89,182,0.1)" },
])

onMounted(async () => {
  try {
    const res = await getCoachDashboard()
    profile.value = res.data?.profile
    certifiedDays.value = res.data?.certified_days
  } catch { /* */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.coach-dash__stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.stat-card {
  display: flex; align-items: center; gap: 16px;
  padding: 24px; background: #fff; border: 1px solid #eee;
}
.stat-card__icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-card__info { display: flex; flex-direction: column; gap: 2px; }
.stat-card__value { font-size: 24px; font-weight: 500; color: #222; font-family: "Playfair Display", serif; }
.stat-card__label { font-size: 12px; color: #999; letter-spacing: 0.5px; }
.coach-dash__panel { margin-top: 24px; padding: 24px; background: #fff; border: 1px solid #eee; }
.coach-dash__panel h3 { font-size: 15px; font-weight: 500; color: #333; margin-bottom: 14px; }
</style>
