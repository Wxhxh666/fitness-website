<template>
  <div class="workouts-view">
    <PageHero
      label="TRAINING LOG"
      title="运动记录"
      desc="逐组记录重量与次数，自动算出训练容量、估算 1RM 与个人纪录，让渐进超负荷看得见。"
    />

    <section class="wo-section">
      <div class="container">
        <!-- ============ 概览 ============ -->
        <div class="wo-stats">
          <div class="wo-stat">
            <div class="wo-stat__label">本周训练</div>
            <div class="wo-stat__value">
              {{ overview?.week.sessions ?? 0 }}<span class="wo-stat__unit">/ 4 次</span>
            </div>
            <div class="wo-stat__bar">
              <i :style="{ width: Math.min(((overview?.week.sessions ?? 0) / 4) * 100, 100) + '%' }"></i>
            </div>
          </div>
          <div class="wo-stat">
            <div class="wo-stat__label">本周容量</div>
            <div class="wo-stat__value">{{ fmt(overview?.week.volume) }}<span class="wo-stat__unit">kg</span></div>
            <div class="wo-stat__hint">{{ overview?.week.sets ?? 0 }} 组 · {{ overview?.week.reps ?? 0 }} 次</div>
          </div>
          <div class="wo-stat">
            <div class="wo-stat__label">连续训练</div>
            <div class="wo-stat__value">{{ overview?.current_streak ?? 0 }}<span class="wo-stat__unit">天</span></div>
            <div class="wo-stat__hint">最长 {{ overview?.longest_streak ?? 0 }} 天</div>
          </div>
          <div class="wo-stat">
            <div class="wo-stat__label">本月时长</div>
            <div class="wo-stat__value">{{ overview?.month.minutes ?? 0 }}<span class="wo-stat__unit">分钟</span></div>
            <div class="wo-stat__hint">平均 {{ overview?.month.avg_duration ?? 0 }} 分钟 / 次</div>
          </div>
        </div>

        <div class="wo-layout">
          <!-- ============ 左：今日记录 ============ -->
          <div class="wo-main">
            <div class="wo-card">
              <div class="wo-card__head">
                <div>
                  <div class="wo-card__label">CURRENT SESSION</div>
                  <h3 class="wo-card__title">
                    <template v-if="active">
                      {{ active.session_date === today ? '今日训练' : active.session_date }}
                    </template>
                    <template v-else>今天还没开始训练</template>
                  </h3>
                </div>
                <div class="wo-card__actions">
                  <el-button v-if="!active" type="primary" :loading="starting" @click="startToday">
                    <el-icon><Plus /></el-icon> 开始今日训练
                  </el-button>
                  <template v-else>
                    <el-button text @click="finishSession">结束训练</el-button>
                  </template>
                </div>
              </div>

              <!-- 空态 -->
              <div v-if="!active" class="wo-empty">
                <div class="wo-empty__icon"><el-icon :size="34"><Timer /></el-icon></div>
                <p>开始一次训练后，就能逐组记录重量和次数。</p>
                <p class="wo-empty__sub">只做简单打卡？在「计划制定」里点完成打卡也会自动记一次训练。</p>
              </div>

              <template v-else>
                <!-- 会话信息 -->
                <div class="wo-meta">
                  <el-input v-model="active.title" placeholder="训练标题，如 胸部训练" maxlength="64"
                            class="wo-meta__title" @change="saveSessionMeta" />
                  <div class="wo-meta__fields">
                    <label>时长</label>
                    <el-input-number v-model="active.duration_min" :min="0" :max="600" :step="5"
                                     size="small" controls-position="right" @change="saveSessionMeta" />
                    <span class="wo-meta__unit">分钟</span>
                    <label class="wo-meta__gap">感受</label>
                    <el-rate v-model="active.feeling" :max="5" @change="saveSessionMeta" />
                  </div>
                </div>

                <!-- 已记录的组 -->
                <div v-if="active.groups.length" class="wo-groups">
                  <div v-for="g in active.groups" :key="g.exercise_name" class="wo-group">
                    <div class="wo-group__head">
                      <span class="wo-group__name">{{ g.exercise_name }}</span>
                      <span class="wo-group__sum">
                        {{ g.sets.length }} 组 · {{ fmt(g.total_volume) }} kg
                        <em v-if="g.best_e1rm">最佳 e1RM {{ g.best_e1rm }}kg</em>
                      </span>
                    </div>
                    <div class="wo-group__rows">
                      <div v-for="(s, i) in g.sets" :key="s.id"
                           :class="['wo-set', { 'is-warmup': s.is_warmup }]">
                        <span class="wo-set__idx">{{ s.is_warmup ? '热' : i + 1 }}</span>
                        <span class="wo-set__main">
                          <b>{{ s.weight_kg || 0 }}</b> kg × <b>{{ s.reps }}</b>
                        </span>
                        <span class="wo-set__rpe" v-if="s.rpe">RPE {{ s.rpe }}</span>
                        <span class="wo-set__vol">{{ s.is_warmup ? '热身' : fmt(s.volume) + ' kg' }}</span>
                        <button class="wo-set__del" title="删除这组" @click="removeSet(s.id)">
                          <el-icon><Close /></el-icon>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="wo-empty wo-empty--small">
                  还没有记录任何组，用下面的输入框开始吧。
                </div>

                <!-- 快速录入 -->
                <div class="wo-add">
                  <el-autocomplete
                    v-model="form.exercise_name"
                    :fetch-suggestions="suggestExercises"
                    placeholder="动作名称，如 杠铃卧推"
                    class="wo-add__name"
                    clearable
                    @select="onPickExercise"
                  >
                    <template #default="{ item }">
                      <div class="wo-suggest">
                        <span>{{ item.exercise_name }}</span>
                        <small v-if="item.last_weight_kg">上次 {{ item.last_weight_kg }}kg × {{ item.last_reps }}</small>
                      </div>
                    </template>
                  </el-autocomplete>

                  <div class="wo-add__nums">
                    <div class="wo-field">
                      <label>重量 kg</label>
                      <el-input-number v-model="form.weight_kg" :min="0" :max="1000" :step="2.5"
                                       :precision="1" controls-position="right" />
                    </div>
                    <div class="wo-field">
                      <label>次数</label>
                      <el-input-number v-model="form.reps" :min="0" :max="1000" :step="1"
                                       controls-position="right" />
                    </div>
                    <div class="wo-field wo-field--sm">
                      <label>RPE</label>
                      <el-input-number v-model="form.rpe" :min="1" :max="10" :step="0.5"
                                       :precision="1" controls-position="right" />
                    </div>
                    <div class="wo-field wo-field--check">
                      <el-checkbox v-model="form.is_warmup">热身组</el-checkbox>
                    </div>
                    <el-button type="primary" class="wo-add__btn" :loading="adding" @click="submitSet"
                               @keyup.enter="submitSet">
                      记录一组
                    </el-button>
                  </div>
                  <p class="wo-add__tip">
                    提示：填好重量次数后连按回车可连续记录，重量/次数会自动沿用上一次输入。
                  </p>
                </div>

                <div class="wo-card__foot">
                  <span>本次共 {{ active.total_sets }} 组 · {{ active.total_reps }} 次 · {{ fmt(active.total_volume) }} kg</span>
                  <el-button text type="danger" size="small" @click="removeSession">删除这次训练</el-button>
                </div>
              </template>
            </div>

            <!-- ============ 历史 ============ -->
            <div class="wo-card">
              <div class="wo-card__head">
                <div>
                  <div class="wo-card__label">HISTORY</div>
                  <h3 class="wo-card__title">历史训练</h3>
                </div>
                <el-radio-group v-model="historyDays" size="small" @change="loadSessions">
                  <el-radio-button :value="30">30 天</el-radio-button>
                  <el-radio-button :value="90">90 天</el-radio-button>
                  <el-radio-button :value="0">全部</el-radio-button>
                </el-radio-group>
              </div>

              <div v-if="loadingSessions" class="wo-loading">加载中…</div>
              <div v-else-if="!sessions.length" class="wo-empty wo-empty--small">
                还没有历史训练记录。
              </div>
              <div v-else class="wo-history">
                <button v-for="s in sessions" :key="s.id" class="wo-history__row"
                        :class="{ 'is-active': active?.id === s.id }" @click="openSession(s.id)">
                  <span class="wo-history__date">
                    <b>{{ s.session_date.slice(5) }}</b>
                    <small>{{ weekdayOf(s.session_date) }}</small>
                  </span>
                  <span class="wo-history__main">
                    <b>{{ s.title || '训练' }}</b>
                    <small>{{ s.total_sets }} 组 · {{ fmt(s.total_volume) }} kg<span v-if="s.duration_min"> · {{ s.duration_min }} 分钟</span></small>
                  </span>
                  <span class="wo-history__go">查看</span>
                </button>
              </div>
            </div>
          </div>

          <!-- ============ 右：图表 / PR / 日历 ============ -->
          <aside class="wo-side">
            <div class="wo-card">
              <div class="wo-card__head">
                <div>
                  <div class="wo-card__label">VOLUME</div>
                  <h3 class="wo-card__title">周训练容量</h3>
                </div>
                <span class="wo-card__aside">近 12 周</span>
              </div>
              <div ref="chartEl" class="wo-chart"></div>
              <p class="wo-chart__foot">
                容量 = 重量 × 次数（不含热身组）。连续几周往上走，说明渐进超负荷在生效。
              </p>
            </div>

            <div class="wo-card">
              <div class="wo-card__head">
                <div>
                  <div class="wo-card__label">PERSONAL BEST</div>
                  <h3 class="wo-card__title">个人纪录</h3>
                </div>
                <el-icon class="wo-card__badge"><Trophy /></el-icon>
              </div>
              <div v-if="!prs.length" class="wo-empty wo-empty--small">练几次之后，这里会自动出现你的 PR。</div>
              <div v-else class="wo-prs">
                <div v-for="p in prs.slice(0, 8)" :key="p.exercise_name" class="wo-pr">
                  <div class="wo-pr__name">{{ p.exercise_name }}</div>
                  <div class="wo-pr__nums">
                    <span v-if="p.e1rm"><em>e1RM</em>{{ p.e1rm.value }}kg</span>
                    <span v-if="p.max_weight"><em>最大重量</em>{{ p.max_weight.weight_kg }}kg × {{ p.max_weight.reps }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="wo-card">
              <div class="wo-card__head">
                <div>
                  <div class="wo-card__label">CALENDAR</div>
                  <h3 class="wo-card__title">{{ monthLabel }}</h3>
                </div>
                <el-icon class="wo-card__badge"><Calendar /></el-icon>
              </div>
              <div class="wo-cal">
                <span v-for="w in ['一','二','三','四','五','六','日']" :key="w" class="wo-cal__wd">{{ w }}</span>
                <span v-for="c in calendarCells" :key="c.key"
                      :class="['wo-cal__day', { 'is-empty': !c.day, 'is-done': !!c.info, 'is-today': c.iso === today }]"
                      :style="c.info ? { background: heatColor(c.info.volume) } : {}"
                      :title="c.info ? `${c.info.sessions} 次训练 · ${fmt(c.info.volume)} kg` : ''">
                  {{ c.day || '' }}
                </span>
              </div>
              <p class="wo-chart__foot">颜色越深，当天训练容量越大。</p>
            </div>
          </aside>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Close, Timer, Trophy, Calendar } from '@element-plus/icons-vue'
