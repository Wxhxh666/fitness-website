<template>
  <div class="plans-page">
    <section class="page-hero">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">TRAINING PROGRAMS</span>
        <h1 class="page-hero__title">计划制定</h1>
        <p class="page-hero__desc">根据你的目标与水平，量身打造专属训练方案。</p>
      </div>
    </section>

    <!-- 身材数据与饮食方案联动横幅 -->
    <section v-if="syncData" class="section section-light" style="padding: 22px 0 0;">
      <div class="container">
        <div class="sync-banner">
          <div class="sync-banner__head">
            <span class="sync-banner__label">FITNESS SYNC</span>
            <button class="sync-banner__close" @click="clearSync"><el-icon><Close /></el-icon></button>
          </div>
          <div class="sync-banner__body">
            <div class="sync-banner__metrics">
              <div class="sync-banner__metric">
                <span>体重</span>
                <b>{{ syncData.metrics?.weight_kg ?? '--' }} kg</b>
              </div>
              <div class="sync-banner__metric">
                <span>BMI</span>
                <b>{{ syncData.metrics?.bmi ?? '--' }}</b>
              </div>
              <div class="sync-banner__metric">
                <span>体脂率</span>
                <b>{{ syncData.metrics?.body_fat ?? '--' }}%</b>
              </div>
              <div class="sync-banner__metric">
                <span>TDEE</span>
                <b>{{ syncData.metrics?.tdee ?? '--' }} kcal</b>
              </div>
              <div class="sync-banner__metric">
                <span>饮食方案</span>
                <b>{{ syncData.diet?.summary?.calories ? syncData.diet.summary.calories + ' kcal/天' : '--' }}</b>
              </div>
              <div class="sync-banner__metric">
                <span>健身目标</span>
                <b>{{ syncTargetLabel }}</b>
              </div>
            </div>
            <p class="sync-banner__tip">已从「身材数据管理」页同步身材指标与 AI 饮食方案，搭配下方训练计划形成完整健身闭环。</p>
            <div class="sync-banner__actions">
              <router-link to="/body-data" class="btn-outline-dark">返回身材数据页</router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Tab Switch -->
    <section class="section section-light" style="padding:24px 0 0;">
      <div class="container">
        <div class="plans__tabs">
          <button :class="['tab-btn', { 'is-active': activeTab === 'official' }]" @click="activeTab = 'official'">官方计划</button>
          <button :class="['tab-btn', { 'is-active': activeTab === 'my' }]" @click="activeTab = 'my'; loadMyPlans()">
            我的计划
            <span v-if="myPlans.length" class="tab-badge">{{ myPlans.length }}</span>
          </button>
        </div>
      </div>
    </section>

    <!-- ===== Official Plans Tab ===== -->
    <template v-if="activeTab === 'official'">
      <section class="plans__goals section section-light">
        <div class="container">
          <div class="section-header text-center">
            <p class="section-subtitle">YOUR GOAL</p>
            <h2 class="section-title">选择你的目标</h2>
            <div class="gold-divider"></div>
          </div>
          <div class="goals__grid">
            <button v-for="goal in goals" :key="goal.key"
              :class="['goal-card', { 'is-active': activeGoal === goal.key }]"
              @click="switchGoal(goal.key)"
            >
              <div class="goal-card__icon"><el-icon :size="28"><component :is="goal.icon" /></el-icon></div>
              <h3 class="goal-card__title">{{ goal.label }}</h3>
              <p class="goal-card__desc">{{ goal.desc }}</p>
            </button>
          </div>
        </div>
      </section>

      <section class="plans__list section section-white">
        <div class="container">
          <div class="section-header text-center">
            <p class="section-subtitle">RECOMMENDED PLANS</p>
            <h2 class="section-title">推荐方案</h2>
            <div class="gold-divider"></div>
          </div>
          <div class="plans__grid">
            <div v-for="(plan, index) in filteredPlans" :key="'official-' + plan.name"
              class="plan-card animate-in" :class="'animate-in-delay-' + (index % 3)"
            >
              <div class="plan-card__badge">{{ plan.badge }}</div>
              <h3 class="plan-card__title">{{ plan.name }}</h3>
              <p class="plan-card__desc">{{ plan.desc }}</p>
              <div class="plan-card__specs">
                <div class="plan-card__spec"><span class="plan-card__spec-label">周期</span><span class="plan-card__spec-value">{{ plan.duration }}</span></div>
                <div class="plan-card__spec"><span class="plan-card__spec-label">频次</span><span class="plan-card__spec-value">{{ plan.frequency }}</span></div>
                <div class="plan-card__spec"><span class="plan-card__spec-label">难度</span><span class="plan-card__spec-value plan-card__diff" :class="'diff--' + plan.difficulty">{{ plan.difficultyLabel }}</span></div>
              </div>
              <div class="plan-card__focus"><span v-for="f in plan.focus" :key="f" class="plan-card__focus-tag">{{ f }}</span></div>
              <div class="plan-card__actions">
                <router-link :to="'/plans/' + plan.id" class="btn-outline-dark plan-card__btn">查看详情</router-link>
                <button v-if="isLoggedIn" class="btn-clone" @click="clonePlan(plan.id)">克隆到我的计划</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- ===== My Plans Tab ===== -->
    <template v-if="activeTab === 'my'">
      <section class="section section-white">
        <div class="container">
          <div class="section-header text-center">
            <p class="section-subtitle">MY PLANS</p>
            <h2 class="section-title">我的计划</h2>
            <div class="gold-divider"></div>
            <div style="margin-top:16px;">
              <button class="btn-primary" @click="openCreateDialog"><el-icon><Plus /></el-icon> 创建计划</button>
            </div>
          </div>
          <div v-if="myPlansLoading" class="text-center" style="padding:60px;color:#999;">加载中...</div>
          <div v-else-if="myPlans.length === 0" class="text-center" style="padding:60px;color:#999;">
            <p style="margin-bottom:16px;">还没有个人计划，可以创建一个或从官方计划克隆</p>
          </div>
          <div v-else class="plans__grid">
            <div v-for="(plan, index) in myPlans" :key="'my-' + plan.id"
              class="plan-card animate-in" :class="'animate-in-delay-' + (index % 3)"
            >
              <h3 class="plan-card__title">{{ plan.name }}</h3>
              <p class="plan-card__desc">{{ plan.desc || '暂无描述' }}</p>
              <div class="plan-card__specs">
                <div v-if="plan.duration" class="plan-card__spec"><span class="plan-card__spec-label">周期</span><span class="plan-card__spec-value">{{ plan.duration }}</span></div>
                <div v-if="plan.frequency" class="plan-card__spec"><span class="plan-card__spec-label">频次</span><span class="plan-card__spec-value">{{ plan.frequency }}</span></div>
                <div class="plan-card__spec"><span class="plan-card__spec-label">目标</span><span class="plan-card__spec-value">{{ plan.goal || '通用' }}</span></div>
              </div>
              <div v-if="plan.weekly_schedule && plan.weekly_schedule.length" class="plan-card__focus">
                <span v-for="d in plan.weekly_schedule.slice(0,5)" :key="d.day" class="plan-card__focus-tag">{{ d.day }}</span>
              </div>
              <div class="plan-card__actions">
                <button class="btn-clone" @click="openEditDialog(plan)"><el-icon><Edit /></el-icon> 编辑</button>
                <button class="btn-clone" @click="logToday(plan)"><el-icon><Check /></el-icon> 打卡</button>
                <button class="btn-clone plan-card__delete" @click="deleteMyPlan(plan.id)"><el-icon><Delete /></el-icon> 删除</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- Add/Edit Plan Dialog -->
    <el-dialog v-model="showPlanDialog" :title="editingPlan ? '编辑计划' : '创建计划'" width="640px" :close-on-click-modal="false">
      <el-form :model="planForm" label-position="top" ref="planFormRef">
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="planForm.name" placeholder="给计划取个名字" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="周期">
              <el-input v-model="planForm.duration" placeholder="如 8 周" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="频次">
              <el-input v-model="planForm.frequency" placeholder="如 3 天/周" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="目标">
              <el-input v-model="planForm.goal" placeholder="如 增肌" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="计划描述">
          <el-input v-model="planForm.description" type="textarea" :rows="2" placeholder="简短描述这个计划" />
        </el-form-item>
        <el-form-item label="周训安排 (每周训练日)">
          <div v-for="(day, idx) in planForm.weekly_schedule" :key="idx" class="schedule-editor-day">
            <div class="schedule-day-header">
              <el-input v-model="day.day" style="width:100px;" placeholder="周一" />
              <el-input v-model="day.focus" style="width:120px;" placeholder="训练重点" />
              <el-button size="small" type="danger" text @click="removeDay(idx)"><el-icon><Delete /></el-icon></el-button>
            </div>
            <div v-for="(ex, exIdx) in day.exercises" :key="exIdx" class="schedule-exercise-row">
              <el-input v-model="ex.name" style="width:150px;" placeholder="动作名" />
              <el-input-number v-model="ex.sets" :min="1" :max="20" size="small" style="width:80px;" />
              <span style="font-size:12px;color:#999;">组 ×</span>
              <el-input v-model="ex.reps" style="width:80px;" placeholder="次数" />
              <el-button size="small" text type="danger" @click="removeExercise(idx, exIdx)"><el-icon><Close /></el-icon></el-button>
            </div>
            <el-button size="small" text @click="addExercise(idx)" style="margin-top:4px;">+ 添加动作</el-button>
          </div>
          <el-button size="small" text @click="addDay" style="margin-top:8px;">+ 添加训练日</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPlanDialog = false">取消</el-button>
        <el-button type="primary" @click="savePlan" :loading="savingPlan">保存计划</el-button>
      </template>
    </el-dialog>

    <!-- Training Log Dialog -->
    <el-dialog v-model="showLogDialog" title="训练打卡" width="400px" :close-on-click-modal="false">
      <div style="text-align:center;padding:20px;">
        <div style="font-size:48px;color:var(--clr-gold);margin-bottom:16px;">
          <el-icon :size="48"><Select /></el-icon>
        </div>
        <p style="font-size:16px;margin-bottom:8px;">确认完成今天的训练？</p>
        <p style="font-size:13px;color:#999;">{{ logTargetPlan?.name || '' }}</p>
        <el-input v-model="logNote" placeholder="训练备注（可选）" style="margin-top:16px;" />
      </div>
      <template #footer>
        <el-button @click="showLogDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmLog" :loading="savingLog">完成打卡</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ArrowRight, Plus, Edit, Check, Delete, Select, Close } from '@element-plus/icons-vue'
