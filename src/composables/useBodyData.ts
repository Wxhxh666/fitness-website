// ============================================================
// useBodyData · 身材数据模块共享状态（模块级单例）
// 供「身体概览 / 指标趋势 / AI 饮食 / 数据管理」四个子页共用，
// 避免各子页重复加载、单位/档案状态不同步。
//
// 私有数据接口现在都要求登录：未登录时不再发请求（否则后端会返回 401），
// 只用本地缓存的档案兜底，页面照常可看、可算，但不会产生任何数据。
// ============================================================
import { ref, reactive, computed } from 'vue'
import {
  getBodyMetrics,
  getBodyRecords,
  getBodyProfile,
  saveBodyProfile,
  getBodyGoals,
  getToken,
} from '@/api'
import { fmtNum, dispValue, round1, weightUnitLabel } from '@/utils/units'
import type { Unit } from '@/utils/units'

// ---------- 共享状态 ----------
const unit = ref<Unit>('metric')
const profile = reactive({ gender: 'male', age: 25, activity_level: 'light' })
const records = ref<any[]>([])
const legacyMetrics = ref<any[]>([])
const goal = ref<any>(null)
const goalSavedAt = ref('')
const results = ref<any>(null)
// 初始值直接读 token，避免已登录用户进页面时闪一下“访客模式”提示条
const authed = ref(!!getToken())

/**
 * 记录“上次是用哪个 token 加载的”。
 * 用 token 而不是布尔值，才能覆盖「匿名浏览 → 登录 → 回到本页」的场景：
 * token 变了就重新拉一次数据。
 */
let loadedToken: string | null = null

export const activityOptions = [
  { value: 'sedentary', label: '久坐少动' },
  { value: 'light', label: '轻度运动' },
  { value: 'moderate', label: '中度力量训练' },
  { value: 'intense', label: '高强度训练' },
]

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
    { key: 'weight_kg', label: '体重', icon: 'Odometer', unit: weightUnit.value },
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

// ---------- 数据管理入口文案 ----------
const measLatestText = computed(() => {
  const withMeas = records.value.find((r) => r.waist_cm != null || r.chest_cm != null || r.hip_cm != null || r.shoulder_cm != null || r.thigh_cm != null || r.arm_cm != null)
  return withMeas ? withMeas.record_date : '暂无'
})

const recordCount = computed(() => records.value.length)

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

// ---------- 加载 ----------
function loadLocalProfile() {
  const cached = localStorage.getItem('fitluxe_body_profile')
  if (!cached) return
  try {
    const p = JSON.parse(cached)
    profile.gender = p.gender || 'male'
    profile.age = p.age || 25
    profile.activity_level = p.activity_level || 'light'
    unit.value = p.unit_system || 'metric'
  } catch { /* 缓存损坏时忽略 */ }
}

async function loadRecords() {
  if (!getToken()) { records.value = []; return }
  try {
    const res = await getBodyRecords()
    records.value = res.data.items
  } catch {
    records.value = []
  }
}

async function loadProfile() {
  if (!getToken()) { loadLocalProfile(); return }
  try {
    const res = await getBodyProfile()
    profile.gender = res.data.gender || 'male'
    profile.age = res.data.age || 25
    profile.activity_level = res.data.activity_level || 'light'
    unit.value = res.data.unit_system || 'metric'
  } catch {
    loadLocalProfile()
  }
}

async function loadGoals() {
  if (!getToken()) { goal.value = null; return }
  try {
    const res = await getBodyGoals()
    if (res.data.items.length) {
      goal.value = res.data.items[0]
      goalSavedAt.value = (goal.value.updated_at || '').slice(0, 10) || new Date().toISOString().slice(0, 10)
    }
  } catch { /* 未登录或接口异常时保持空目标 */ }
}

async function loadLegacyMetrics() {
  if (!getToken()) { legacyMetrics.value = []; return }
  try {
    const res = await getBodyMetrics()
    legacyMetrics.value = res.data
  } catch { /* ignore */ }
}

/** 首次进入任一身材子页（或登录状态变化）时加载全部数据 */
async function loadAll() {
  const token = getToken()
  authed.value = !!token
  if (!token) {
    loadedToken = null
    records.value = []
    legacyMetrics.value = []
    goal.value = null
    loadLocalProfile()
    return
  }
  if (loadedToken === token) return
  loadedToken = token
  await Promise.all([loadRecords(), loadProfile(), loadGoals()])
  await loadLegacyMetrics()
}

/** 登录 / 退出后调用，强制下次进入页面重新拉取 */
function resetLoaded() {
  loadedToken = null
}

// ---------- 档案 ----------
async function saveProfile() {
  if (!getToken()) {
    throw new Error('请先登录后再保存档案')
  }
  await saveBodyProfile({ ...profile, unit_system: unit.value })
  localStorage.setItem('fitluxe_body_profile', JSON.stringify({ ...profile, unit_system: unit.value }))
  return true
}

export function useBodyData() {
  return {
    unit,
    profile,
    records,
    legacyMetrics,
    goal,
    goalSavedAt,
    results,
    authed,
    activityOptions,
    weightUnit,
    topMetrics,
    measLatestText,
    recordCount,
    latestWith,
    prevWith,
    earliestWith,
    onCalculated,
    onGoalSaved,
    onGoalCleared,
    loadAll,
    loadRecords,
    loadProfile,
    saveProfile,
    resetLoaded,
  }
}
