<template>
  <el-dialog v-model="visible" title="身材目标管理" width="860px">
    <div class="entry-dialog">
      <div class="goals__layout">
        <div class="goals__form">
          <div class="goals__form-grid">
            <div class="goals__field">
              <label>目标体重（{{ weightUnit }}）</label>
              <el-input-number v-model="goalWeightDisplay" :min="0" :step="0.1" :controls="false" style="width: 100%" />
            </div>
            <div class="goals__field">
              <label>目标 BMI</label>
              <el-input-number v-model="goalForm.target_bmi" :min="10" :max="45" :step="0.1" :controls="false" style="width: 100%" />
            </div>
            <div class="goals__field">
              <label>目标体脂率（%）</label>
              <el-input-number v-model="goalForm.target_body_fat" :min="3" :max="50" :step="0.1" :controls="false" style="width: 100%" />
            </div>
            <div class="goals__field">
              <label>每日热量缺口 / 盈余（kcal）</label>
              <el-select v-model="calorieDelta" style="width: 100%">
                <el-option label="250 kcal / 天（温和）" :value="250" />
                <el-option label="350 kcal / 天" :value="350" />
                <el-option label="500 kcal / 天（推荐）" :value="500" />
                <el-option label="750 kcal / 天（激进）" :value="750" />
              </el-select>
            </div>
          </div>
          <div class="goals__actions">
            <button class="btn-primary" @click="saveGoal">保存目标</button>
            <button class="btn-text btn-text--light" @click="clearGoal">清除目标</button>
          </div>
          <p v-if="goalSavedAt" class="goals__saved">当前目标保存于 {{ goalSavedAt }}</p>
        </div>
        <div class="goals__result">
          <div v-if="!goalPlan" class="goals__empty">
            <el-icon :size="36"><Flag /></el-icon>
            <p>设定目标后，这里会展示完成进度与基于 TDEE 的热量方案。</p>
            <p class="goals__empty-note">提示：热量推算依赖已保存记录中的 TDEE，请先保存一条含年龄与运动强度的记录。</p>
          </div>
          <template v-else>
            <div class="goals__progress">
              <div v-for="g in goalProgressCards" :key="g.key" class="goal-progress">
                <div class="goal-progress__head">
                  <span>{{ g.label }}</span>
                  <span class="goal-progress__pct">{{ g.percent === null ? '--' : g.percent + '%' }}</span>
                </div>
                <div class="goal-progress__track">
                  <div class="goal-progress__fill" :style="{ width: (g.percent ?? 0) + '%' }"></div>
                </div>
                <div class="goal-progress__sub">
                  <span>当前 {{ g.current }}</span>
                  <span>目标 {{ g.target }}</span>
                </div>
              </div>
            </div>
            <div class="goal-plan">
              <h3 class="goal-plan__title"><el-icon><Odometer /></el-icon>每日热量方案</h3>
              <div class="goal-plan__row"><span>当前每日消耗 TDEE</span><b>{{ goalPlan.tdee }} kcal</b></div>
              <div class="goal-plan__row"><span>建议每日摄入</span><b class="goal-plan__accent">{{ goalPlan.intake }} kcal</b></div>
              <div class="goal-plan__row"><span>每日{{ goalPlan.direction === 'loss' ? '热量缺口' : '热量盈余' }}</span><b>{{ goalPlan.delta }} kcal</b></div>
              <div class="goal-plan__row"><span>预估达成天数</span><b>{{ goalPlan.days }} 天</b></div>
              <div class="goal-plan__row"><span>预计达成日期</span><b>{{ goalPlan.targetDate }}</b></div>
              <p class="goal-plan__note">* 按「每减 / 增 1kg 体重约需 7700 kcal」粗略估算，实际进度因人而异。</p>
            </div>
          </template>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { saveBodyGoal, deleteBodyGoal } from '@/api'
import { fmtDisp, fmtNum, round1, kgToLb, lbToKg, weightUnitLabel } from '@/utils/units'
import { ensureLogin } from '@/utils/authGuard'
import type { Unit } from '@/utils/units'

const visible = defineModel<boolean>('visible', { default: false })

const props = defineProps<{
  records: any[]
  goal: any
  goalSavedAt: string
  unit: Unit
}>()

const emit = defineEmits<{
  (e: 'saved', goal: any): void
  (e: 'cleared'): void
}>()

const goalForm = reactive({ target_weight: null as number | null, target_bmi: null as number | null, target_body_fat: null as number | null })
const calorieDelta = ref(500)

const weightUnit = computed(() => weightUnitLabel(props.unit))

const goalWeightDisplay = computed({
  get: () => (props.unit === 'imperial' ? round1(kgToLb(goalForm.target_weight)) : goalForm.target_weight),
  set: (v: number | null | undefined) => {
    goalForm.target_weight = props.unit === 'imperial' ? lbToKg(v ?? null) : (v ?? null)
  },
})

function latestWith(field: string) {
  for (const r of props.records) if (r[field] != null) return r
  return null
}

function earliestWith(field: string) {
  const asc = [...props.records].sort((a, b) => (a.record_date < b.record_date ? -1 : 1))
  for (const r of asc) if (r[field] != null) return r
  return null
}

