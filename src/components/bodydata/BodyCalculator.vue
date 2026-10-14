<template>
  <div class="analytics__left">
    <div class="panel-card">
      <div class="panel-card__head">
        <h3 class="panel-card__title"><el-icon><DataAnalysis /></el-icon>多指标计算器</h3>
        <span class="panel-card__tag">BMI / 体脂 / BMR / TDEE</span>
      </div>
      <div class="calc__form">
        <div class="calc__form-grid">
          <div class="calc__field">
            <label>身高（{{ heightUnit }}）</label>
            <el-input-number v-model="heightDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：175" style="width: 100%" />
          </div>
          <div class="calc__field">
            <label>体重（{{ weightUnit }}）</label>
            <el-input-number v-model="weightDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：70" style="width: 100%" />
          </div>
          <div class="calc__field">
            <label>腰围（{{ cmUnit }}）</label>
            <el-input-number v-model="calcWaistDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：78" style="width: 100%" />
          </div>
          <div class="calc__field">
            <label>臀围（{{ cmUnit }}）</label>
            <el-input-number v-model="calcHipDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：96" style="width: 100%" />
          </div>
          <div class="calc__field">
            <label>颈围（{{ cmUnit }}，选填）</label>
            <el-input-number v-model="calcNeckDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：38" style="width: 100%" />
          </div>
          <div class="calc__field">
            <label>运动强度</label>
            <el-select v-model="profile.activity_level" style="width: 100%">
              <el-option v-for="opt in activityOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </div>
          <div class="calc__field">
            <label>年龄</label>
            <el-input-number v-model="profile.age" :min="10" :max="100" :controls="false" style="width: 100%" />
          </div>
          <div class="calc__field">
            <label>性别</label>
            <el-radio-group v-model="profile.gender" style="margin-top: 6px">
              <el-radio-button value="male">男</el-radio-button>
              <el-radio-button value="female">女</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="calc__actions">
          <button class="btn-primary" @click="onCalculate">计算全部指标</button>
          <button class="btn-outline-dark" :disabled="!results" @click="openSaveDialog">保存本次记录</button>
          <button class="btn-text" @click="clearCalcInputs">清空输入</button>
        </div>
        <p v-if="calcDirty" class="form-hint">参数已更新，点击「计算全部指标」刷新结果</p>
      </div>

      <div class="calc__results">
        <div v-if="!results" class="calc__empty">
          <el-icon :size="36"><DataAnalysis /></el-icon>
          <p>填写上方参数并点击「计算全部指标」，这里会展示完整的身体数据画像。</p>
        </div>
        <template v-else>
          <div class="calc__cards">
            <div v-for="m in metricCards" :key="m.key" class="metric-detail-card">
              <div class="metric-detail-card__head">
                <span class="metric-detail-card__label">{{ m.label }}</span>
                <span v-if="m.tag" class="metric-detail-card__tag">{{ m.tag }}</span>
              </div>
              <div class="metric-detail-card__value">
                <span class="metric-detail-card__num">{{ m.value }}</span>
                <span class="metric-detail-card__unit">{{ m.unit }}</span>
              </div>
              <div v-if="m.category" class="metric-detail-card__category" :class="m.categoryClass">{{ m.category }}</div>
              <div class="metric-detail-card__bar">
                <div class="metric-detail-card__track">
                  <div class="metric-detail-card__healthy" :style="healthyStyle(m)"></div>
                  <div class="metric-detail-card__dot" :style="dotStyle(m)"></div>
                </div>
                <div class="metric-detail-card__scale"><span>{{ m.scale[0] }}</span><span>{{ m.scale[1] }}</span></div>
              </div>
            </div>
          </div>

          <div class="health-tips">
            <h3 class="health-tips__title"><el-icon><FirstAidKit /></el-icon>健康风险简易评估</h3>
            <ul class="health-tips__list">
              <li v-for="(tip, i) in results.health_tips" :key="i" class="health-tips__item" :class="`health-tips__item--${tip.level}`">
                <span class="health-tips__dot"></span>{{ tip.text }}
              </li>
            </ul>
            <p class="health-tips__note">* 提示基于 BMI、体脂、腰围与年龄自动生成，仅作参考，不构成医疗建议。</p>
          </div>
        </template>
      </div>
    </div>

    <el-dialog v-model="saveDialog.visible" title="保存本次记录" width="420px">
      <div class="save-dialog">
        <div class="save-dialog__field">
          <label>当前阶段</label>
          <el-select v-model="saveDialog.stage" style="width: 100%">
            <el-option label="减脂" value="fatloss" />
            <el-option label="增肌" value="muscle" />
            <el-option label="保持" value="maintain" />
          </el-select>
        </div>
        <div class="save-dialog__field">
          <label>记录日期</label>
          <el-date-picker v-model="saveDialog.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </div>
        <p class="save-dialog__tip">保存后会自动同步核心指标卡片，并进入趋势图与对比列表。</p>
      </div>
      <template #footer>
        <el-button @click="saveDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveRecord">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { calculateBodyMetrics, saveBodyRecord } from '@/api'
