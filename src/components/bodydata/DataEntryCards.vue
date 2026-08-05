<template>
  <section class="data-entry section section-white">
    <div class="container">
      <div class="section-header text-center">
        <p class="section-subtitle">DATA MANAGEMENT</p>
        <h2 class="section-title">数据管理入口</h2>
        <div class="gold-divider"></div>
        <p class="section-desc">围度记录、身材目标管理、历史数据存档，三个入口集中管理你的全部身体数据。</p>
      </div>
      <div class="data-entry__grid">
        <div class="data-entry__card" @click="emit('open-measurements')">
          <div class="data-entry__icon"><el-icon :size="28"><Ruler /></el-icon></div>
          <h3 class="data-entry__title">围度记录</h3>
          <p class="data-entry__desc">胸围、肩宽、腰围、臀围、大腿围、手臂围测量存档与变化柱状图。</p>
          <span class="data-entry__meta">最近测量：{{ measLatestText }}</span>
          <button class="btn-outline-dark data-entry__btn">进入围度管理</button>
        </div>
        <div class="data-entry__card" @click="emit('open-goals')">
          <div class="data-entry__icon"><el-icon :size="28"><Flag /></el-icon></div>
          <h3 class="data-entry__title">身材目标管理</h3>
          <p class="data-entry__desc">目标体重 / BMI / 体脂率设定，结合 TDEE 推算热量缺口与达成天数。</p>
          <span class="data-entry__meta">{{ goal ? '目标已设定，进度随时可查' : '尚未设定目标' }}</span>
          <button class="btn-outline-dark data-entry__btn">进入目标管理</button>
        </div>
        <div class="data-entry__card" @click="emit('open-history')">
          <div class="data-entry__icon"><el-icon :size="28"><Files /></el-icon></div>
          <h3 class="data-entry__title">历史数据存档</h3>
          <p class="data-entry__desc">全部身材记录表格、两条记录对比小结与 Excel 一键导出。</p>
          <span class="data-entry__meta">共 {{ recordCount }} 条记录</span>
          <button class="btn-outline-dark data-entry__btn">进入数据存档</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  measLatestText: string
  goal: any
  recordCount: number
}>()

const emit = defineEmits<{
  (e: 'open-measurements'): void
  (e: 'open-goals'): void
  (e: 'open-history'): void
}>()
</script>

<style scoped>
.data-entry { padding: 100px 0; }
.data-entry__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 56px; }
.data-entry__card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.06); padding: 40px 30px; text-align: center; cursor: pointer; transition: var(--transition-default); }
.data-entry__card:hover { transform: translateY(-5px); box-shadow: 0 14px 44px rgba(0, 0, 0, 0.08); border-color: rgba(201, 169, 110, 0.4); }
.data-entry__icon { color: var(--clr-gold); margin-bottom: 18px; }
.data-entry__title { font-family: var(--font-display); font-size: 20px; font-weight: 400; margin-bottom: 12px; color: var(--clr-dark); }
.data-entry__desc { font-size: 13px; color: var(--clr-gray); line-height: 1.8; margin-bottom: 16px; min-height: 48px; }
.data-entry__meta { display: inline-block; font-size: 12px; color: var(--clr-gray-light); margin-bottom: 18px; }
.data-entry__btn { width: 100%; justify-content: center; }

@media (max-width: 1024px) {
  .data-entry__grid { grid-template-columns: 1fr; }
}
</style>
