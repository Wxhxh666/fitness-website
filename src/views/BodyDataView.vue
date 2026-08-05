<template>
  <div class="bodydata-page">
    <!-- ============ 页面标题 ============ -->
    <section class="page-hero">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">BODY ANALYTICS</span>
        <h1 class="page-hero__title">身材数据管理</h1>
        <p class="page-hero__desc">用数据量化每一分努力，科学追踪身体变化，让进步清晰可见。</p>
      </div>
    </section>

    <!-- ============ 个人基础档案 ============ -->
    <ProfileStrip
      :profile="profile"
      :unit="unit"
      :activity-options="activityOptions"
      @save="saveProfile"
      @update:unit="unit = $event"
    />

    <!-- ============ 核心指标总览 ============ -->
    <MetricOverview :metrics="topMetrics" />

    <!-- ============ 指标计算与趋势 ============ -->
    <section class="analytics section section-light">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">METRICS &amp; TRENDS</p>
          <h2 class="section-title">指标计算与趋势</h2>
          <div class="gold-divider"></div>
          <p class="section-desc">左侧计算 BMI、体脂率、BMR、TDEE 等多维指标；右侧对照 BMI 参考标准，并查看历史身材数据趋势。</p>
        </div>
        <div class="analytics__grid">
          <BodyCalculator
            :profile="profile"
            :unit="unit"
            :activity-options="activityOptions"
            @calculated="onCalculated"
            @saved="loadRecords"
          />
          <TrendHistory :records="records" :unit="unit" @open-history="historyDialog.visible = true" />
        </div>
      </div>
    </section>

    <!-- ============ AI 智能饮食规划 ============ -->
    <section class="ai-diet section section-dark">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">AI DIET PLAN</p>
          <h2 class="section-title">AI 智能饮食规划</h2>
          <div class="gold-divider"></div>
          <p class="section-desc" style="color: var(--clr-gray)">结合身体指标、健身目标与饮食偏好生成科学饮食方案；配套每日打卡与每周复盘，并把数据同步到「计划制定」页，形成完整健身闭环。</p>
        </div>
        <DietPlanner :records="records" :results="results" :profile="profile" :activity-options="activityOptions" />
      </div>
    </section>

    <!-- ============ 数据管理入口 ============ -->
    <DataEntryCards
      :meas-latest-text="measLatestText"
      :goal="goal"
      :record-count="records.length"
      @open-measurements="measDialog.visible = true"
      @open-goals="goalDialog.visible = true"
      @open-history="historyDialog.visible = true"
    />

    <!-- ============ 对话框 ============ -->
    <MeasurementDialog v-model:visible="measDialog.visible" :records="records" :unit="unit" @saved="loadRecords" />
    <GoalManagerDialog
      v-model:visible="goalDialog.visible"
      :records="records"
      :goal="goal"
      :goal-saved-at="goalSavedAt"
      :unit="unit"
      @saved="onGoalSaved"
      @cleared="onGoalCleared"
    />
    <HistoryArchiveDialog v-model:visible="historyDialog.visible" :records="records" :unit="unit" @changed="loadRecords" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ProfileStrip from '@/components/bodydata/ProfileStrip.vue'
import MetricOverview from '@/components/bodydata/MetricOverview.vue'
import BodyCalculator from '@/components/bodydata/BodyCalculator.vue'
import TrendHistory from '@/components/bodydata/TrendHistory.vue'
import DietPlanner from '@/components/bodydata/DietPlanner.vue'
import DataEntryCards from '@/components/bodydata/DataEntryCards.vue'
import MeasurementDialog from '@/components/bodydata/MeasurementDialog.vue'
import GoalManagerDialog from '@/components/bodydata/GoalManagerDialog.vue'
import HistoryArchiveDialog from '@/components/bodydata/HistoryArchiveDialog.vue'
import {
  getBodyMetrics,
  getBodyRecords,
  getBodyProfile,
  saveBodyProfile,
  getBodyGoals,
} from '@/api'
import { fmtNum, dispValue, round1, weightUnitLabel } from '@/utils/units'
import type { Unit } from '@/utils/units'

const activityOptions = [
  { value: 'sedentary', label: '久坐少动' },
  { value: 'light', label: '轻度运动' },
  { value: 'moderate', label: '中度力量训练' },
  { value: 'intense', label: '高强度训练' },
]

// ---------- 共享状态 ----------
const unit = ref<Unit>('metric')
const profile = reactive({ gender: 'male', age: 25, activity_level: 'light' })
const records = ref<any[]>([])
const legacyMetrics = ref<any[]>([])
const results = ref<any>(null)
const goal = ref<any>(null)
const goalSavedAt = ref('')
const measDialog = reactive({ visible: false })
const goalDialog = reactive({ visible: false })
const historyDialog = reactive({ visible: false })

const weightUnit = computed(() => weightUnitLabel(unit.value))

// ---------- 记录工具 ----------
function latestWith(field: string) {
  for (const r of records.value) if (r[field] != null) return r
  return null
}

function prevWith(field: string) {
  let found = false
  for (const r of records.value) {
    if (r[field] == null) continue
    if (found) return r
    found = true
  }
  return null
}

function earliestWith(field: string) {
  const asc = [...records.value].sort((a, b) => (a.record_date < b.record_date ? -1 : 1))
  for (const r of asc) if (r[field] != null) return r
  return null
}

