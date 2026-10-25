<template>
  <section class="goal-progress section section-light">
    <div class="container">
      <div class="section-header text-center">
        <p class="section-subtitle">GOAL PROGRESS</p>
        <h2 class="section-title">目标达成进度</h2>
        <div class="gold-divider"></div>
        <p class="section-desc">
          {{
            summary.configured
              ? `以 ${summary.startedAt || '设定目标'} 为起点，按最新一次记录计算完成度。`
              : '还没有设定目标。先定一个目标体重或体脂率，这里会持续追踪你的完成度。'
          }}
        </p>
      </div>

      <!-- 未登录 / 未设定目标时的引导 -->
      <div v-if="!authed" class="goal-progress__empty">
        <el-icon :size="28"><Trophy /></el-icon>
        <p>登录后即可设定目标并追踪达成进度。</p>
        <button class="btn-primary" @click="goLogin">去登录</button>
      </div>

      <div v-else-if="!summary.configured" class="goal-progress__empty">
        <el-icon :size="28"><Flag /></el-icon>
        <p>尚未设定目标，设一个能看见的终点，进步才有刻度。</p>
        <router-link class="btn-primary" to="/body-data/records">去设定目标</router-link>
      </div>

      <template v-else>
        <!-- 综合进度 -->
        <div class="goal-progress__overall">
          <div class="goal-progress__bar-wrap">
            <div class="goal-progress__bar">
              <span class="goal-progress__bar-fill" :style="{ width: pct(summary.overall) }"></span>
            </div>
            <div class="goal-progress__bar-meta">
              <span>综合完成度 <b>{{ pct(summary.overall) }}</b></span>
              <span v-if="summary.overall >= 1" class="goal-progress__done">
                <el-icon><Check /></el-icon>全部达成
              </span>
            </div>
          </div>
        </div>

        <!-- 各项目标环形 -->
        <div class="goal-progress__grid">
          <div v-for="m in summary.metrics" :key="m.key" class="goal-ring">
            <svg class="goal-ring__svg" viewBox="0 0 120 120" role="img" :aria-label="`${m.label}进度`">
              <circle class="goal-ring__track" cx="60" cy="60" r="52" />
              <circle
                class="goal-ring__fill"
                :class="{ 'is-reached': m.reached }"
                cx="60"
                cy="60"
                r="52"
                :stroke-dasharray="CIRCUMFERENCE"
                :stroke-dashoffset="dashOffset(m.progress)"
              />
            </svg>
            <div class="goal-ring__center">
              <span class="goal-ring__pct">{{ m.target == null ? '--' : pct(m.progress) }}</span>
              <span class="goal-ring__label">{{ m.label }}</span>
            </div>
            <div class="goal-ring__foot">
              <span class="goal-ring__values">
                <em>{{ m.current == null ? '--' : fmtNum(m.current) }}</em>
                <i>→</i>
                <em>{{ m.target == null ? '--' : fmtNum(m.target) }}{{ m.unit }}</em>
              </span>
              <span v-if="m.reached" class="goal-ring__state done">已达成</span>
              <span v-else-if="m.remaining != null" class="goal-ring__state">
                还差 {{ fmtRemaining(m) }}
              </span>
              <span v-else class="goal-ring__state muted">{{ m.note }}</span>
            </div>
          </div>

          <!-- 每日热量目标：没有起点，做成对比卡 -->
          <div class="goal-ring goal-ring--calorie">
            <div class="goal-ring__icon"><el-icon :size="26"><KnifeFork /></el-icon></div>
            <div class="goal-ring__kcal">
              <span class="goal-ring__kcal-value">{{ summary.dailyCalorie == null ? '--' : Math.round(summary.dailyCalorie) }}</span>
              <span class="goal-ring__kcal-unit">kcal / 日</span>
            </div>
            <p class="goal-ring__kcal-desc">
              <template v-if="summary.dailyCalorie == null">未设定每日摄入目标</template>
              <template v-else-if="summary.latestTdee == null">目标摄入，暂无可对比的消耗数据</template>
              <template v-else>
                当前日消耗 {{ Math.round(summary.latestTdee) }} kcal，{{
                  calorieGapText
                }}
              </template>
            </p>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { fmtNum, type Unit } from '@/utils/units'
import { buildGoalSummary, fmtRemaining } from '@/utils/goal'

const props = defineProps<{
  records: any[]
  goal: any
  unit: Unit
  authed: boolean
}>()

const router = useRouter()
const CIRCUMFERENCE = 2 * Math.PI * 52

