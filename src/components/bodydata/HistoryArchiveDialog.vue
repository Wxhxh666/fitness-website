<template>
  <el-dialog v-model="visible" title="历史数据存档" width="960px">
    <div class="entry-dialog">
      <div class="history__toolbar">
        <span class="history__hint">共 {{ records.length }} 条记录，选择两条可生成对比小结</span>
        <div class="history__toolbar-spacer"></div>
        <button class="btn-outline-dark" @click="onExport"><el-icon><Download /></el-icon>导出 Excel</button>
        <el-popconfirm title="确认清空全部身材记录？此操作不可恢复。" confirm-button-text="清空" cancel-button-text="取消" @confirm="onClearAll">
          <template #reference>
            <button class="btn-danger-outline">清空全部记录</button>
          </template>
        </el-popconfirm>
      </div>

      <div v-if="compareResult" class="compare-panel compare-panel--light">
        <div class="compare-panel__head">
          <h3 class="compare-panel__title"><el-icon><Switch /></el-icon>数据对比小结</h3>
          <button class="btn-text" @click="clearCompare">关闭</button>
        </div>
        <p class="compare-panel__summary">{{ compareResult.summary }}</p>
        <div class="compare-panel__grid">
          <div v-for="d in compareResult.diffs" :key="d.key" class="compare-item compare-item--light">
            <span class="compare-item__label">{{ d.label }}</span>
            <span class="compare-item__val">{{ fmtDisp(unit, d.key, d.from) }} {{ d.unit }} → {{ fmtDisp(unit, d.key, d.to) }} {{ d.unit }}</span>
            <span class="compare-item__diff" :class="diffClass(d)">{{ d.diff > 0 ? '+' : '' }}{{ d.diff }} {{ d.unit }}</span>
          </div>
        </div>
      </div>

      <el-table :data="records" empty-text="暂无记录，先在上方计算并保存一条吧" style="width: 100%">
        <el-table-column label="日期" width="110">
          <template #default="{ row }">{{ row.record_date }}</template>
        </el-table-column>
        <el-table-column label="阶段" width="80">
          <template #default="{ row }">
            <span v-if="row.stage" class="stage-tag">{{ stageLabel(row.stage) }}</span>
            <span v-else class="stage-tag stage-tag--none">未标注</span>
          </template>
        </el-table-column>
        <el-table-column label="体重" width="100">
          <template #default="{ row }">{{ fmtDisp(unit, 'weight_kg', row.weight_kg) }} {{ weightUnit }}</template>
        </el-table-column>
        <el-table-column label="BMI" width="80">
          <template #default="{ row }">{{ fmtNum(row.bmi) }}</template>
        </el-table-column>
        <el-table-column label="体脂率" width="90">
          <template #default="{ row }">{{ fmtNum(row.body_fat) }}%</template>
        </el-table-column>
        <el-table-column label="肌肉量" width="100">
          <template #default="{ row }">{{ fmtDisp(unit, 'muscle_mass', row.muscle_mass) }} {{ weightUnit }}</template>
        </el-table-column>
        <el-table-column label="TDEE" width="90">
          <template #default="{ row }">{{ fmtNum(row.tdee) }}</template>
        </el-table-column>
        <el-table-column label="操作" min-width="150">
          <template #default="{ row }">
            <button class="table-btn" :class="{ 'table-btn--active': compareSel.includes(row.id) }" @click="toggleCompare(row.id)">
              {{ compareSel.includes(row.id) ? '已选对比' : '对比' }}
            </button>
            <el-popconfirm title="删除这条记录？" confirm-button-text="删除" cancel-button-text="取消" @confirm="onDeleteRecord(row.id)">
              <template #reference>
                <button class="table-btn table-btn--danger">删除</button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  deleteBodyRecord,
  deleteAllBodyRecords,
  compareBodyRecords,
  exportBodyRecords,
} from '@/api'
import { fmtNum, fmtDisp, weightUnitLabel } from '@/utils/units'
import { ensureLogin } from '@/utils/authGuard'
import type { Unit } from '@/utils/units'

const visible = defineModel<boolean>('visible', { default: false })

const props = defineProps<{
  records: any[]
  unit: Unit
}>()

const emit = defineEmits<{
  (e: 'changed'): void
}>()

const compareSel = ref<number[]>([])
const compareResult = ref<any>(null)

const stageOptions = [
  { value: 'fatloss', label: '减脂' },
  { value: 'muscle', label: '增肌' },
  { value: 'maintain', label: '保持' },
]

const weightUnit = computed(() => weightUnitLabel(props.unit))

function stageLabel(stage: string) {
  return stageOptions.find((s) => s.value === stage)?.label || stage
}