import { getPlanGoals, getPlans, getExerciseCategories, isLoggedIn as checkLogin, getUser,
  cloneOfficialPlan, getUserPlans, createUserPlan, updateUserPlan, deleteUserPlan,
  logTraining, getTrainingStats } from '@/api'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const activeTab = ref('official')
const activeGoal = ref('muscle')
const goals = ref<any[]>([])
const plans = ref<any[]>([])
const loading = ref(false)
const isLoggedIn = ref(checkLogin())

// My plans
const myPlans = ref<any[]>([])
const myPlansLoading = ref(false)
const showPlanDialog = ref(false)
const editingPlan = ref<any>(null)
const savingPlan = ref(false)
const planFormRef = ref<FormInstance>()
const planForm = reactive({
  name: '', duration: '', frequency: '', goal: '', description: '',
  weekly_schedule: [] as any[],
})

// Training log
const showLogDialog = ref(false)
const logTargetPlan = ref<any>(null)
const savingLog = ref(false)
const logNote = ref('')
const trainingStats = ref<any>({})
const syncData = ref<any>(null)

const syncTargetLabel = computed(() => {
  const map: Record<string, string> = { fatloss: '减脂', muscle: '增肌', maintain: '维持体重' }
  return map[syncData.value?.target] || syncData.value?.target || '--'
})