import { fmtNum, fmtDisp, round1, cmField, weightField } from '@/utils/units'
import type { Unit } from '@/utils/units'

const props = defineProps<{
  profile: any
  unit: Unit
  activityOptions: { value: string; label: string }[]
}>()

const emit = defineEmits<{
  (e: 'calculated', results: any): void
  (e: 'saved'): void
}>()

const heightCm = ref<number | null>(null)
const weightKg = ref<number | null>(null)
const calcWaistCm = ref<number | null>(null)
const calcHipCm = ref<number | null>(null)
const calcNeckCm = ref<number | null>(null)
const results = ref<any>(null)
const saveDialog = reactive({ visible: false, stage: 'fatloss', date: '' })
const calcDirty = ref(false)
let calcHintTimer: any = null

const weightUnit = computed(() => (props.unit === 'imperial' ? 'lb' : 'kg'))
const cmUnit = computed(() => (props.unit === 'imperial' ? 'in' : 'cm'))
const heightUnit = computed(() => (props.unit === 'imperial' ? 'in' : 'cm'))

const heightDisplay = cmField(() => props.unit, heightCm)
const weightDisplay = weightField(() => props.unit, weightKg)
const calcWaistDisplay = cmField(() => props.unit, calcWaistCm)
const calcHipDisplay = cmField(() => props.unit, calcHipCm)
const calcNeckDisplay = cmField(() => props.unit, calcNeckCm)

function flashHint() {
  calcDirty.value = true
  clearTimeout(calcHintTimer)
  calcHintTimer = setTimeout(() => { calcDirty.value = false }, 3000)
}

watch(
  [heightCm, weightKg, calcWaistCm, calcHipCm, calcNeckCm, () => props.profile.age, () => props.profile.activity_level, () => props.profile.gender],
  () => flashHint()
)

function pct(v: number | null | undefined, scale: number[]) {
  if (v == null) return 0
  const [min, max] = scale
  return Math.max(0, Math.min(100, ((v - min) / (max - min)) * 100))
}

