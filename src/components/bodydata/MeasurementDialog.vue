<template>
  <el-dialog v-model="visible" title="围度记录" width="900px">
    <div class="entry-dialog">
      <div class="measurements__layout">
        <div class="measurements__form">
          <div class="measurements__grid">
            <div v-for="f in measurementFields" :key="f.key" class="measurement-field">
              <label>{{ f.label }}（{{ cmUnit }}）</label>
              <el-input-number v-model="f.model" :min="0" :step="0.1" :controls="false" placeholder="输入数值" style="width: 100%" />
            </div>
          </div>
          <div class="measurements__actions">
            <button class="btn-primary" @click="saveMeasurements">保存本次围度</button>
            <button class="btn-text" @click="clearMeasurements">清空</button>
          </div>
        </div>
        <div class="measurements__chart">
          <div class="measurements__chart-head">
            <el-select v-model="measChartMetric" size="small" style="width: 140px">
              <el-option v-for="f in measurementFields" :key="f.key" :label="f.label" :value="f.key" />
            </el-select>
            <span class="measurements__chart-hint">最近 {{ measChartItems.length }} 次测量（{{ cmUnit }}）</span>
          </div>
          <BarChart :items="measChartItems" :unit="cmUnit" color="#0CD8A0" />
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import BarChart from '@/components/BarChart.vue'
import { saveBodyRecord } from '@/api'
import { dispValue, cmUnitLabel, cmField } from '@/utils/units'
import { ensureLogin } from '@/utils/authGuard'
import type { Unit } from '@/utils/units'

const visible = defineModel<boolean>('visible', { default: false })

const props = defineProps<{
  records: any[]
  unit: Unit
}>()

const emit = defineEmits<{
  (e: 'saved'): void
}>()

const chestCm = ref<number | null>(null)
const shoulderCm = ref<number | null>(null)
const measWaistCm = ref<number | null>(null)
const measHipCm = ref<number | null>(null)
const thighCm = ref<number | null>(null)
const armCm = ref<number | null>(null)
const measChartMetric = ref('chest_cm')

const cmUnit = computed(() => cmUnitLabel(props.unit))

const measurementFields = computed(() => [
  { key: 'chest_cm', label: '胸围', model: cmField(() => props.unit, chestCm) },
  { key: 'shoulder_cm', label: '肩宽', model: cmField(() => props.unit, shoulderCm) },
  { key: 'waist_cm', label: '腰围', model: cmField(() => props.unit, measWaistCm) },
  { key: 'hip_cm', label: '臀围', model: cmField(() => props.unit, measHipCm) },
  { key: 'thigh_cm', label: '大腿围', model: cmField(() => props.unit, thighCm) },
  { key: 'arm_cm', label: '手臂围', model: cmField(() => props.unit, armCm) },
])

const measChartItems = computed(() => {
  const key = measChartMetric.value
  const list = [...props.records]
    .filter((r) => r[key] != null)
    .sort((a, b) => (a.record_date < b.record_date ? -1 : 1))
    .slice(-12)
    .map((r) => ({
      label: r.record_date.slice(5),
      value: dispValue(props.unit, key, r[key]) as number,
    }))
  return list
})

async function saveMeasurements() {
  const payload: any = {
    record_date: new Date().toISOString().slice(0, 10),
    chest_cm: chestCm.value,
    shoulder_cm: shoulderCm.value,
    waist_cm: measWaistCm.value,
    hip_cm: measHipCm.value,
    thigh_cm: thighCm.value,
    arm_cm: armCm.value,
  }
  const hasAny = [chestCm.value, shoulderCm.value, measWaistCm.value, measHipCm.value, thighCm.value, armCm.value].some((v) => v != null)
  if (!hasAny) {
    ElMessage.warning('请至少填写一项围度')
    return
  }
  if (!ensureLogin('请先登录后再保存围度')) return
  try {
    await saveBodyRecord(payload)
    ElMessage.success('围度已保存')
    clearMeasurements()
    emit('saved')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

function clearMeasurements() {
  chestCm.value = null
  shoulderCm.value = null
  measWaistCm.value = null
  measHipCm.value = null
  thighCm.value = null
  armCm.value = null
}
</script>

<style scoped>
.entry-dialog .measurements__layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; align-items: start; }
.entry-dialog .measurements__form { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.entry-dialog .measurements__grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.measurement-field label { display: block; font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; margin-bottom: 6px; }
.entry-dialog .measurements__actions { display: flex; align-items: center; gap: 12px; margin-top: 20px; }
.btn-text { background: none; border: none; color: var(--clr-gray); font-size: 13px; letter-spacing: 1px; cursor: pointer; padding: 8px 4px; transition: var(--transition-default); }
.btn-text:hover { color: var(--clr-gold-dark); }
.entry-dialog .measurements__chart { background: var(--clr-bg-dark); border: 1px solid rgba(255, 255, 255, 0.06); padding: 18px; }
.measurements__chart-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; gap: 12px; flex-wrap: wrap; }
.measurements__chart-hint { font-size: 12px; color: var(--clr-gray); }

@media (max-width: 1024px) {
  .entry-dialog .measurements__layout { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .entry-dialog .measurements__grid { grid-template-columns: 1fr; }
}
</style>