function clearSync() {
  localStorage.removeItem('fitluxe_fitness_sync')
  syncData.value = null
}

async function loadGoals() {
  try {
    const res = await getPlanGoals()
    goals.value = res.data
    if (goals.value.length > 0) activeGoal.value = goals.value[0].key
  } catch { /* fallback */ }
}
async function loadPlans() {
  loading.value = true
  try {
    const res = await getPlans({ goal: activeGoal.value })
    plans.value = res.data.items
  } catch { /* fallback */ }
  finally { loading.value = false }
}
function switchGoal(key: string) {
  activeGoal.value = key
  loadPlans()
}
const filteredPlans = computed(() => plans.value)

async function loadMyPlans() {
  isLoggedIn.value = checkLogin()
  if (!isLoggedIn.value) { ElMessage.warning('请先登录'); return }
  myPlansLoading.value = true
  try {
    const [planRes, statsRes] = await Promise.all([
      getUserPlans(),
      getTrainingStats(),
    ])
    myPlans.value = planRes.data.items
    trainingStats.value = statsRes.data
  } catch { /* */ }
  finally { myPlansLoading.value = false }
}

async function clonePlan(planId: number) {
  if (!checkLogin()) { ElMessage.warning('请先登录'); return }
  try {
    await cloneOfficialPlan(planId)
    ElMessage.success('已克隆到我的计划')
    if (activeTab.value === 'my') loadMyPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '克隆失败')
  }
}