const metricCards = computed(() => {
  if (!results.value) return []
  const r = results.value
  const male = r.gender === 'male'
  const stdScale = r.healthy_weight_range ? [r.healthy_weight_range[0] - 8, r.healthy_weight_range[1] + 8] : [40, 90]
  return [
    {
      key: 'bmi', label: 'BMI 身体质量指数', value: fmtNum(r.bmi), unit: '',
      scale: [10, 40], healthy: [18.5, 24.9], category: r.bmi_category_label,
      categoryClass: `cat-${r.bmi_category || 'unknown'}`,
    },
    {
      key: 'body_fat', label: '体脂率', value: fmtNum(r.body_fat), unit: '%',
      scale: [0, 40], healthy: r.body_fat_range, category: male ? '男性正常 10% - 20%' : '女性正常 18% - 28%',
      categoryClass: 'cat-normal', tag: r.body_fat_formula === 'navy' ? 'US Navy 公式' : '简化公式',
    },
    {
      key: 'bmr', label: '基础代谢 BMR', value: fmtNum(r.bmr, 0), unit: 'kcal',
      scale: r.bmr_range, healthy: [1200, 1800], category: 'Mifflin-St Jeor 公式',
      categoryClass: 'cat-normal',
    },
    {
      key: 'tdee', label: '每日消耗 TDEE', value: fmtNum(r.tdee, 0), unit: 'kcal',
      scale: r.tdee_range, healthy: [1600, 3200], category: `${r.activity_label} × ${r.tdee_multiplier}`,
      categoryClass: 'cat-normal',
    },
    {
      key: 'whr', label: '腰臀比 WHR', value: fmtNum(r.whr, 2), unit: '',
      scale: r.whr_range, healthy: [0.6, r.whr_healthy_max], category: `健康参考 ≤ ${r.whr_healthy_max}`,
      categoryClass: 'cat-normal',
    },
    {
      key: 'muscle_mass', label: '肌肉量估算', value: fmtDisp(props.unit, 'muscle_mass', r.muscle_mass), unit: weightUnit.value,
      scale: r.muscle_mass_range, healthy: r.muscle_mass_range, category: '基于体重与体脂估算',
      categoryClass: 'cat-normal',
    },
    {
      key: 'standard_weight', label: '标准体重参考', value: fmtDisp(props.unit, 'standard_weight', r.standard_weight), unit: weightUnit.value,
      scale: stdScale, healthy: r.healthy_weight_range, category: '以 BMI 22 为理想值',
      categoryClass: 'cat-normal',
    },
  ]
})

function healthyStyle(m: any) {
  const left = pct(m.healthy?.[0], m.scale)
  const right = pct(m.healthy?.[1], m.scale)
  return { left: left + '%', width: Math.max(right - left, 2) + '%' }
}

function dotStyle(m: any) {
  const raw = results.value ? results.value[m.key] : null
  return { left: pct(raw, m.scale) + '%' }
}

function buildCalcPayload() {
  return {
    gender: props.profile.gender,
    age: props.profile.age,
    activity_level: props.profile.activity_level,
    height_cm: heightCm.value,
    weight_kg: weightKg.value,
    waist_cm: calcWaistCm.value,
    hip_cm: calcHipCm.value,
    neck_cm: calcNeckCm.value,
  }
}

async function onCalculate() {
  if (!heightCm.value || !weightKg.value) {
    ElMessage.warning('请先填写身高与体重')
    return
  }
  try {
    const res = await calculateBodyMetrics(buildCalcPayload())
    results.value = res.data
    emit('calculated', res.data)
  } catch (e: any) {
    ElMessage.error(e?.message || '计算失败')
  }
}

function clearCalcInputs() {
  heightCm.value = null
  weightKg.value = null
  calcWaistCm.value = null
  calcHipCm.value = null
  calcNeckCm.value = null
  results.value = null
}

function openSaveDialog() {
  if (!results.value) return
  saveDialog.stage = 'fatloss'
  saveDialog.date = new Date().toISOString().slice(0, 10)
  saveDialog.visible = true
}