const summary = computed(() => buildGoalSummary(props.records, props.goal, props.unit))

const pct = (v: number) => `${Math.round((v || 0) * 100)}%`
const dashOffset = (progress: number) => CIRCUMFERENCE * (1 - Math.min(1, Math.max(0, progress || 0)))

/** 目标摄入 vs 实际消耗：负数=缺口（减脂），正数=盈余（增肌） */
const calorieGapText = computed(() => {
  const { dailyCalorie, latestTdee } = summary.value
  if (dailyCalorie == null || latestTdee == null) return ''
  const gap = Math.round(dailyCalorie - latestTdee)
  if (Math.abs(gap) <= 50) return '基本持平，适合维持体重'
  return gap < 0 ? `每日缺口约 ${Math.abs(gap)} kcal，适合减脂` : `每日盈余约 ${gap} kcal，适合增肌`
})

function goLogin() {
  router.push({ path: '/login', query: { redirect: '/body-data' } })
}
</script>

<style scoped>
.goal-progress { padding: 80px 0; }
.goal-progress__overall { max-width: 720px; margin: 40px auto 0; }
.goal-progress__bar {
  height: 10px;
  background: rgba(12, 17, 23, 0.06);
  border-radius: 999px;
  overflow: hidden;
}
.goal-progress__bar-fill {
  display: block;
  height: 100%;
  background: var(--grad-brand);
  border-radius: 999px;
  transition: width 0.8s cubic-bezier(0.22, 0.61, 0.36, 1);
}
.goal-progress__bar-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  font-size: 13px;
  color: var(--clr-gray);
}
.goal-progress__bar-meta b { color: var(--clr-dark); font-weight: 600; }
.goal-progress__done { display: inline-flex; align-items: center; gap: 4px; color: var(--clr-gold-dark); }

.goal-progress__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 48px;
}
.goal-ring {
  position: relative;
  background: var(--clr-white);
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 28px 20px 22px;
  text-align: center;
  transition: var(--transition-default);
}
.goal-ring:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06); }
.goal-ring__svg { width: 120px; height: 120px; transform: rotate(-90deg); }
.goal-ring__track {
  fill: none;
  stroke: rgba(12, 17, 23, 0.07);
  stroke-width: 8;
}
.goal-ring__fill {
  fill: none;
  stroke: var(--clr-gold);
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.9s cubic-bezier(0.22, 0.61, 0.36, 1);
}
.goal-ring__fill.is-reached { stroke: var(--clr-volt); }
.goal-ring__center {
  position: absolute;
  top: 28px;
  left: 0;
  right: 0;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  pointer-events: none;
}
.goal-ring__pct { font-family: var(--font-display); font-size: 26px; color: var(--clr-dark); }
.goal-ring__label { font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; }
.goal-ring__foot { margin-top: 14px; display: flex; flex-direction: column; gap: 6px; }
.goal-ring__values { font-size: 13px; color: var(--clr-gray); }
.goal-ring__values em { font-style: normal; color: var(--clr-dark); }
.goal-ring__values i { font-style: normal; margin: 0 5px; color: var(--clr-gray-lighter); }
.goal-ring__state { font-size: 12px; color: var(--clr-gray-light); }
.goal-ring__state.done { color: var(--clr-gold-dark); }
.goal-ring__state.muted { color: var(--clr-gray-lighter); }

.goal-ring--calorie { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; }
.goal-ring__icon { color: var(--clr-gold); }
.goal-ring__kcal { display: flex; align-items: baseline; gap: 4px; }
.goal-ring__kcal-value { font-family: var(--font-display); font-size: 30px; color: var(--clr-dark); }
.goal-ring__kcal-unit { font-size: 12px; color: var(--clr-gray); }
.goal-ring__kcal-desc { font-size: 12px; color: var(--clr-gray-light); line-height: 1.7; }

.goal-progress__empty {
  margin-top: 48px;
  padding: 48px 24px;
  text-align: center;
  background: var(--clr-white);
  border: 1px dashed rgba(12, 17, 23, 0.12);
  color: var(--clr-gray);
}
.goal-progress__empty :deep(.el-icon) { color: var(--clr-gold); margin-bottom: 12px; }
.goal-progress__empty p { margin-bottom: 18px; font-size: 14px; }
.goal-progress__empty .btn-primary { display: inline-flex; align-items: center; }

@media (max-width: 1024px) {
  .goal-progress__grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .goal-progress__grid { grid-template-columns: 1fr; }
}
</style>