function openCreateDialog() {
  if (!checkLogin()) { ElMessage.warning('请先登录'); return }
  editingPlan.value = null
  planForm.name = ''; planForm.duration = ''; planForm.frequency = ''
  planForm.goal = ''; planForm.description = ''
  planForm.weekly_schedule = []
  showPlanDialog.value = true
}

function openEditDialog(plan: any) {
  editingPlan.value = plan
  planForm.name = plan.name
  planForm.duration = plan.duration || ''
  planForm.frequency = plan.frequency || ''
  planForm.goal = plan.goal || ''
  planForm.description = plan.desc || plan.description || ''
  planForm.weekly_schedule = JSON.parse(JSON.stringify(plan.weekly_schedule || []))
  showPlanDialog.value = true
}

function addDay() {
  planForm.weekly_schedule.push({ day: '', focus: '', exercises: [] })
}
function removeDay(idx: number) {
  planForm.weekly_schedule.splice(idx, 1)
}
function addExercise(dayIdx: number) {
  planForm.weekly_schedule[dayIdx].exercises.push({ name: '', sets: 3, reps: '12' })
}
function removeExercise(dayIdx: number, exIdx: number) {
  planForm.weekly_schedule[dayIdx].exercises.splice(exIdx, 1)
}

async function savePlan() {
  if (!planForm.name.trim()) { ElMessage.warning('请输入计划名称'); return }
  savingPlan.value = true
  try {
    if (editingPlan.value) {
      await updateUserPlan(editingPlan.value.id, { ...planForm })
      ElMessage.success('计划已更新')
    } else {
      await createUserPlan({ ...planForm })
      ElMessage.success('计划已创建')
    }
    showPlanDialog.value = false
    loadMyPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    savingPlan.value = false
  }
}