import { init, use, type ECharts } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import PageHero from '@/components/PageHero.vue'
import {
  listWorkoutSessions, createWorkoutSession, getWorkoutSession, updateWorkoutSession,
  deleteWorkoutSession, addWorkoutSets, deleteWorkoutSet,
  getWorkoutOverview, getVolumeSeries, getWorkoutCalendar, getPersonalRecords, getMyExercises,
  type WorkoutSessionItem, type WorkoutGroup, type WorkoutOverview,
} from '@/api'

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

type ActiveSession = WorkoutSessionItem & { groups: WorkoutGroup[] }
interface ExerciseOption { exercise_name: string; last_weight_kg: number; last_reps: number; last_date: string }

const today = new Date().toLocaleDateString('sv-SE') // YYYY-MM-DD，避免时区偏移
const month = ref(today.slice(0, 7))

const loadingSessions = ref(false)
const starting = ref(false)
const adding = ref(false)
const sessions = ref<WorkoutSessionItem[]>([])
const active = ref<ActiveSession | null>(null)
const overview = ref<WorkoutOverview | null>(null)
const myExercises = ref<ExerciseOption[]>([])
const prs = ref<any[]>([])
const weekly = ref<{ week_start: string; volume: number; sets: number }[]>([])
const calDays = ref<{ date: string; sessions: number; volume: number; sets: number }[]>([])
const historyDays = ref(30)

