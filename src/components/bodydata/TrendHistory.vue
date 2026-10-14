<template>
  <div class="analytics__right">
    <div class="panel-card">
      <div class="panel-card__head">
        <h3 class="panel-card__title"><el-icon><Scale /></el-icon>BMI 参考标准</h3>
      </div>
      <div class="bmi-guide">
        <div class="bmi-guide__row"><span class="bmi-guide__range">&lt; 18.5</span><span class="bmi-guide__label">偏瘦</span></div>
        <div class="bmi-guide__row"><span class="bmi-guide__range">18.5 – 24.9</span><span class="bmi-guide__label normal">正常范围</span></div>
        <div class="bmi-guide__row"><span class="bmi-guide__range">25 – 29.9</span><span class="bmi-guide__label">超重</span></div>
        <div class="bmi-guide__row"><span class="bmi-guide__range">≥ 30</span><span class="bmi-guide__label">肥胖</span></div>
        <p class="bmi-guide__note">* BMI 仅供参考，运动员等肌肉量较高的人群可能不适用，请结合体脂率判断。</p>
      </div>
    </div>

    <div class="panel-card">
      <div class="panel-card__head">
        <h3 class="panel-card__title"><el-icon><TrendCharts /></el-icon>历史身材数据趋势</h3>
      </div>
      <div class="trend-tools">
        <el-select v-model="rangeDays" size="small" style="width: 110px">
          <el-option label="近 30 天" value="30" />
          <el-option label="近 90 天" value="90" />
          <el-option label="全部" value="all" />
        </el-select>
        <el-select v-model="chartMetric" size="small" style="width: 120px">
          <el-option v-for="opt in trendMetricOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-radio-group v-model="chartGroup" size="small">
          <el-radio-button value="record">按次</el-radio-button>
          <el-radio-button value="week">按周</el-radio-button>
          <el-radio-button value="month">按月</el-radio-button>
        </el-radio-group>
      </div>
      <LineChart :items="trendItems" :unit="trendUnit" color="#0CD8A0" />
      <div class="trend-foot">
        <span class="trend-foot__hint">选择两条记录可自动生成对比小结</span>
        <button class="btn-outline-dark trend-foot__btn" @click="emit('open-history')">数据存档与对比</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import LineChart from '@/components/LineChart.vue'
import { dispValue, weightUnitLabel, cmUnitLabel } from '@/utils/units'
import type { Unit } from '@/utils/units'

const props = defineProps<{
  records: any[]
  unit: Unit
}>()

const emit = defineEmits<{
  (e: 'open-history'): void
}>()

const trendMetricOptions = [
  { value: 'weight_kg', label: '体重' },
  { value: 'bmi', label: 'BMI' },
  { value: 'body_fat', label: '体脂率' },
  { value: 'waist_cm', label: '腰围' },
  { value: 'muscle_mass', label: '肌肉量' },
  { value: 'tdee', label: '每日消耗' },
]

const stageOptions = [
  { value: 'fatloss', label: '减脂' },
  { value: 'muscle', label: '增肌' },
  { value: 'maintain', label: '保持' },
]

const rangeDays = ref<'30' | '90' | 'all'>('30')
const chartMetric = ref('weight_kg')
const chartGroup = ref<'record' | 'week' | 'month'>('week')

const weightUnit = computed(() => weightUnitLabel(props.unit))
const cmUnit = computed(() => cmUnitLabel(props.unit))

function stageLabel(stage: string) {
  return stageOptions.find((s) => s.value === stage)?.label || stage
}

function weekLabel(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  const day = (d.getDay() + 6) % 7
  d.setDate(d.getDate() - day)
  return `${d.getMonth() + 1}/${d.getDate()}周`
}

function monthLabel(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  return `${d.getMonth() + 1}月`
}

const trendItems = computed(() => {
  let list = [...props.records]
  if (rangeDays.value !== 'all') {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - Number(rangeDays.value))
    const cutoffStr = cutoff.toISOString().slice(0, 10)
    list = list.filter((r) => r.record_date >= cutoffStr)
  }
  list.sort((a, b) => (a.record_date < b.record_date ? -1 : 1))
  const key = chartMetric.value
  const points = list
    .filter((r) => r[key] != null)
    .map((r) => ({
      label: r.record_date,
      value: dispValue(props.unit, key, r[key]) as number,
      marker: r.stage ? stageLabel(r.stage) : '',
    }))

  if (chartGroup.value === 'record') return points

  const groups: { label: string; value: number; marker: string }[] = []
  for (const p of points) {
    const gLabel = chartGroup.value === 'week' ? weekLabel(p.label) : monthLabel(p.label)
    const last = groups[groups.length - 1]
    if (last && last.label === gLabel) {
      last.value = p.value
      if (p.marker) last.marker = p.marker
    } else {
      groups.push({ label: gLabel, value: p.value, marker: p.marker })
    }
  }
  return groups
})

const trendUnit = computed(() => {
  const key = chartMetric.value
  if (key === 'weight_kg' || key === 'muscle_mass') return weightUnit.value
  if (key === 'waist_cm') return cmUnit.value
  if (key === 'body_fat') return '%'
  if (key === 'tdee') return 'kcal'
  return ''
})
</script>

<style scoped>
.analytics__right { display: flex; flex-direction: column; gap: 28px; }
.panel-card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 26px; }
.panel-card__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.panel-card__title { font-size: 16px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
.panel-card__title .el-icon { color: var(--clr-gold); }

.bmi-guide { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.04); padding: 8px 22px; }
.bmi-guide__row { display: flex; justify-content: space-between; align-items: center; padding: 13px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.04); }
.bmi-guide__range { font-family: var(--font-display); font-size: 16px; color: var(--clr-dark); }
.bmi-guide__label { font-size: 13px; color: var(--clr-gray); letter-spacing: 1px; }
.bmi-guide__label.normal { color: #6b8e6b; }
.bmi-guide__note { margin-top: 14px; font-size: 11px; color: var(--clr-gray-light); line-height: 1.6; }

.trend-tools { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
.trend-foot { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
.trend-foot__hint { font-size: 12px; color: var(--clr-gray-light); }
</style>