async function deleteMyPlan(id: number) {
  if (!confirm('确定要删除这个计划吗？')) return
  try {
    await deleteUserPlan(id)
    ElMessage.success('已删除')
    loadMyPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

function logToday(plan: any) {
  logTargetPlan.value = plan
  logNote.value = ''
  showLogDialog.value = true
}

async function confirmLog() {
  if (!logTargetPlan.value) return
  savingLog.value = true
  try {
    await logTraining({
      plan_id: logTargetPlan.value.id,
      is_official: false,
      focus: logTargetPlan.value.goal || '',
      note: logNote.value,
    })
    ElMessage.success('今日打卡完成!')
    showLogDialog.value = false
    loadMyPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '打卡失败')
  } finally {
    savingLog.value = false
  }
}

onMounted(async () => {
  try {
    const raw = localStorage.getItem('fitluxe_fitness_sync')
    syncData.value = raw ? JSON.parse(raw) : null
  } catch { /* ignore */ }
  await loadGoals()
  await loadPlans()
  if (isLoggedIn.value) loadMyPlans()
})
</script>

<style scoped>
.page-hero { position:relative; padding:160px 0 80px; background:var(--clr-black); overflow:hidden; }
.page-hero__bg { position:absolute; inset:0; background:radial-gradient(ellipse at 30% 60%,rgba(201,169,110,0.05),transparent 50%); }
.page-hero__content { position:relative; z-index:1; }
.page-hero__label { font-size:11px; letter-spacing:4px; color:var(--clr-gold); margin-bottom:16px; display:inline-block; }
.page-hero__title { font-family:var(--font-display); font-size:48px; font-weight:400; color:var(--clr-cream); margin-bottom:16px; letter-spacing:2px; }
.page-hero__desc { font-size:15px; color:var(--clr-gray-light); max-width:500px; }

.plans__tabs { display:flex; gap:12px; margin-bottom:0; }
.sync-banner { background: var(--clr-white); border: 1px solid rgba(201, 169, 110, 0.35); padding: 20px 24px; }
.sync-banner__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.sync-banner__label { font-size: 11px; letter-spacing: 3px; color: var(--clr-gold); }
.sync-banner__close { background: none; border: none; color: var(--clr-gray-light); cursor: pointer; font-size: 16px; }
.sync-banner__close:hover { color: var(--clr-dark); }
.sync-banner__metrics { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 14px; }
.sync-banner__metric { display: flex; flex-direction: column; gap: 2px; padding: 12px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.04); }
.sync-banner__metric span { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.sync-banner__metric b { font-family: var(--font-display); font-size: 17px; font-weight: 400; color: var(--clr-dark); }
.sync-banner__tip { font-size: 12px; color: var(--clr-gray); margin-bottom: 12px; }
.sync-banner__actions { display: flex; }
.plans__tabs .tab-btn { padding:12px 28px; background:transparent; border:1px solid rgba(0,0,0,0.08); font-size:13px; letter-spacing:1px; color:var(--clr-gray); cursor:pointer; transition:all .3s; font-family:inherit; display:flex; align-items:center; gap:6px; }
.plans__tabs .tab-btn:hover { border-color:var(--clr-gold); color:var(--clr-gold); }
.plans__tabs .tab-btn.is-active { background:var(--clr-gold); border-color:var(--clr-gold); color:var(--clr-white); }
.tab-badge { background:var(--clr-gold-dark); color:#fff; font-size:10px; padding:1px 7px; border-radius:10px; }

.goals__grid { display:grid; grid-template-columns:repeat(4,1fr); gap:20px; margin-top:48px; }
.goal-card { text-align:center; padding:40px 20px; background:var(--clr-white); border:1px solid rgba(0,0,0,0.05); cursor:pointer; transition:var(--transition-default); font-family:inherit; }
.goal-card:hover { border-color:var(--clr-gold); transform:translateY(-4px); box-shadow:0 8px 32px rgba(201,169,110,0.1); }
.goal-card.is-active { border-color:var(--clr-gold); background:var(--clr-white); box-shadow:0 8px 32px rgba(201,169,110,0.15); }
.goal-card__icon { margin-bottom:16px; color:var(--clr-gold); }
.goal-card__title { font-family:var(--font-display); font-size:18px; font-weight:400; color:var(--clr-dark); margin-bottom:8px; letter-spacing:1px; }
.goal-card__desc { font-size:13px; color:var(--clr-gray); line-height:1.6; }

.plans__grid { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; margin-top:48px; }
.plan-card { background:var(--clr-white); border:1px solid rgba(0,0,0,0.05); padding:36px 28px; transition:var(--transition-default); display:flex; flex-direction:column; }
.plan-card:hover { transform:translateY(-4px); box-shadow:0 12px 40px rgba(0,0,0,0.08); }
.plan-card__badge { display:inline-block; align-self:flex-start; font-size:10px; letter-spacing:2px; padding:4px 14px; margin-bottom:16px; color:var(--clr-gold); border:1px solid var(--clr-gold); }
.plan-card__title { font-family:var(--font-display); font-size:22px; font-weight:400; color:var(--clr-dark); margin-bottom:12px; letter-spacing:1px; }
.plan-card__desc { font-size:14px; line-height:1.7; color:var(--clr-gray); margin-bottom:24px; flex:1; }
.plan-card__specs { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; padding:16px 0; border-top:1px solid rgba(0,0,0,0.04); border-bottom:1px solid rgba(0,0,0,0.04); margin-bottom:16px; }
.plan-card__spec { text-align:center; display:flex; flex-direction:column; gap:4px; }
.plan-card__spec-label { font-size:10px; letter-spacing:2px; color:var(--clr-gray-light); text-transform:uppercase; }
.plan-card__spec-value { font-family:var(--font-display); font-size:15px; color:var(--clr-dark); }
.plan-card__diff.diff--beginner { color:#6b8e6b; } .plan-card__diff.diff--intermediate { color:#c9a96e; } .plan-card__diff.diff--advanced { color:#c0392b; }
.plan-card__focus { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:24px; }
.plan-card__focus-tag { font-size:11px; letter-spacing:1px; padding:4px 12px; background:var(--clr-bg-section); color:var(--clr-gray); }
.plan-card__actions { display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
.plan-card__btn { align-self:flex-start; }
.btn-clone { padding:8px 16px; font-size:12px; letter-spacing:1px; color:var(--clr-gold); border:1px solid var(--clr-gold); background:transparent; cursor:pointer; transition:all .2s; font-family:inherit; display:inline-flex; align-items:center; gap:4px; }
.btn-clone:hover { background:var(--clr-gold); color:var(--clr-white); }
.plan-card__delete { color:#c0392b; border-color:#c0392b; }
.plan-card__delete:hover { background:#c0392b; color:#fff; }

.schedule-editor-day { border:1px solid #eee; padding:12px; margin-bottom:12px; background:#fafafa; }
.schedule-day-header { display:flex; align-items:center; gap:8px; margin-bottom:8px; }
.schedule-exercise-row { display:flex; align-items:center; gap:8px; margin-top:4px; }

@media (max-width:1024px) { .goals__grid { grid-template-columns:repeat(2,1fr); } .plans__grid { grid-template-columns:repeat(2,1fr); } }
@media (max-width:768px) { .goals__grid { grid-template-columns:repeat(2,1fr); } .plans__grid { grid-template-columns:1fr; } .page-hero__title { font-size:32px; } }
</style>