const form = reactive({
  exercise_name: '',
  weight_kg: 20,
  reps: 10,
  rpe: null as number | null,
  is_warmup: false,
})

const monthLabel = computed(() => {
  const [y, m] = month.value.split('-')
  return `${y} 年 ${Number(m)} 月`
})

const calendarCells = computed(() => {
  const [y, m] = month.value.split('-').map(Number)
  const startWeekday = (new Date(y, m - 1, 1).getDay() + 6) % 7 // 周一为一周起点
  const daysInMonth = new Date(y, m, 0).getDate()
  const map = new Map(calDays.value.map((d) => [d.date, d]))
  const cells: { key: string; day: number; iso?: string; info?: any }[] = []
  for (let i = 0; i < startWeekday; i++) cells.push({ key: `pad-${i}`, day: 0 })
  for (let d = 1; d <= daysInMonth; d++) {
    const iso = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cells.push({ key: iso, day: d, iso, info: map.get(iso) })
  }
  return cells
})

const maxCalVolume = computed(() => Math.max(1, ...calDays.value.map((d) => d.volume)))

function heatColor(volume: number) {
  const ratio = Math.min(volume / maxCalVolume.value, 1)
  return `rgba(12, 216, 160, ${0.16 + ratio * 0.66})`
}

function fmt(n?: number | null) {
  if (n === undefined || n === null) return '0'
  return Number(n).toLocaleString('zh-CN', { maximumFractionDigits: 1 })
}