async function confirmSaveRecord() {
  try {
    const payload = {
      ...buildCalcPayload(),
      stage: saveDialog.stage,
      record_date: saveDialog.date,
    }
    await saveBodyRecord(payload)
    saveDialog.visible = false
    ElMessage.success('记录已保存')
    emit('saved')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}
</script>

<style scoped>
.panel-card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 26px; }
.panel-card__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.panel-card__title { font-size: 16px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
.panel-card__title .el-icon { color: var(--clr-gold); }
.panel-card__tag { font-size: 11px; color: var(--clr-gold-dark); border: 1px solid rgba(12, 216, 160, 0.4); padding: 2px 8px; letter-spacing: 1px; }

.calc__form { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 24px; margin-bottom: 20px; }
.calc__form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.calc__field label { display: block; font-size: 12px; letter-spacing: 1px; color: var(--clr-gray); margin-bottom: 6px; }
.calc__actions { display: flex; align-items: center; gap: 12px; margin-top: 22px; flex-wrap: wrap; }
.btn-text { background: none; border: none; color: var(--clr-gray); font-size: 13px; letter-spacing: 1px; cursor: pointer; padding: 8px 4px; transition: var(--transition-default); }
.btn-text:hover { color: var(--clr-gold-dark); }

.calc__results { min-height: 160px; }
.calc__empty { border: 1px dashed rgba(0, 0, 0, 0.14); padding: 56px 24px; text-align: center; color: var(--clr-gray); font-size: 13px; }
.calc__empty .el-icon { color: var(--clr-gold); margin-bottom: 12px; }
.calc__cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.metric-detail-card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 16px; }
.metric-detail-card__head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.metric-detail-card__label { font-size: 12px; letter-spacing: 1px; color: var(--clr-gray); }
.metric-detail-card__tag { font-size: 10px; color: var(--clr-gold-dark); border: 1px solid rgba(12, 216, 160, 0.4); padding: 1px 6px; letter-spacing: 0.5px; }
.metric-detail-card__value { display: flex; align-items: baseline; gap: 4px; margin-bottom: 2px; }
.metric-detail-card__num { font-family: var(--font-display); font-size: 26px; color: var(--clr-dark); }
.metric-detail-card__unit { font-size: 12px; color: var(--clr-gray); }
.metric-detail-card__category { font-size: 11px; margin-bottom: 12px; }
.cat-normal { color: #6b8e6b; }
.cat-underweight { color: #0CD8A0; }
.cat-overweight { color: #0CD8A0; }
.cat-obese { color: #c0392b; }
.cat-unknown { color: var(--clr-gray); }
.metric-detail-card__bar { margin-top: 4px; }
.metric-detail-card__track { position: relative; height: 6px; background: linear-gradient(to right, #0CD8A0 0%, #6b8e6b 30%, #6b8e6b 55%, #0CD8A0 75%, #c0392b 100%); border-radius: 3px; }
.metric-detail-card__healthy { position: absolute; top: -2px; height: 10px; border: 1px dashed rgba(17, 17, 17, 0.45); border-radius: 3px; background: rgba(255, 255, 255, 0.25); }
.metric-detail-card__dot { position: absolute; top: -4px; width: 14px; height: 14px; border-radius: 50%; background: var(--clr-dark); border: 2px solid var(--clr-white); transform: translateX(-7px); z-index: 2; box-shadow: 0 1px 5px rgba(0, 0, 0, 0.3); }
.metric-detail-card__scale { display: flex; justify-content: space-between; margin-top: 8px; font-size: 10px; color: var(--clr-gray-light); }

.health-tips { margin-top: 18px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 18px 20px; }
.health-tips__title { font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: var(--clr-dark); }
.health-tips__title .el-icon { color: var(--clr-gold); }
.health-tips__list { display: flex; flex-direction: column; gap: 9px; }
.health-tips__item { display: flex; align-items: flex-start; gap: 10px; font-size: 12px; line-height: 1.6; color: var(--clr-gray-deep); }
.health-tips__dot { width: 7px; height: 7px; border-radius: 50%; margin-top: 7px; flex-shrink: 0; }
.health-tips__item--info .health-tips__dot { background: #6b8e6b; }
.health-tips__item--warn .health-tips__dot { background: #0CD8A0; }
.health-tips__item--danger .health-tips__dot { background: #c0392b; }
.health-tips__note { margin-top: 12px; font-size: 11px; color: var(--clr-gray-light); }

.save-dialog__field { margin-bottom: 16px; }
.save-dialog__field label { display: block; font-size: 12px; color: var(--clr-gray); margin-bottom: 6px; }
.save-dialog__tip { font-size: 12px; color: var(--clr-gray-light); margin-top: 8px; }

@media (max-width: 768px) {
  .calc__form-grid { grid-template-columns: 1fr; }
  .calc__cards { grid-template-columns: 1fr 1fr; }
}
</style>
