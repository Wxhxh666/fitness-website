<template>
  <div class="body-chart">
    <svg v-if="items.length" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="xMidYMid meet" class="body-chart__svg">
      <g v-for="(gy, i) in gridY" :key="'grid' + i">
        <line :x1="padL" :y1="gy" :x2="W - padR" :y2="gy" class="body-chart__grid" />
        <text :x="padL - 8" :y="gy + 4" class="body-chart__axis" text-anchor="end">{{ yLabel(i) }}</text>
      </g>

      <g v-for="(b, idx) in bars" :key="'bar' + idx">
        <rect :x="b.x" :y="b.y" :width="b.w" :height="b.h" :fill="color" rx="2" class="body-chart__bar" />
        <text :x="b.x + b.w / 2" :y="b.y - 8" text-anchor="middle" class="body-chart__value">{{ fmt(b.value) }}</text>
        <text :x="b.x + b.w / 2" :y="H - 8" text-anchor="middle" class="body-chart__axis">{{ b.label }}</text>
      </g>
    </svg>
    <div v-else class="body-chart__empty">暂无围度数据，录入一次测量即可生成图表</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  items: { label: string; value: number }[]
  color?: string
  unit?: string
  height?: number
}>(), {
  color: '#c9a96e',
  unit: '',
  height: 240,
})

const W = 800
const padL = 54
const padR = 24
const padT = 30
const padB = 38
const H = props.height
const plotW = W - padL - padR
const plotH = H - padT - padB

const max = computed(() => Math.max(1, ...props.items.map(i => i.value)))

const gridY = computed(() => {
  const rows: number[] = []
  for (let i = 0; i < 4; i++) rows.push(padT + (plotH / 3) * i)
  return rows
})

function yLabel(i: number) {
  return fmt(max.value - (max.value / 3) * i)
}

const bars = computed(() => {
  const n = props.items.length
  const slot = plotW / n
  const w = Math.min(slot * 0.55, 56)
  return props.items.map((it, i) => {
    const h = (it.value / max.value) * plotH
    return {
      x: padL + i * slot + (slot - w) / 2,
      y: padT + plotH - h,
      w,
      h,
      label: it.label,
      value: it.value,
    }
  })
})

function fmt(v: number) {
  const rounded = Math.abs(v) >= 10 ? v.toFixed(0) : v.toFixed(1)
  return `${rounded}${props.unit}`
}
</script>

<style scoped>
.body-chart { width: 100%; }
.body-chart__svg { width: 100%; display: block; }
.body-chart__grid { stroke: rgba(255, 255, 255, 0.08); stroke-width: 1; }
.body-chart__axis { font-size: 11px; fill: var(--clr-gray-light, #9a9a9a); font-family: var(--font-primary); }
.body-chart__bar { transition: opacity 0.25s ease; }
.body-chart__bar:hover { opacity: 0.8; }
.body-chart__value { font-size: 11px; fill: var(--clr-cream, #f5f0e8); font-family: var(--font-primary); }
.body-chart__empty {
  padding: 48px 0;
  text-align: center;
  color: var(--clr-gray-light, #9a9a9a);
  font-size: 13px;
  border: 1px dashed rgba(255, 255, 255, 0.16);
}
</style>