function weekdayOf(iso: string) {
  const names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return names[new Date(iso + 'T00:00:00').getDay()]
}

// ---------------------------------------------------------------- 数据加载
async function loadOverview() {
  try {
    const res = await getWorkoutOverview()
    overview.value = res.data
  } catch { /* 概览失败不阻塞主流程 */ }
}

async function loadSessions() {
  loadingSessions.value = true
  try {
    const params: any = { limit: 60 }
    if (historyDays.value) params.days = historyDays.value
    const res = await listWorkoutSessions(params)
    sessions.value = res.data.items
    // 首次进入时，把今天（或最近一次）的训练作为当前编辑对象
    if (!active.value && sessions.value.length) {
      const latest = sessions.value[0]
      if (latest.session_date === today) await openSession(latest.id, false)
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '加载训练记录失败')
  } finally {
    loadingSessions.value = false
  }
}

async function loadSide() {
  try {
    const [ex, pr, vol, cal] = await Promise.all([
      getMyExercises(), getPersonalRecords(), getVolumeSeries(12), getWorkoutCalendar(month.value),
    ])
    myExercises.value = ex.data.items
    prs.value = pr.data.items
    weekly.value = vol.data.items
    calDays.value = cal.data.days
    await nextTick()
    renderChart()
  } catch { /* 侧栏数据失败不影响记录 */ }
}

async function openSession(id: number, scroll = true) {
  try {
    const res = await getWorkoutSession(id)
    active.value = res.data
    if (scroll) window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e: any) {
    ElMessage.error(e?.message || '打开训练失败')
  }
}

async function startToday() {
  starting.value = true
  try {
    const res = await createWorkoutSession({ session_date: today, title: '今日训练' })
    await openSession(res.data.id, false)
    await loadSessions()
  } catch (e: any) {
    ElMessage.error(e?.message || '创建训练失败')
  } finally {
    starting.value = false
  }
}