const goalPlan = computed(() => {
  const cur = latestWith('weight_kg')
  if (!props.goal || !cur || !cur.tdee) return null
  const tdee = cur.tdee as number
  const target = props.goal.target_weight
  const current = cur.weight_kg as number
  if (target == null) {
    return {
      tdee, intake: tdee, delta: 0, days: 0,
      targetDate: new Date().toISOString().slice(0, 10),
      direction: 'maintain',
    }
  }
  const diff = current - target
  const delta = calorieDelta.value
  if (diff > 0.5) {
    const days = Math.ceil((diff * 7700) / delta)
    const d = new Date()
    d.setDate(d.getDate() + days)
    return { tdee, intake: tdee - delta, delta, days, targetDate: d.toISOString().slice(0, 10), direction: 'loss' }
  }
  if (diff < -0.5) {
    const days = Math.ceil((-diff * 7700) / delta)
    const d = new Date()
    d.setDate(d.getDate() + days)
    return { tdee, intake: tdee + delta, delta, days, targetDate: d.toISOString().slice(0, 10), direction: 'gain' }
  }
  return { tdee, intake: tdee, delta: 0, days: 0, targetDate: new Date().toISOString().slice(0, 10), direction: 'maintain' }
})

const goalProgressCards = computed(() => {
  const fields = [
    { key: 'weight_kg', label: '体重目标', target: props.goal?.target_weight, unit: weightUnit.value },
    { key: 'bmi', label: 'BMI 目标', target: props.goal?.target_bmi, unit: '' },
    { key: 'body_fat', label: '体脂率目标', target: props.goal?.target_body_fat, unit: '%' },
  ]
  return fields.map((f) => {
    const start = earliestWith(f.key)
    const current = latestWith(f.key)
    if (!start || !current || f.target == null) {
      return { ...f, current: '--', target: f.target == null ? '--' : fmtDisp(props.unit, f.key, f.target), percent: null }
    }
    const s = start[f.key] as number
    const c = current[f.key] as number
    const t = f.target as number
    const span = s - t
    const pctDone = span === 0 ? 100 : Math.max(0, Math.min(100, ((s - c) / span) * 100))
    return {
      ...f,
      current: fmtDisp(props.unit, f.key, c),
      target: fmtDisp(props.unit, f.key, t),
      percent: Math.round(pctDone),
    }
  })
})

async function saveGoal() {
  const hasAny = goalForm.target_weight != null || goalForm.target_bmi != null || goalForm.target_body_fat != null
  if (!hasAny) {
    ElMessage.warning('请至少设定一个目标')
    return
  }
  if (!ensureLogin('请先登录后再设定目标')) return
  const payload: any = {
    target_weight: goalForm.target_weight,
    target_bmi: goalForm.target_bmi,
    target_body_fat: goalForm.target_body_fat,
  }
  if (goalPlan.value) payload.daily_calorie = goalPlan.value.intake
  try {
    const res = await saveBodyGoal(payload)
    emit('saved', res.data)
    ElMessage.success('目标已保存')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

async function clearGoal() {
  if (!props.goal) return
  if (!ensureLogin('请先登录后再操作')) return
  try {
    await deleteBodyGoal(props.goal.id)
    emit('cleared')
    goalForm.target_weight = null
    goalForm.target_bmi = null
    goalForm.target_body_fat = null
    ElMessage.success('目标已清除')
  } catch (e: any) {
    ElMessage.error(e?.message || '清除失败')
  }
}
</script>

<style scoped>
.entry-dialog .goals__layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; align-items: start; }
.entry-dialog .goals__form { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.entry-dialog .goals__form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.goals__field label { display: block; font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; margin-bottom: 6px; }
.entry-dialog .goals__actions { display: flex; align-items: center; gap: 12px; margin-top: 20px; }
.btn-text { background: none; border: none; color: var(--clr-gray); font-size: 13px; letter-spacing: 1px; cursor: pointer; padding: 8px 4px; transition: var(--transition-default); }
.btn-text:hover { color: var(--clr-gold-dark); }
.btn-text--light { color: var(--clr-gray-light); }
.btn-text--light:hover { color: var(--clr-gold); }
.goals__saved { margin-top: 12px; font-size: 12px; color: var(--clr-gray); }
.entry-dialog .goals__result { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.goals__empty { text-align: center; padding: 40px 16px; color: var(--clr-gray); font-size: 13px; }
.goals__empty .el-icon { color: var(--clr-gold); margin-bottom: 12px; }
.goals__empty-note { margin-top: 8px; font-size: 11px; color: var(--clr-gray-light); }
.entry-dialog .goals__progress { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }
.goal-progress__head { display: flex; justify-content: space-between; font-size: 13px; color: var(--clr-dark); margin-bottom: 8px; }
.goal-progress__pct { color: var(--clr-gold-dark); font-weight: 500; }
.goal-progress__track { height: 6px; background: rgba(0, 0, 0, 0.08); border-radius: 3px; overflow: hidden; }
.goal-progress__fill { height: 100%; background: linear-gradient(to right, var(--clr-gold), var(--clr-gold-light)); border-radius: 3px; transition: width 0.5s ease; }
.goal-progress__sub { display: flex; justify-content: space-between; margin-top: 6px; font-size: 11px; color: var(--clr-gray); }
.goal-plan { border-top: 1px solid rgba(0, 0, 0, 0.08); padding-top: 16px; }
.goal-plan__title { font-size: 14px; display: flex; align-items: center; gap: 8px; color: var(--clr-dark); margin-bottom: 12px; font-weight: 500; }
.goal-plan__title .el-icon { color: var(--clr-gold); }
.goal-plan__row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05); font-size: 13px; color: var(--clr-gray-deep); }
.goal-plan__row b { font-weight: 500; color: var(--clr-dark); }
.goal-plan__accent { color: var(--clr-gold-dark) !important; font-size: 16px; }
.goal-plan__note { margin-top: 12px; font-size: 11px; color: var(--clr-gray-light); }

@media (max-width: 1024px) {
  .entry-dialog .goals__layout { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .entry-dialog .goals__form-grid { grid-template-columns: 1fr; }
}
</style>
