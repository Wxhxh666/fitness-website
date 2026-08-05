<template>
  <div class="p-card fade-in">
    <h3 class="p-card__title"><el-icon><DataAnalysis /></el-icon>健身数据仪表盘</h3>

    <!-- 统计数字：金色高亮 -->
    <div class="dash-stats">
      <div class="dash-stat">
        <span class="dash-stat__label">测量次数</span>
        <span class="stat-value">{{ stats.measurements }}</span>
      </div>
      <div class="dash-stat">
        <span class="dash-stat__label">食谱数量</span>
        <span class="stat-value">{{ stats.diet_plans }}</span>
      </div>
      <div class="dash-stat">
        <span class="dash-stat__label">训练计划数</span>
        <span class="stat-value">{{ stats.plans }}</span>
      </div>
      <div class="dash-stat">
        <span class="dash-stat__label">打卡天数</span>
        <span class="stat-value">{{ stats.checkin_days }}</span>
      </div>
    </div>

    <!-- 近30天体重迷你折线图（ECharts） -->
    <div class="dash-chart">
      <div class="dash-chart__head">
        <span class="dash-chart__title">近 30 天体重趋势</span>
        <span v-if="!weightSeries.length" class="dash-chart__empty">暂无体重记录，去身材管理页添加一条吧</span>
      </div>
      <div ref="chartEl" class="dash-chart__el"></div>
    </div>

    <!-- 快捷跳转 -->
    <div class="dash-actions">
      <button class="btn-primary" @click="go('/body-data')"><el-icon><TrendCharts /></el-icon>身材管理</button>
      <button class="btn-outline" @click="go('/body-data')"><el-icon><Bowl /></el-icon>AI 饮食规划</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { init, use, type ECharts } from 'echarts/core'
import { LineChart as ELineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ElMessage } from 'element-plus'
import { getDashboardStats } from '@/api'

// 按需注册 ECharts 模块，减小打包体积
use([ELineChart, GridComponent, TooltipComponent, CanvasRenderer])

const router = useRouter()
const stats = ref({ measurements: 0, diet_plans: 0, plans: 0, checkin_days: 0 })
const weightSeries = ref<{ date: string; weight_kg: number }[]>([])
const chartEl = ref<HTMLDivElement | null>(null)
let chart: ECharts | null = null

async function loadStats() {
  try {
    const res = await getDashboardStats()
    stats.value = res.data.stats
    weightSeries.value = res.data.weight_series || []
    await nextTick()
    renderChart()
  } catch (e: any) {
    ElMessage.error(e?.message || '统计数据加载失败')
  }
}

function renderChart() {
  if (!chartEl.value) return
  if (!chart) chart = init(chartEl.value)
  chart.setOption({
    grid: { left: 44, right: 18, top: 24, bottom: 26 },
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: 'rgba(184,156,102,0.35)', textStyle: { color: '#333' } },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: weightSeries.value.map((p) => p.date.slice(5)),
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#999', fontSize: 11 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
      axisLabel: { color: '#999', fontSize: 11 },
    },
    series: [
      {
        name: '体重(kg)',
        type: 'line',
        data: weightSeries.value.map((p) => p.weight_kg),
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { color: '#B89C66', width: 2 },
        itemStyle: { color: '#B89C66' },
        areaStyle: { color: 'rgba(184,156,102,0.12)' },
      },
    ],
  })
}

function onResize() {
  chart?.resize()
}

function go(path: string) {
  router.push(path)
}

watch(weightSeries, () => renderChart())

onMounted(() => {
  loadStats()
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.dash-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 22px; }
.dash-stat {
  background: #FBF8F2;
  border: 1px solid rgba(184, 156, 102, 0.18);
  border-radius: 10px;
  padding: 18px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: center;
}
.dash-stat__label { font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; }
.dash-chart { border: 1px solid rgba(184, 156, 102, 0.16); border-radius: 10px; padding: 16px; margin-bottom: 22px; }
.dash-chart__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.dash-chart__title { font-size: 13px; font-weight: 500; color: var(--clr-dark); }
.dash-chart__empty { font-size: 12px; color: var(--clr-gray-light); }
.dash-chart__el { height: 220px; width: 100%; }
.dash-actions { display: flex; gap: 12px; }

@media (max-width: 768px) {
  .dash-stats { grid-template-columns: repeat(2, 1fr); }
}
</style>