async function finishSession() {
  if (!active.value) return
  try {
    await updateWorkoutSession(active.value.id, { duration_min: active.value.duration_min })
    ElMessage.success('已保存本次训练')
    await Promise.all([loadOverview(), loadSide(), loadSessions()])
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

async function saveSessionMeta() {
  if (!active.value) return
  try {
    await updateWorkoutSession(active.value.id, {
      title: active.value.title,
      duration_min: active.value.duration_min,
      feeling: active.value.feeling,
    })
    const target = sessions.value.find((s) => s.id === active.value!.id)
    if (target) {
      target.title = active.value.title
      target.duration_min = active.value.duration_min
    }
  } catch (e: any) {
    ElMessage.warning(e?.message || '保存失败')
  }
}

function suggestExercises(query: string, cb: (items: ExerciseOption[]) => void) {
  const q = (query || '').trim().toLowerCase()
  const list = myExercises.value.filter((e) => !q || e.exercise_name.toLowerCase().includes(q))
  cb(list.slice(0, 8))
}

function onPickExercise(item: ExerciseOption) {
  if (item.last_weight_kg) form.weight_kg = item.last_weight_kg
  if (item.last_reps) form.reps = item.last_reps
}

async function submitSet() {
  if (!active.value) return
  const name = form.exercise_name.trim()
  if (!name) { ElMessage.warning('请先填写动作名称'); return }
  if (!form.weight_kg && !form.reps) { ElMessage.warning('重量和次数不能同时为 0'); return }

  adding.value = true
  try {
    const res = await addWorkoutSets(active.value.id, {
      exercise_name: name,
      weight_kg: form.weight_kg || 0,
      reps: form.reps || 0,
      rpe: form.rpe ?? null,
      is_warmup: form.is_warmup,
    })
    const data = res.data
    Object.assign(active.value, data.session)
    await openSession(active.value.id, false)

    const records = data.records || []
    const improved = records.filter((r: any) => r.previous_value > 0)
    if (improved.length) {
      const r = improved[0]
      const label: Record<string, string> = { e1rm: '估算 1RM', max_weight: '最大重量', max_reps: '最多次数', max_volume: '单组容量' }
      ElMessage.success(`新纪录！${r.exercise_name} ${label[r.record_type] || r.record_type} ${r.value}`)
    }
    // 重量/次数沿用，方便连续记录；热身标记只对当前组生效
    form.is_warmup = false
    await Promise.all([loadOverview(), loadSide(), loadSessions()])
  } catch (e: any) {
    ElMessage.error(e?.message || '记录失败')
  } finally {
    adding.value = false
  }
}

async function removeSet(setId: number) {
  if (!active.value) return
  try {
    await deleteWorkoutSet(active.value.id, setId)
    // 重新拉取：组的序号、容量、最佳 e1RM 都要跟着变，本地拼容易不一致
    await openSession(active.value.id, false)
    await Promise.all([loadOverview(), loadSide()])
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

async function removeSession() {
  if (!active.value) return
  try {
    await ElMessageBox.confirm('删除后这次训练的所有组记录都会消失，确定吗？', '删除训练', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
  } catch { return }
  try {
    await deleteWorkoutSession(active.value.id)
    ElMessage.success('已删除')
    active.value = null
    await Promise.all([loadOverview(), loadSide(), loadSessions()])
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

// ---------------------------------------------------------------- 图表
const chartEl = ref<HTMLDivElement | null>(null)
let chart: ECharts | null = null

function renderChart() {
  if (!chartEl.value) return
  if (!chart) chart = init(chartEl.value)
  const labels = weekly.value.map((w) => w.week_start.slice(5).replace('-', '/'))
  const data = weekly.value.map((w) => w.volume)
  chart.setOption({
    grid: { left: 8, right: 8, top: 16, bottom: 4, containLabel: true },
    tooltip: {
      trigger: 'axis',
      formatter: (p: any) => {
        const i = p[0].dataIndex
        const w = weekly.value[i]
        return `${w.week_start} 起<br/>容量 ${fmt(w.volume)} kg · ${w.sets} 组`
      },
    },
    xAxis: {
      type: 'category', data: labels,
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.08)' } },
      axisTick: { show: false },
      axisLabel: { color: '#97A2AD', fontSize: 10, interval: 2 },
    },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } },
      axisLabel: { color: '#97A2AD', fontSize: 10 } },
    series: [{
      type: 'bar',
      data,
      barMaxWidth: 18,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#0CD8A0' },
            { offset: 1, color: 'rgba(12,216,160,0.25)' },
          ],
        },
      },
    }],
  })
}