// ---------- 核心指标卡片 ----------
const topMetrics = computed(() => {
  const defs = [
    { key: 'weight_kg', label: '体重', icon: 'Scale', unit: weightUnit.value },
    { key: 'body_fat', label: '体脂率', icon: 'Histogram', unit: '%' },
    { key: 'muscle_mass', label: '肌肉量', icon: 'Aim', unit: weightUnit.value },
    { key: 'tdee', label: '每日消耗', icon: 'Lightning', unit: 'kcal' },
  ]
  return defs.map((d) => {
    const cur = latestWith(d.key)
    const prev = prevWith(d.key)
    let value: number | null = cur ? dispValue(unit.value, d.key, cur[d.key]) : null
    if (value === null) {
      const legacyKey = d.key === 'weight_kg' ? 'weight' : d.key === 'tdee' ? 'bmr' : d.key
      const lm = legacyMetrics.value.find((m) => m.key === legacyKey)
      value = lm ? dispValue(unit.value, d.key, lm.value) : null
    }
    let change: string | null = null
    let trendClass = ''
    if (cur && prev) {
      const diff = round1(dispValue(unit.value, d.key, (cur[d.key] ?? 0) - (prev[d.key] ?? 0)))
      if (diff !== null && diff !== 0) {
        change = `${diff > 0 ? '+' : ''}${diff}${d.unit}`
        trendClass = diff > 0 ? 'up' : 'down'
      } else {
        change = '0' + d.unit
      }
    } else {
      const lm = legacyMetrics.value.find((m) => m.key === (d.key === 'weight_kg' ? 'weight' : d.key === 'tdee' ? 'bmr' : d.key))
      if (lm && lm.change) {
        change = `${lm.change > 0 ? '+' : ''}${lm.change}${d.unit}`
        trendClass = lm.trend === 'down' ? 'down' : 'up'
      }
    }
    return { ...d, value: value == null ? '--' : fmtNum(value), change, trendClass }
  })
})

const measLatestText = computed(() => {
  const withMeas = records.value.find((r) => r.waist_cm != null || r.chest_cm != null || r.hip_cm != null || r.shoulder_cm != null || r.thigh_cm != null || r.arm_cm != null)
  return withMeas ? withMeas.record_date : '暂无'
})

// ---------- 事件 ----------
function onCalculated(res: any) {
  results.value = res
}

function onGoalSaved(g: any) {
  goal.value = g
  goalSavedAt.value = new Date().toISOString().slice(0, 10)
}

function onGoalCleared() {
  goal.value = null
  goalSavedAt.value = ''
}

// ---------- 档案 ----------
async function saveProfile() {
  try {
    await saveBodyProfile({ ...profile, unit_system: unit.value })
    localStorage.setItem('fitluxe_body_profile', JSON.stringify({ ...profile, unit_system: unit.value }))
    ElMessage.success('档案已保存')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

// ---------- 加载 ----------
async function loadRecords() {
  try {
    const res = await getBodyRecords()
    records.value = res.data.items
  } catch {
    records.value = []
  }
}

async function loadProfile() {
  try {
    const res = await getBodyProfile()
    profile.gender = res.data.gender || 'male'
    profile.age = res.data.age || 25
    profile.activity_level = res.data.activity_level || 'light'
    unit.value = res.data.unit_system || 'metric'
  } catch {
    const cached = localStorage.getItem('fitluxe_body_profile')
    if (cached) {
      try {
        const p = JSON.parse(cached)
        profile.gender = p.gender || 'male'
        profile.age = p.age || 25
        profile.activity_level = p.activity_level || 'light'
        unit.value = p.unit_system || 'metric'
      } catch { /* ignore */ }
    }
  }
}

async function loadGoals() {
  try {
    const res = await getBodyGoals()
    if (res.data.items.length) {
      goal.value = res.data.items[0]
      goalSavedAt.value = (goal.value.updated_at || '').slice(0, 10) || new Date().toISOString().slice(0, 10)
    }
  } catch { /* ignore */ }
}

onMounted(async () => {
  await Promise.all([loadRecords(), loadProfile(), loadGoals()])
  try {
    const res = await getBodyMetrics()
    legacyMetrics.value = res.data
  } catch { /* ignore */ }
})
</script>

<style scoped>
.page-hero { position: relative; padding: 160px 0 80px; background: var(--clr-black); overflow: hidden; }
.page-hero__bg { position: absolute; inset: 0; background: radial-gradient(ellipse at 30% 60%, rgba(201, 169, 110, 0.05), transparent 50%); }
.page-hero__content { position: relative; z-index: 1; }
.page-hero__label { font-size: 11px; letter-spacing: 4px; color: var(--clr-gold); margin-bottom: 16px; display: inline-block; }
.page-hero__title { font-family: var(--font-display); font-size: 48px; font-weight: 400; color: var(--clr-cream); margin-bottom: 16px; letter-spacing: 2px; }
.page-hero__desc { font-size: 15px; color: var(--clr-gray-light); max-width: 500px; }

/* ---------- 指标计算与趋势 ---------- */
.analytics { padding: 100px 0; }
.analytics__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 56px; align-items: start; }

/* ---------- AI 智能饮食规划 ---------- */
.ai-diet { padding: 100px 0; }

@media (max-width: 1024px) {
  .analytics__grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .page-hero { padding: 120px 0 56px; }
  .page-hero__title { font-size: 34px; }
}
</style>
