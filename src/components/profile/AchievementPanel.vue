<template>
  <div class="ach-panel">
    <!-- ============ 汇总 ============ -->
    <div class="ach-summary">
      <div class="ach-summary__head">
        <div>
          <p class="ach-summary__label">ACHIEVEMENTS</p>
          <h3 class="ach-summary__title">
            已解锁 <b>{{ data.summary.unlocked }}</b> / {{ data.summary.total }}
          </h3>
        </div>
        <div class="ach-summary__tiers">
          <span class="ach-tier ach-tier--gold">金 {{ data.summary.gold }}</span>
          <span class="ach-tier ach-tier--silver">银 {{ data.summary.silver }}</span>
          <span class="ach-tier ach-tier--bronze">铜 {{ data.summary.bronze }}</span>
        </div>
      </div>
      <div class="ach-summary__bar">
        <span class="ach-summary__fill" :style="{ width: pct(data.summary.completion) }"></span>
      </div>
      <p v-if="data.summary.next" class="ach-summary__next">
        离「{{ data.summary.next.name }}」还差
        <b>{{ gapText(data.summary.next) }}</b>
      </p>
      <p v-else-if="data.summary.total" class="ach-summary__next">全部成就已解锁，没什么能拦住你了。</p>
    </div>

    <!-- ============ 分类筛选 ============ -->
    <div class="ach-filter">
      <button
        v-for="f in filters"
        :key="f.value"
        class="ach-filter__btn"
        :class="{ 'is-active': active === f.value }"
        @click="active = f.value"
      >
        {{ f.label }}
        <span class="ach-filter__count">{{ countOf(f.value) }}</span>
      </button>
    </div>

    <!-- ============ 勋章网格 ============ -->
    <div v-if="loading" class="ach-empty">加载中…</div>
    <div v-else-if="!visible.length" class="ach-empty">这个分类下还没有成就。</div>
    <div v-else class="ach-grid">
      <div
        v-for="a in visible"
        :key="a.key"
        class="ach-card"
        :class="[`ach-card--${a.tier}`, { 'is-locked': !a.unlocked }]"
      >
        <div class="ach-card__badge">
          <el-icon :size="22"><component :is="a.icon" /></el-icon>
        </div>
        <div class="ach-card__body">
          <h4 class="ach-card__name">
            {{ a.name }}
            <el-icon v-if="a.unlocked" class="ach-card__check"><CircleCheck /></el-icon>
          </h4>
          <p class="ach-card__desc">{{ a.desc }}</p>
          <div class="ach-card__bar">
            <span :style="{ width: pct(a.progress) }"></span>
          </div>
          <p class="ach-card__progress">
            {{ fmtCurrent(a) }} / {{ formatTarget(a) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAchievements, type AchievementData, type AchievementItem } from '@/api'

const loading = ref(true)
const active = ref<'all' | 'training' | 'streak' | 'body'>('all')
const data = ref<AchievementData>({
  items: [],
  summary: { unlocked: 0, total: 0, completion: 0, gold: 0, silver: 0, bronze: 0, by_category: {}, next: null },
  stats: {},
})

const filters = [
  { value: 'all' as const, label: '全部' },
  { value: 'training' as const, label: '训练' },
  { value: 'streak' as const, label: '坚持' },
  { value: 'body' as const, label: '身材' },
]

const visible = computed(() =>
  active.value === 'all' ? data.value.items : data.value.items.filter((i) => i.category === active.value),
)

const pct = (v: number) => `${Math.round((v || 0) * 100)}%`

function countOf(value: string) {
  const items = data.value.items
  if (value === 'all') return `${data.value.summary.unlocked}/${items.length}`
  const c = data.value.summary.by_category?.[value]
  return c ? `${c.unlocked}/${c.total}` : '0/0'
}

/** 重量类成就用 kg，数字太大时换算成吨更易读 */
function fmtCurrent(a: AchievementItem) {
  if (a.unit === 'kg' && a.metric !== 'exercise_kinds' && a.current >= 10000) {
    return `${(a.current / 1000).toFixed(1)}t`
  }
  return `${a.current}${a.unit}`
}

function formatTarget(a: AchievementItem) {
  if (a.unit === 'kg' && a.metric !== 'exercise_kinds' && a.target >= 10000) {
    return `${(a.target / 1000).toFixed(0)}t`
  }
  return `${a.target}${a.unit}`
}

function gapText(a: AchievementItem) {
  const gap = Math.max(0, a.target - a.current)
  if (a.unit === 'kg' && gap >= 10000) return `${(gap / 1000).toFixed(1)} 吨容量`
  return `${gap}${a.unit}`
}

async function load() {
  loading.value = true
  try {
    const res = await getAchievements()
    data.value = res.data
  } catch (e: any) {
    ElMessage.error(e?.message || '成就加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.ach-panel { display: flex; flex-direction: column; gap: 20px; }

.ach-summary { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 24px 26px; }
.ach-summary__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.ach-summary__label { font-size: 10px; letter-spacing: 3px; color: var(--clr-gold); margin-bottom: 6px; }
.ach-summary__title { font-size: 17px; font-weight: 500; color: var(--clr-dark); }
.ach-summary__title b { font-family: var(--font-display); font-size: 24px; color: var(--clr-gold-dark); }
.ach-summary__tiers { display: flex; gap: 8px; }
.ach-tier { font-size: 12px; padding: 3px 10px; border-radius: 999px; border: 1px solid currentColor; }
.ach-tier--gold { color: #8a6d1f; }
.ach-tier--silver { color: #6b7681; }
.ach-tier--bronze { color: #9c6b45; }
.ach-summary__bar { height: 8px; background: rgba(12, 17, 23, 0.06); border-radius: 999px; margin-top: 18px; overflow: hidden; }
.ach-summary__fill { display: block; height: 100%; background: var(--grad-brand); border-radius: 999px; transition: width 0.8s cubic-bezier(0.22, 0.61, 0.36, 1); }
.ach-summary__next { margin-top: 12px; font-size: 13px; color: var(--clr-gray); }
.ach-summary__next b { color: var(--clr-dark); }

.ach-filter { display: flex; gap: 8px; flex-wrap: wrap; }
.ach-filter__btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 13px;
  color: var(--clr-gray);
  background: var(--clr-white);
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 999px;
  cursor: pointer;
  transition: var(--transition-default);
}
.ach-filter__btn:hover { border-color: rgba(12, 216, 160, 0.45); color: var(--clr-dark); }
.ach-filter__btn.is-active { background: var(--clr-dark); color: #fff; border-color: var(--clr-dark); }
.ach-filter__count { font-size: 11px; opacity: 0.65; }

.ach-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.ach-card {
  display: flex;
  gap: 14px;
  padding: 16px 18px;
  background: var(--clr-white);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: var(--transition-default);
}
.ach-card:hover { transform: translateY(-3px); box-shadow: 0 12px 36px rgba(0, 0, 0, 0.07); }
.ach-card__badge {
  flex: 0 0 44px;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
}
.ach-card--gold .ach-card__badge { background: linear-gradient(135deg, #b6ff3c, #0cd8a0); color: var(--clr-dark); }
.ach-card--silver .ach-card__badge { background: linear-gradient(135deg, #dfe6ea, #97a2ad); color: var(--clr-dark); }
.ach-card--bronze .ach-card__badge { background: linear-gradient(135deg, #e0b48f, #a9714a); }
.ach-card__body { flex: 1; min-width: 0; }
.ach-card__name { display: flex; align-items: center; gap: 6px; font-size: 14px; color: var(--clr-dark); margin-bottom: 4px; }
.ach-card__check { color: var(--clr-gold-dark); }
.ach-card__desc { font-size: 12px; color: var(--clr-gray); line-height: 1.6; margin-bottom: 10px; }
.ach-card__bar { height: 4px; background: rgba(12, 17, 23, 0.07); border-radius: 999px; overflow: hidden; }
.ach-card__bar span { display: block; height: 100%; background: var(--clr-gold); border-radius: 999px; transition: width 0.6s ease; }
.ach-card__progress { margin-top: 6px; font-size: 11px; color: var(--clr-gray-light); }

/* 未解锁：去饱和 + 降低对比，避免和已获得的正反馈抢注意力 */
.ach-card.is-locked { background: var(--clr-bg-section); }
.ach-card.is-locked .ach-card__badge { background: rgba(12, 17, 23, 0.08); color: var(--clr-gray-lighter); }
.ach-card.is-locked .ach-card__name { color: var(--clr-gray); }
.ach-card.is-locked .ach-card__bar span { background: var(--clr-gray-lighter); }

.ach-empty { padding: 40px; text-align: center; color: var(--clr-gray-light); font-size: 13px; background: var(--clr-white); border: 1px dashed rgba(12, 17, 23, 0.1); }

@media (max-width: 900px) {
  .ach-grid { grid-template-columns: 1fr; }
}
</style>