function onResize() { chart?.resize() }

onMounted(async () => {
  await Promise.all([loadOverview(), loadSessions(), loadSide()])
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.wo-section { padding: 72px 0 100px; background: var(--clr-bg-section); }

/* ---------- 概览 ---------- */
.wo-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.wo-stat { background: var(--clr-white); border: 1px solid rgba(0,0,0,0.05); padding: 22px 24px; }
.wo-stat__label { font-size: 12px; letter-spacing: 2px; color: var(--clr-gray); margin-bottom: 10px; }
.wo-stat__value { font-family: var(--font-display); font-size: 30px; color: var(--clr-dark); line-height: 1; }
.wo-stat__unit { font-size: 13px; color: var(--clr-gray); margin-left: 6px; font-family: var(--font-primary); }
.wo-stat__hint { margin-top: 10px; font-size: 12px; color: var(--clr-gray-light); }
.wo-stat__bar { margin-top: 14px; height: 4px; background: rgba(0,0,0,0.06); overflow: hidden; }
.wo-stat__bar i { display: block; height: 100%; background: var(--grad-brand); transition: width .5s ease; }

/* ---------- 布局 ---------- */
.wo-layout { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 20px; align-items: start; }
.wo-main, .wo-side { display: flex; flex-direction: column; gap: 20px; }

.wo-card { background: var(--clr-white); border: 1px solid rgba(0,0,0,0.05); padding: 26px 28px; }
.wo-card__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 20px; }
.wo-card__label { font-size: 10px; letter-spacing: 3px; color: var(--clr-gold-dark); margin-bottom: 6px; }
.wo-card__title { font-family: var(--font-display); font-size: 22px; font-weight: 400; color: var(--clr-dark); margin: 0; }
.wo-card__aside { font-size: 12px; color: var(--clr-gray-light); }
.wo-card__badge { color: var(--clr-gold); font-size: 20px; }
.wo-card__actions { display: flex; gap: 8px; align-items: center; }
.wo-card__foot {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(0,0,0,0.06);
  font-size: 12px; color: var(--clr-gray);
}

/* ---------- 空态/加载 ---------- */
.wo-empty { text-align: center; padding: 36px 20px; color: var(--clr-gray); font-size: 14px; }
.wo-empty--small { padding: 20px; font-size: 13px; color: var(--clr-gray-light); }
.wo-empty__icon { color: var(--clr-gold); margin-bottom: 12px; }
.wo-empty__sub { font-size: 12px; color: var(--clr-gray-light); margin-top: 6px; }
.wo-loading { padding: 24px; text-align: center; color: var(--clr-gray-light); font-size: 13px; }

/* ---------- 会话信息 ---------- */
.wo-meta { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin-bottom: 18px; }
.wo-meta__title { max-width: 320px; }
.wo-meta__fields { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--clr-gray); }
.wo-meta__fields label { color: var(--clr-gray); }
.wo-meta__gap { margin-left: 8px; }
.wo-meta__unit { color: var(--clr-gray-light); }

/* ---------- 组列表 ---------- */
.wo-groups { display: flex; flex-direction: column; gap: 18px; margin-bottom: 8px; }
.wo-group__head { display: flex; justify-content: space-between; align-items: baseline; padding-bottom: 8px; border-bottom: 1px solid rgba(0,0,0,0.06); }
.wo-group__name { font-size: 15px; color: var(--clr-dark); font-weight: 500; }
.wo-group__sum { font-size: 12px; color: var(--clr-gray); }
.wo-group__sum em { font-style: normal; color: var(--clr-gold-dark); margin-left: 10px; }
.wo-group__rows { margin-top: 6px; }