async function toggleCompare(id: number) {
  const idx = compareSel.value.indexOf(id)
  if (idx >= 0) {
    compareSel.value.splice(idx, 1)
  } else {
    if (compareSel.value.length >= 2) {
      compareSel.value.shift()
    }
    compareSel.value.push(id)
  }
  compareResult.value = null
  if (compareSel.value.length === 2) {
    try {
      const res = await compareBodyRecords(compareSel.value[0], compareSel.value[1])
      compareResult.value = res.data
    } catch (e: any) {
      ElMessage.error(e?.message || '对比失败')
    }
  }
}

function clearCompare() {
  compareSel.value = []
  compareResult.value = null
}

function diffClass(d: any) {
  const key = d.key
  if (key === 'weight_kg' || key === 'body_fat' || key === 'waist_cm' || key === 'whr') {
    return d.diff < 0 ? 'good' : 'bad'
  }
  return d.diff > 0 ? 'good' : 'bad'
}

async function onDeleteRecord(id: number) {
  if (!ensureLogin('请先登录后再操作')) return
  try {
    await deleteBodyRecord(id)
    ElMessage.success('已删除')
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

async function onClearAll() {
  if (!ensureLogin('请先登录后再操作')) return
  try {
    await deleteAllBodyRecords()
    ElMessage.success('全部记录已清空')
    clearCompare()
    emit('changed')
  } catch (e: any) {
    ElMessage.error(e?.message || '清空失败')
  }
}

async function onExport() {
  if (!ensureLogin('请先登录后再导出')) return
  try {
    const blob = await exportBodyRecords()
    const isCsv = blob.type.includes('csv')
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `身材记录_${new Date().toISOString().slice(0, 10)}.${isCsv ? 'csv' : 'xlsx'}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功，请查收下载文件')
  } catch (e: any) {
    ElMessage.error(e?.message || '导出失败')
  }
}
</script>

<style scoped>
.history__toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; flex-wrap: wrap; }
.history__hint { font-size: 12px; color: var(--clr-gray); }
.history__toolbar-spacer { flex: 1; }
.btn-danger-outline { padding: 9px 18px; background: transparent; color: #b3554a; font-size: 12px; letter-spacing: 2px; border: 1px solid rgba(179, 85, 74, 0.5); cursor: pointer; transition: var(--transition-default); }
.btn-danger-outline:hover { background: rgba(179, 85, 74, 0.08); }
.btn-text { background: none; border: none; color: var(--clr-gray); font-size: 13px; letter-spacing: 1px; cursor: pointer; padding: 8px 4px; transition: var(--transition-default); }
.btn-text:hover { color: var(--clr-gold-dark); }
.compare-panel { margin-top: 16px; background: rgba(12, 216, 160, 0.07); border: 1px solid rgba(12, 216, 160, 0.35); padding: 18px 20px; margin-bottom: 18px; }
.compare-panel--light .compare-panel__title { color: var(--clr-dark); }
.compare-panel--light .compare-panel__summary { color: var(--clr-gray-deep); }
.compare-panel--light .compare-item { background: var(--clr-white); }
.compare-panel--light .compare-item__val { color: var(--clr-dark); }
.compare-panel--light .compare-item__label { color: var(--clr-gray); }
.compare-panel__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.compare-panel__title { font-size: 14px; display: flex; align-items: center; gap: 8px; color: var(--clr-dark); font-weight: 500; }
.compare-panel__summary { font-size: 13px; color: var(--clr-gray-deep); line-height: 1.8; margin-bottom: 14px; }
.compare-panel__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 10px; }
.compare-item { display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); }
.compare-item__label { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.compare-item__val { font-size: 12px; color: var(--clr-dark); }
.compare-item__diff { font-size: 13px; font-weight: 500; }
.compare-item__diff.good { color: #5d8a5d; }
.compare-item__diff.bad { color: #b3554a; }
.stage-tag { font-size: 11px; padding: 2px 8px; border: 1px solid rgba(12, 216, 160, 0.45); color: var(--clr-gold-dark); }
.stage-tag--none { border-color: rgba(0, 0, 0, 0.15); color: var(--clr-gray); }
.table-btn { background: transparent; border: 1px solid rgba(0, 0, 0, 0.2); color: var(--clr-gray-deep); font-size: 12px; padding: 4px 12px; cursor: pointer; margin-right: 8px; transition: var(--transition-default); }
.table-btn:hover { border-color: var(--clr-gold); color: var(--clr-gold-dark); }
.table-btn--active { border-color: var(--clr-gold); color: var(--clr-gold-dark); }
.table-btn--danger { border-color: rgba(179, 85, 74, 0.45); color: #b3554a; }
.table-btn--danger:hover { border-color: #b3554a; color: #b3554a; }
</style>
