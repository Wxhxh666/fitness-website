// ============================================================
// 身材目标进度计算
// BodyGoal 之前只负责"存"，从没被展示过，用户设完目标就再也看不到进展。
// 这里把「起始值 → 当前值 → 目标值」换算成 0~1 的进度，交给环形图渲染。
// ============================================================
import { dispValue, fmtNum, round1, weightUnitLabel, type Unit } from './units'

export interface GoalMetric {
  key: 'weight_kg' | 'bmi' | 'body_fat'
  label: string
  unit: string
  /** 目标值（已按单位换算） */
  target: number | null
  /** 设定目标时（或最早一条记录）的起点值 */
  start: number | null
  /** 最近一条记录的当前值 */
  current: number | null
  /** 0~1，已完成的百分比 */
  progress: number
  /** 距离目标还差多少（带符号，正数表示还要降，负数表示还要升） */
  remaining: number | null
  /** 是否已达成 */
  reached: boolean
  /** 起点与目标相同、数据不足等无法计算进度的情形 */
  note: string
}

export interface GoalSummary {
  metrics: GoalMetric[]
  /** 综合进度：多个目标取平均，只算能算出进度的项 */
  overall: number
  /** 是否有任何目标被设定 */
  configured: boolean
  /** 设定目标那天 */
  startedAt: string
  /** 每日目标摄入（kcal），无起始值不参与进度，单独展示 */
  dailyCalorie: number | null
  /** 最近一条记录的 TDEE，用来对比缺口 */
  latestTdee: number | null
}

const clamp01 = (v: number) => Math.min(1, Math.max(0, v))

/** 取最早 / 最新的一条含指定字段的记录（records 按日期倒序传入） */
function pickBounds(records: any[], field: string) {
  let current: number | null = null
  let start: number | null = null
  for (const r of records) {
    const v = r?.[field]
    if (v == null || Number.isNaN(Number(v))) continue
    if (current === null) current = Number(v)
    start = Number(v) // 循环结束时剩下最后一条，即日期最早的那条
  }
  return { start, current }
}

function buildMetric(
  records: any[],
  unit: Unit,
  field: 'weight_kg' | 'bmi' | 'body_fat',
  label: string,
  unitLabel: string,
  targetRaw: number | null | undefined,
): GoalMetric {
  const { start: startRaw, current: currentRaw } = pickBounds(records, field)
  const toDisp = (v: number | null) => (v == null ? null : dispValue(unit, field, v))
  const start = toDisp(startRaw)
  const current = toDisp(currentRaw)
  const target = toDisp(targetRaw == null ? null : Number(targetRaw))

  let progress = 0
  let remaining: number | null = null
  let reached = false
  let note = ''

  if (target == null) {
    note = '未设定'
  } else if (current == null) {
    note = '暂无记录'
  } else {
    remaining = round1(target - current)
    // 达成判定必须看方向：减重目标降到 70 以下（68）当然算达成，
    // 只比较"是否接近目标"会把超额完成判成没完成。
    const tol = Math.max(0.3, Math.abs(target) * 0.005)
    if (start == null || Math.abs(start - target) < 1e-6) {
      // 起点就等于目标（或只有一条记录）：没有可画的"从哪走到哪"，只能看当前是否已达标
      reached = Math.abs(target - current) <= tol
    } else if (target < start) {
      reached = current <= target + tol // 减重：降到目标或更低
    } else {
      reached = current >= target - tol // 增重：升到目标或更高
    }

    if (start == null || Math.abs(start - target) < 1e-6) {
      progress = reached ? 1 : 0
      note = reached ? '' : '一条记录，暂无进度'
    } else {
      // 用「起点→当前」占「起点→目标」的比例。方向由起点与目标的相对大小自动决定，
      // 减重（target < start）和增重（target > start）用同一个式子。
      progress = clamp01((start - current) / (start - target))
      if (progress >= 1 || reached) note = '已达成'
    }
  }

  return {
    key: field,
    label,
    unit: unitLabel,
    target,
    start,
    current,
    progress: Math.round(progress * 1000) / 1000,
    remaining,
    reached,
    note,
  }
}

/**
 * @param records 身材记录，按 record_date 倒序（与接口返回一致）
 * @param goal    最新一条 BodyGoal，可为 null
 */
export function buildGoalSummary(records: any[], goal: any, unit: Unit): GoalSummary {
  const list = Array.isArray(records) ? records.filter(Boolean) : []
  const weightUnit = weightUnitLabel(unit)

  const metrics: GoalMetric[] = [
    buildMetric(list, unit, 'weight_kg', '体重', weightUnit, goal?.target_weight),
    buildMetric(list, unit, 'bmi', 'BMI', '', goal?.target_bmi),
    buildMetric(list, unit, 'body_fat', '体脂率', '%', goal?.target_body_fat),
  ]

  // 综合进度只统计"真正能算进度"的项：起点与目标不同、且两者都有值。
  // 只有一条记录时 start 等于 current，算出来的 0% 会把平均分拉低，那不代表没进展。
  const scored = metrics.filter(
    (m) => m.target != null && m.current != null && m.start != null && Math.abs(m.start - m.target) > 1e-6,
  )
  const overall = scored.length ? scored.reduce((s, m) => s + m.progress, 0) / scored.length : 0

  const latest = list.find((r) => r?.tdee != null)

  return {
    metrics,
    overall: Math.round(overall * 1000) / 1000,
    configured: metrics.some((m) => m.target != null),
    startedAt: (goal?.updated_at || goal?.created_at || '').slice(0, 10),
    dailyCalorie: goal?.daily_calorie != null ? Number(goal.daily_calorie) : null,
    latestTdee: latest ? Number(latest.tdee) : null,
  }
}

/**
 * 目标差额文案，用于「还差 X」。
 * 取绝对值：remaining 是带符号的（目标 - 当前），直接拼出来会出现"还差 -12kg"，
 * 方向交给调用方的文案决定（减重 / 增重）。
 */
export function fmtRemaining(m: GoalMetric): string {
  if (m.remaining == null) return '--'
  return `${fmtNum(Math.abs(m.remaining))}${m.unit}`
}
