<template>
  <div class="body-chart">
    <svg v-if="items.length" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="xMidYMid meet" class="body-chart__svg">
      <g v-for="(gy, i) in gridY" :key="'grid' + i">
        <line :x1="padL" :y1="gy" :x2="W - padR" :y2="gy" class="body-chart__grid" />
        <text :x="padL - 8" :y="gy + 4" class="body-chart__axis" text-anchor="end">{{ yLabel(i) }}</text>
      </g>

      <polyline v-if="areaPoints.length > 1" :points="areaPoints" class="body-chart__area" />
      <polyline v-if="polyPoints.length > 1" :points="polyPoints" class="body-chart__line" :style="{ stroke: color }" />

      <g v-for="(p, idx) in chartPoints" :key="'dot' + idx">
        <circle :cx="p.x" :cy="p.y" r="4" :fill="color" class="body-chart__dot" />
        <text v-if="showValues" :x="p.x" :y="p.y - 12" class="body-chart__value" text-anchor="middle">
          {{ fmt(p.value) }}
        </text>
        <g v-if="p.marker" class="body-chart__marker">
          <line :x1="p.x" :y1="p.y + 7" :x2="p.x" :y2="p.y + 16" stroke="#c0392b" stroke-width="1" />
          <rect :x="p.x - 20" :y="p.y - 44" width="40" height="18" rx="2" fill="#c0392b" />
          <text :x="p.x" :y="p.y - 31" text-anchor="middle" class="body-chart__marker-text">{{ p.marker }}</text>
        </g>
      </g>

      <text v-for="t in xTicks" :key="'x' + t.idx" :x="t.x" :y="H - 8" class="body-chart__axis" text-anchor="middle">{{ t.label }}</text>
    </svg>
    <div v-else class="body-chart__empty">暂无数据，先保存一条记录即可看到趋势</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  items: { label: string; value: number; marker?: string }[]
  color?: string
  unit?: string
  showValues?: boolean
  height?: number
}>(), {
  color: '#c9a96e',
  unit: '',
  showValues: false,
  height: 260,
})

const W = 800
const padL = 54
const padR = 24
const padT = 30
const padB = 36
const H = props.height
const plotW = W - padL - padR
const plotH = H - padT - padB

const nums = computed(() => props.items.map(i => i.value))
const min = computed(() => Math.min(...nums.value))
const max = computed(() => Math.max(...nums.value))
const span = computed(() => (max.value - min.value) || 1)

function xAt(i: number) {
  const n = props.items.length
  return n > 1 ? padL + (i / (n - 1)) * plotW : padL + plotW / 2
}
function yAt(v: number) {
  return padT + (1 - (v - min.value) / span.value) * plotH
}

const chartPoints = computed(() =>
  props.items.map((it, i) => ({
    x: xAt(i),
    y: yAt(it.value),
    value: it.value,
    marker: it.marker || '',
  }))
)

const polyPoints = computed(() => chartPoints.value.map(p => `${p.x},${p.y}`).join(' '))
const areaPoints = computed(() => {
  if (!chartPoints.value.length) return ''
  const first = chartPoints.value[0]
  const last = chartPoints.value[chartPoints.value.length - 1]
  return `${first.x},${padT + plotH} ${polyPoints.value} ${last.x},${padT + plotH}`
})

const gridY = computed(() => {
  const rows: number[] = []
  for (let i = 0; i < 4; i++) rows.push(padT + (plotH / 3) * i)
  return rows
})

function yLabel(i: number) {
  const v = max.value - (span.value / 3) * i
  return fmt(v)
}

const xTicks = computed(() => {
  const n = props.items.length
  const step = Math.max(1, Math.ceil(n / 6))
  const out: { idx: number; x: number; label: string }[] = []
  for (let i = 0; i < n; i += step) {
    out.push({ idx: i, x: xAt(i), label: props.items[i].label })
  }
  if (out[out.length - 1]?.idx !== n - 1) {
    out.push({ idx: n - 1, x: xAt(n - 1), label: props.items[n - 1].label })
  }
  return out
})

function fmt(v: number) {
  const rounded = Math.abs(v) >= 10 ? v.toFixed(0) : v.toFixed(1)
  return `${rounded}${props.unit}`
}
</script>

<style scoped>
.body-chart { width: 100%; }
.body-chart__svg { width: 100%; display: block; }
.body-chart__grid { stroke: rgba(0, 0, 0, 0.07); stroke-width: 1; }
.body-chart__axis { font-size: 11px; fill: var(--clr-gray-light, #9a9a9a); font-family: var(--font-primary); }
.body-chart__area { fill: rgba(201, 169, 110, 0.12); stroke: none; }
.body-chart__line { fill: none; stroke-width: 2; }
.body-chart__dot { stroke: var(--clr-white, #fff); stroke-width: 2; }
.body-chart__value { font-size: 11px; fill: var(--clr-dark, #111); font-family: var(--font-primary); }
.body-chart__marker-text { font-size: 10px; fill: #fff; font-family: var(--font-primary); }
.body-chart__empty {
  padding: 56px 0;
  text-align: center;
  color: var(--clr-gray-light, #9a9a9a);
  font-size: 13px;
  border: 1px dashed rgba(0, 0, 0, 0.12);
}
</style>
