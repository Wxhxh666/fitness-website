<template>
  <section class="metrics section section-white">
    <div class="container">
      <div class="section-header text-center">
        <p class="section-subtitle">KEY METRICS</p>
        <h2 class="section-title">身体核心指标总览</h2>
        <div class="gold-divider"></div>
      </div>
      <div class="metrics__grid">
        <div v-for="(m, idx) in metrics" :key="idx" class="metric-card">
          <div class="metric-card__icon"><el-icon :size="24"><component :is="m.icon" /></el-icon></div>
          <div class="metric-card__info"><span class="metric-card__value">{{ m.value }}</span><span class="metric-card__unit">{{ m.unit }}</span></div>
          <span class="metric-card__label">{{ m.label }}</span>
          <div v-if="m.change !== null" class="metric-card__trend" :class="m.trendClass">
            <el-icon><component :is="m.trendClass === 'up' ? 'Top' : 'Bottom'" /></el-icon>{{ m.change }}
          </div>
          <div v-else class="metric-card__trend muted">较上次 --</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  metrics: any[]
}>()
</script>

<style scoped>
.metrics { padding: 80px 0; }
.metrics__grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 48px; }
.metric-card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 32px 24px; text-align: center; transition: var(--transition-default); }
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06); }
.metric-card__icon { margin-bottom: 16px; color: var(--clr-gold); }
.metric-card__info { display: flex; align-items: baseline; justify-content: center; gap: 4px; margin-bottom: 4px; }
.metric-card__value { font-family: var(--font-display); font-size: 32px; color: var(--clr-dark); }
.metric-card__unit { font-size: 14px; color: var(--clr-gray); }
.metric-card__label { font-size: 13px; color: var(--clr-gray); letter-spacing: 1px; }
.metric-card__trend { margin-top: 12px; font-size: 12px; display: flex; align-items: center; justify-content: center; gap: 4px; }
.metric-card__trend.up { color: #6b8e6b; }
.metric-card__trend.down { color: #888; }
.metric-card__trend.muted { color: var(--clr-gray-light); }

@media (max-width: 1024px) {
  .metrics__grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .metrics__grid { grid-template-columns: 1fr; }
}
</style>