.wo-set {
  display: grid; grid-template-columns: 32px 1fr auto 92px 28px;
  align-items: center; gap: 10px; padding: 9px 6px; font-size: 13px;
  border-bottom: 1px dashed rgba(0,0,0,0.05);
}
.wo-set:last-child { border-bottom: none; }
.wo-set.is-warmup { opacity: .62; }
.wo-set__idx { color: var(--clr-gray-light); font-size: 12px; text-align: center; }
.wo-set__main { color: var(--clr-dark); }
.wo-set__main b { font-family: var(--font-mono); font-size: 14px; }
.wo-set__rpe { font-size: 11px; color: var(--clr-gray); }
.wo-set__vol { font-size: 12px; color: var(--clr-gray-light); text-align: right; }
.wo-set__del { border: none; background: none; cursor: pointer; color: var(--clr-gray-lighter); padding: 4px; }
.wo-set__del:hover { color: #e05656; }

/* ---------- 录入 ---------- */
.wo-add { margin-top: 20px; padding: 18px; background: var(--clr-bg-section); border: 1px solid rgba(0,0,0,0.04); }
.wo-add__name { width: 100%; margin-bottom: 12px; }
.wo-add__nums { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; }
.wo-field { display: flex; flex-direction: column; gap: 5px; }
.wo-field label { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.wo-field :deep(.el-input-number) { width: 118px; }
.wo-field--sm :deep(.el-input-number) { width: 96px; }
.wo-field--check { padding-bottom: 6px; }
.wo-add__btn { margin-left: auto; }
.wo-add__tip { margin: 12px 0 0; font-size: 11px; color: var(--clr-gray-light); }
.wo-suggest { display: flex; justify-content: space-between; gap: 16px; }
.wo-suggest small { color: var(--clr-gray-light); }

/* ---------- 历史 ---------- */
.wo-history { display: flex; flex-direction: column; max-height: 420px; overflow-y: auto; }
.wo-history__row {
  display: flex; align-items: center; gap: 16px; width: 100%; text-align: left;
  padding: 12px 8px; background: none; border: none; border-bottom: 1px solid rgba(0,0,0,0.04);
  cursor: pointer; transition: background .2s;
}
.wo-history__row:hover { background: var(--clr-bg-section); }
.wo-history__row.is-active { background: rgba(12,216,160,0.06); }
.wo-history__date { display: flex; flex-direction: column; align-items: center; width: 52px; color: var(--clr-dark); }
.wo-history__date b { font-family: var(--font-display); font-size: 16px; }
.wo-history__date small { font-size: 10px; color: var(--clr-gray-light); }
.wo-history__main { flex: 1; display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.wo-history__main b { font-size: 14px; color: var(--clr-dark); font-weight: 500; }
.wo-history__main small { font-size: 12px; color: var(--clr-gray); }
.wo-history__go { font-size: 12px; color: var(--clr-gold-dark); }

/* ---------- 侧栏 ---------- */
.wo-chart { height: 180px; width: 100%; }
.wo-chart__foot { margin: 10px 0 0; font-size: 11px; color: var(--clr-gray-light); line-height: 1.6; }
.wo-prs { display: flex; flex-direction: column; gap: 12px; }
.wo-pr { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding-bottom: 10px; border-bottom: 1px dashed rgba(0,0,0,0.05); }
.wo-pr:last-child { border-bottom: none; padding-bottom: 0; }
.wo-pr__name { font-size: 13px; color: var(--clr-dark); }
.wo-pr__nums { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; font-size: 12px; color: var(--clr-gray); }
.wo-pr__nums em { font-style: normal; font-size: 10px; color: var(--clr-gray-light); margin-right: 4px; }

/* ---------- 日历 ---------- */
.wo-cal { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; }
.wo-cal__wd { font-size: 10px; color: var(--clr-gray-light); text-align: center; padding-bottom: 4px; }
.wo-cal__day {
  aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
  font-size: 11px; color: var(--clr-gray); background: rgba(0,0,0,0.03);
}
.wo-cal__day.is-empty { background: none; }
.wo-cal__day.is-done { color: #06301f; font-weight: 600; }
.wo-cal__day.is-today { outline: 1.5px solid var(--clr-gold); outline-offset: -1.5px; }

@media (max-width: 1100px) {
  .wo-layout { grid-template-columns: 1fr; }
  .wo-stats { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .wo-section { padding: 48px 0 72px; }
  .wo-card { padding: 20px; }
  .wo-set { grid-template-columns: 28px 1fr auto 28px; }
  .wo-set__vol { display: none; }
  .wo-add__btn { margin-left: 0; width: 100%; }
  .wo-field :deep(.el-input-number) { width: 100%; }
  .wo-field { flex: 1 1 40%; }
}
</style>
