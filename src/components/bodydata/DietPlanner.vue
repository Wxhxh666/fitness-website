<template>
  <div class="ai-diet__card">
    <div class="ai-diet__main">
      <div class="ai-diet__form">
        <p class="ai-diet__source"><el-icon><InfoFilled /></el-icon>{{ dietSourceHint }}</p>
        <div class="ai-diet__field">
          <label>健身目标</label>
          <el-select v-model="dietForm.target" style="width: 100%">
            <el-option label="减脂" value="fatloss" />
            <el-option label="增肌" value="muscle" />
            <el-option label="维持体重" value="maintain" />
          </el-select>
        </div>
        <div class="ai-diet__field">
          <label>每周运动强度</label>
          <el-select v-model="dietForm.sport_level" style="width: 100%">
            <el-option v-for="opt in activityOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </div>
        <div class="ai-diet__field">
          <label>就餐条件</label>
          <el-select v-model="dietForm.eat_scene" style="width: 100%">
            <el-option v-for="s in eatSceneOptions" :key="s" :label="s" :value="s" />
          </el-select>
        </div>
        <div class="ai-diet__field">
          <label>饮食限制与偏好（忌口 / 过敏 / 口味）</label>
          <el-input v-model="dietForm.diet_limit" type="textarea" :rows="3" placeholder="例：不吃海鲜，乳糖不耐受，偏爱清淡少油" />
        </div>
        <div class="ai-diet__actions">
          <button class="btn-outline-dark" @click="syncToPlans">
            <el-icon><Link /></el-icon>同步到计划制定
          </button>
          <button class="btn-text btn-text--light" @click="clearChat">清空对话</button>
        </div>
        <p class="ai-diet__hint">在右侧对话框输入你的饮食问题，或直接点击下方推荐问题开始对话。</p>
        <p v-if="dietDirty" class="form-hint">偏好已更新，下次生成方案时生效</p>
      </div>

      <div class="chat-panel">
        <div class="chat-panel__head">
          <span class="chat-panel__title"><el-icon><ChatDotRound /></el-icon>AI 营养师对话</span>
          <span class="chat-panel__sub">{{ chatMessages.length }} 条消息</span>
        </div>

        <div ref="chatBox" class="chat-panel__messages">
          <div v-if="!chatMessages.length" class="chat-panel__empty">
            <el-icon :size="36"><MagicStick /></el-icon>
            <p>输入你的饮食问题（例如「帮我生成一份减脂食谱」「换成外卖版」），AI 会结合你的身材数据回答。</p>
            <button class="btn-primary" :disabled="chatSending" @click="sendChat('按我的身材数据生成一份' + dietTargetLabel(dietForm.target) + '食谱')">
              生成 AI 饮食方案
            </button>
          </div>

          <div v-for="(m, i) in chatMessages" :key="i" class="chat-msg" :class="'chat-msg--' + m.role">
            <div class="chat-msg__bubble">
              <template v-if="m.role === 'assistant'">
                <div v-if="m.mock" class="ai-diet__mock">演示模式：以下为示例方案。</div>
                <DietPlanCards v-if="m.plan" :plan="m.plan" />
                <div class="chat-msg__text">
                  <pre>{{ m.content }}</pre>
                </div>
                <div v-if="m.plan" class="chat-msg__actions">
                  <button class="btn-outline-dark" @click="saveChatPlan(m)"><el-icon><FolderAdd /></el-icon>保存到档案</button>
                </div>
              </template>
              <template v-else>{{ m.content }}</template>
            </div>
            <span class="chat-msg__time">{{ m.time }}</span>
          </div>

          <div v-if="chatSending" class="chat-msg chat-msg--assistant">
            <div class="chat-msg__bubble chat-msg__thinking">
              <span class="chat-dot"></span><span class="chat-dot"></span><span class="chat-dot"></span>
            </div>
          </div>
        </div>

        <div class="chat-panel__chips">
          <button v-for="c in suggestionChips" :key="c" class="chat-chip" :disabled="chatSending" @click="sendChat(c)">{{ c }}</button>
        </div>

        <div class="chat-panel__input">
          <el-input
            v-model="chatInput"
            type="textarea"
            :rows="2"
            resize="none"
            placeholder="输入你的饮食问题，例如：帮我换成外卖友好的版本 / 乳糖不耐受怎么吃"
            @keydown.enter.prevent="sendChat()"
          />
          <button class="btn-primary chat-panel__send" :disabled="chatSending || !chatInput.trim()" @click="sendChat()">
            {{ chatSending ? 'AI 思考中…' : '发送' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 饮食打卡 + 周期复盘 -->
    <div class="ai-diet__extra">
      <div class="diet-checkin">
        <h3 class="ai-extra__title"><el-icon><KnifeFork /></el-icon>每日饮食打卡</h3>
        <div class="diet-checkin__compare">
          <div class="diet-checkin__cmp-item">
            <span class="diet-checkin__cmp-label">今日摄入</span>
            <b>{{ todayLog ? fmtNum(todayLog.calories, 0) : '--' }}</b><span class="diet-checkin__cmp-unit">kcal</span>
          </div>
          <div class="diet-checkin__cmp-item">
            <span class="diet-checkin__cmp-label">TDEE 参考</span>
            <b>{{ tdeeNow ? fmtNum(tdeeNow, 0) : '--' }}</b><span class="diet-checkin__cmp-unit">kcal</span>
          </div>
          <div class="diet-checkin__cmp-item">
            <span class="diet-checkin__cmp-label">热量差值</span>
            <b :class="diffClassSimple(caloriesDiff)">{{ caloriesDiff === null ? '--' : (caloriesDiff > 0 ? '+' : '') + fmtNum(caloriesDiff, 0) }}</b>
          </div>
        </div>
        <div class="diet-checkin__form">
          <div class="diet-checkin__row">
            <div class="diet-checkin__field">
              <label>日期</label>
              <el-date-picker v-model="dietLogForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </div>
            <div class="diet-checkin__field">
              <label>当日摄入（kcal）*</label>
              <el-input-number v-model="dietLogForm.calories" :min="0" :step="10" :controls="false" style="width: 100%" placeholder="例：1850" />
            </div>
          </div>
          <div class="diet-checkin__row">
            <div class="diet-checkin__field">
              <label>蛋白质 g</label>
              <el-input-number v-model="dietLogForm.protein_g" :min="0" :controls="false" style="width: 100%" />
            </div>
            <div class="diet-checkin__field">
              <label>碳水 g</label>
              <el-input-number v-model="dietLogForm.carbs_g" :min="0" :controls="false" style="width: 100%" />
            </div>
            <div class="diet-checkin__field">
              <label>脂肪 g</label>
              <el-input-number v-model="dietLogForm.fat_g" :min="0" :controls="false" style="width: 100%" />
            </div>
          </div>
          <div class="diet-checkin__field">
            <label>备注</label>
            <el-input v-model="dietLogForm.note" placeholder="例：训练日 / 外食聚餐" />
          </div>
          <button class="btn-primary" @click="saveDietLogNow">保存打卡</button>
        </div>
        <div v-if="dietLogs.length" class="diet-checkin__list">
          <div v-for="log in dietLogs.slice(0, 7)" :key="log.id" class="diet-checkin__item">
            <span class="diet-checkin__date">{{ log.log_date }}</span>
            <span class="diet-checkin__cal">{{ fmtNum(log.calories, 0) }} kcal</span>
            <span class="diet-checkin__macros">P{{ fmtNum(log.protein_g, 0) }} / C{{ fmtNum(log.carbs_g, 0) }} / F{{ fmtNum(log.fat_g, 0) }}</span>
            <el-popconfirm title="删除这条打卡？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removeDietLog(log.id)">
              <template #reference>
                <button class="table-btn table-btn--danger">删除</button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>

      <div class="weekly-review">
        <h3 class="ai-extra__title"><el-icon><Refresh /></el-icon>周期复盘（近 7 天）</h3>
        <p class="weekly-review__desc">汇总本周身材数据与饮食打卡情况，AI 生成一周健身饮食复盘小结。</p>
        <button class="btn-primary" :disabled="reviewLoading" @click="generateReview">
          {{ reviewLoading ? 'AI 汇总中…' : '生成本周复盘' }}
        </button>
        <div v-if="weeklyReview" class="weekly-review__chips">
          <div v-for="c in reviewChips" :key="c.label" class="weekly-review__chip">
            <span class="weekly-review__chip-label">{{ c.label }}</span>
            <b>{{ c.value }}</b>
          </div>
        </div>
        <div v-if="weeklyReview" class="weekly-review__text">
          <div v-if="weeklyReview.mock" class="ai-diet__mock">演示模式：以下为示例复盘。</div>
          <pre>{{ weeklyReview.review_text }}</pre>
        </div>
      </div>
    </div>

    <div v-if="savedPlans.length" class="ai-diet__saved">
      <h3 class="ai-diet__saved-title"><el-icon><Files /></el-icon>已保存方案（{{ savedPlans.length }}）</h3>
      <div v-for="p in savedPlans" :key="p.id" class="ai-diet__saved-item">
        <div class="ai-diet__saved-info">
          <span class="ai-diet__saved-target">{{ dietTargetLabel(p.target) }}</span>
          <span class="ai-diet__saved-date">{{ (p.created_at || '').slice(0, 10) }}</span>
          <span v-if="p.diet_limit" class="ai-diet__saved-limit">{{ p.diet_limit }}</span>
        </div>
        <div class="ai-diet__saved-actions">
          <button class="table-btn" @click="viewSavedPlan(p.id)">查看</button>
          <el-popconfirm title="删除这份方案？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removeSavedPlan(p.id)">
            <template #reference>
              <button class="table-btn table-btn--danger">删除</button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <el-dialog v-model="planDialog.visible" title="已保存的 AI 饮食方案" width="760px">
      <div v-if="planDialog.detail" class="plan-dialog">
        <div class="plan-dialog__meta">
          <span>{{ dietTargetLabel(planDialog.detail.target) }}方案</span>
          <span>{{ (planDialog.detail.created_at || '').slice(0, 10) }}</span>
          <span v-if="planDialog.detail.eat_scene">{{ planDialog.detail.eat_scene }}</span>
          <span v-if="planDialog.detail.model">模型：{{ planDialog.detail.model }}</span>
        </div>
        <DietPlanCards :plan="planDialog.detail.plan" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import DietPlanCards from '@/components/DietPlanCards.vue'
import {
  generateDietPlan,
  saveDietPlan as saveDietPlanReq,
  getDietPlans,
  getDietPlanDetail,
  deleteDietPlan,
  saveDietLog,
  getDietLogs,
  deleteDietLog,
  generateWeeklyReview,
} from '@/api'
import { fmtNum } from '@/utils/units'

const props = defineProps<{
  records: any[]
  results: any
  profile: any
  activityOptions: { value: string; label: string }[]
}>()

const router = useRouter()

const eatSceneOptions = ['自己做饭', '食堂就餐', '外卖为主', '外出就餐', '出差旅行']

const dietForm = reactive({ target: 'fatloss', sport_level: 'light', eat_scene: '自己做饭', diet_limit: '' })
const chatMessages = ref<any[]>([])
const chatInput = ref('')
const chatSending = ref(false)
const chatBox = ref<HTMLElement | null>(null)
const savedPlans = ref<any[]>([])
const planDialog = reactive({ visible: false, detail: null as any })
const dietLogs = ref<any[]>([])
const dietLogForm = reactive({ date: '', calories: null as number | null, protein_g: null as number | null, carbs_g: null as number | null, fat_g: null as number | null, note: '' })
const weeklyReview = ref<any>(null)
const reviewLoading = ref(false)
const dietDirty = ref(false)
let dietHintTimer: any = null

function flashHint() {
  dietDirty.value = true
  clearTimeout(dietHintTimer)
  dietHintTimer = setTimeout(() => { dietDirty.value = false }, 3000)
}

watch(
  [() => dietForm.target, () => dietForm.sport_level, () => dietForm.eat_scene, () => dietForm.diet_limit],
  () => flashHint()
)

function latestWith(field: string) {
  for (const r of props.records) if (r[field] != null) return r
  return null
}

function dietTargetLabel(target: string) {
  const map: Record<string, string> = { fatloss: '减脂', muscle: '增肌', maintain: '维持体重' }
  return map[target] || target
}

function buildDietPayload(regenerate = false) {
  const rec = latestWith('weight_kg')
  const src = rec || props.results
  if (!src || !src.height_cm || !src.weight_kg) return null
  return {
    height_cm: src.height_cm,
    weight_kg: src.weight_kg,
    bmi: src.bmi,
    body_fat: src.body_fat,
    gender: src.gender || props.profile.gender,
    age: src.age || props.profile.age,
    bmr: src.bmr,
    tdee: src.tdee,
    waist_cm: src.waist_cm,
    hip_cm: src.hip_cm,
    neck_cm: src.neck_cm,
    sport_level: dietForm.sport_level,
    target: dietForm.target,
    diet_limit: dietForm.diet_limit,
    eat_scene: dietForm.eat_scene,
    regenerate,
  }
}

const dietSourceHint = computed(() => {
  const rec = latestWith('weight_kg')
  return rec
    ? `使用最近一次保存记录（${rec.record_date}）中的身体指标`
    : props.results
      ? '使用当前计算结果中的身体指标'
      : '请先在上方计算指标或保存一条身材记录'
})

const suggestionChips = computed(() => {
  const rec = latestWith('weight_kg') || props.results
  const target = dietTargetLabel(dietForm.target)
  const chips = [`按我的身材数据生成一份${target}食谱`]
  if (rec?.tdee) chips.push(`我的 TDEE 是 ${fmtNum(rec.tdee, 0)}，帮我规划每日热量`)
  if (rec?.bmi) chips.push(`我 BMI ${fmtNum(rec.bmi)}，平时怎么吃更健康`)
  chips.push('换成外卖友好的版本', '给我 3 个快手晚餐搭配')
  if (dietForm.diet_limit.trim()) chips.push(`按我的忌口生成：${dietForm.diet_limit.trim()}`)
  return chips.slice(0, 6)
})

function chatNow() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function scrollChat() {
  nextTick(() => {
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  })
}

async function sendChat(text?: string) {
  const msg = (text ?? chatInput.value).trim()
  if (!msg || chatSending.value) return
  const payload = buildDietPayload(false)
  if (!payload) {
    ElMessage.warning('请先在上方填写身高体重并计算，或保存一条身材记录')
    return
  }
  chatInput.value = ''
  chatMessages.value.push({ role: 'user', content: msg, time: chatNow() })
  chatSending.value = true
  scrollChat()
  try {
    const history = chatMessages.value.slice(0, -1).map((m) => ({ role: m.role, content: m.content }))
    const res = await generateDietPlan({ ...payload, user_message: msg, history }, false)
    const d = res.data
    chatMessages.value.push({
      role: 'assistant',
      content: d.raw_text || (d.plan ? JSON.stringify(d.plan, null, 2) : '模型未返回内容，请重试'),
      plan: d.plan || null,
      mock: !!d.mock,
      time: chatNow(),
    })
    if (d.mock) ElMessage.info('当前未配置 DEEPSEEK_API_KEY，展示演示方案')
  } catch (e: any) {
    chatMessages.value.push({
      role: 'assistant',
      content: '生成失败：' + (e?.message || '请稍后重试'),
      plan: null,
      mock: false,
      time: chatNow(),
    })
  } finally {
    chatSending.value = false
    scrollChat()
  }
}

function clearChat() {
  chatMessages.value = []
  chatInput.value = ''
}

async function saveChatPlan(m: any) {
  if (!m.plan) return
  try {
    await saveDietPlanReq({
      target: dietForm.target,
      sport_level: dietForm.sport_level,
      diet_limit: dietForm.diet_limit,
      eat_scene: dietForm.eat_scene,
      plan_json: JSON.stringify(m.plan),
      raw_text: m.content || '',
      model: '',
    })
    ElMessage.success('方案已保存到档案')
    await loadDietPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

async function loadDietPlans() {
  try {
    const res = await getDietPlans()
    savedPlans.value = res.data.items
  } catch {
    savedPlans.value = []
  }
}

async function viewSavedPlan(id: number) {
  try {
    const res = await getDietPlanDetail(id)
    planDialog.detail = res.data
    planDialog.visible = true
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  }
}

async function removeSavedPlan(id: number) {
  try {
    await deleteDietPlan(id)
    ElMessage.success('已删除')
    await loadDietPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

const tdeeNow = computed(() => latestWith('tdee')?.tdee ?? null)
const todayLog = computed(() => dietLogs.value.find((l) => l.log_date === dietLogForm.date) || dietLogs.value.find((l) => l.log_date === new Date().toISOString().slice(0, 10)) || null)
const caloriesDiff = computed(() => {
  if (!todayLog.value || !tdeeNow.value) return null
  return todayLog.value.calories - tdeeNow.value
})

async function loadDietLogs() {
  try {
    const res = await getDietLogs()
    dietLogs.value = res.data.items
  } catch {
    dietLogs.value = []
  }
}

async function saveDietLogNow() {
  if (!dietLogForm.calories || dietLogForm.calories <= 0) {
    ElMessage.warning('请填写当日摄入热量')
    return
  }
  try {
    await saveDietLog({
      log_date: dietLogForm.date,
      calories: dietLogForm.calories,
      protein_g: dietLogForm.protein_g,
      carbs_g: dietLogForm.carbs_g,
      fat_g: dietLogForm.fat_g,
      note: dietLogForm.note,
    })
    ElMessage.success('打卡成功')
    dietLogForm.note = ''
    await loadDietLogs()
  } catch (e: any) {
    ElMessage.error(e?.message || '打卡失败')
  }
}

async function removeDietLog(id: number) {
  try {
    await deleteDietLog(id)
    ElMessage.success('已删除')
    await loadDietLogs()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

function diffClassSimple(diff: number | null) {
  if (diff === null) return ''
  return diff > 0 ? 'bad' : 'good'
}

const reviewChips = computed(() => {
  if (!weeklyReview.value) return []
  const s = weeklyReview.value.summary || {}
  const w = s.weight
  return [
    { label: '本周记录', value: (s.record_count ?? 0) + ' 条' },
    { label: '体重变化', value: w ? `${w.change > 0 ? '+' : ''}${w.change}kg` : '数据不足' },
    { label: '打卡天数', value: (s.diet?.log_days ?? 0) + ' 天' },
    { label: '日均摄入', value: s.diet?.avg_calories != null ? fmtNum(s.diet.avg_calories, 0) + ' kcal' : '--' },
  ]
})

async function generateReview() {
  reviewLoading.value = true
  try {
    const res = await generateWeeklyReview()
    weeklyReview.value = res.data
    if (res.data.mock) ElMessage.info('当前为演示复盘，配置 API Key 后由 AI 生成')
  } catch (e: any) {
    ElMessage.error(e?.message || '复盘生成失败')
  } finally {
    reviewLoading.value = false
  }
}

function syncToPlans() {
  const rec = latestWith('weight_kg') || props.results
  const lastPlan = [...chatMessages.value].reverse().find((m) => m.plan)
  const payload: any = {
    synced_at: new Date().toISOString(),
    metrics: rec
      ? {
        weight_kg: rec.weight_kg,
        bmi: rec.bmi,
        body_fat: rec.body_fat,
        tdee: rec.tdee,
        height_cm: rec.height_cm,
      }
      : null,
    diet: lastPlan?.plan || null,
    target: dietForm.target,
  }
  localStorage.setItem('fitluxe_fitness_sync', JSON.stringify(payload))
  ElMessage.success('身材指标与饮食方案已同步，跳转计划制定页')
  router.push('/plans')
}

onMounted(() => {
  dietLogForm.date = new Date().toISOString().slice(0, 10)
  loadDietPlans()
  loadDietLogs()
})
</script>

<style scoped>
.ai-diet__card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); padding: 28px; margin-top: 56px; }
.ai-diet__main { display: grid; grid-template-columns: 1fr 1.5fr; gap: 24px; }
.ai-diet__form { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 24px; }
.ai-diet__source { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--clr-gray); background: var(--clr-bg-section); border: 1px dashed rgba(0, 0, 0, 0.14); padding: 10px 12px; margin-bottom: 18px; line-height: 1.6; }
.ai-diet__source .el-icon { color: var(--clr-gold); flex-shrink: 0; }
.ai-diet__field { margin-bottom: 16px; }
.ai-diet__field label { display: block; font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; margin-bottom: 6px; }
.ai-diet__actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.ai-diet__mock { background: rgba(201, 169, 110, 0.08); border: 1px dashed rgba(201, 169, 110, 0.5); color: #8a6d3b; font-size: 12px; padding: 10px 14px; margin-bottom: 16px; line-height: 1.7; }
.ai-diet__hint { margin-top: 14px; font-size: 12px; color: var(--clr-gray-light); line-height: 1.7; }
.btn-text { background: none; border: none; color: var(--clr-gray); font-size: 13px; letter-spacing: 1px; cursor: pointer; padding: 8px 4px; transition: var(--transition-default); }
.btn-text:hover { color: var(--clr-gold-dark); }
.btn-text--light { color: var(--clr-gray-light); }
.btn-text--light:hover { color: var(--clr-gold); }

.chat-panel { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); display: flex; flex-direction: column; height: 640px; }
.chat-panel__head { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid rgba(0, 0, 0, 0.05); }
.chat-panel__title { font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
.chat-panel__title .el-icon { color: var(--clr-gold); }
.chat-panel__sub { font-size: 11px; color: var(--clr-gray-light); }
.chat-panel__messages { flex: 1; overflow-y: auto; padding: 18px; display: flex; flex-direction: column; gap: 14px; }
.chat-panel__empty { text-align: center; padding: 48px 20px; color: var(--clr-gray); font-size: 13px; }
.chat-panel__empty .el-icon { color: var(--clr-gold); margin-bottom: 12px; }
.chat-panel__empty p { margin-bottom: 16px; line-height: 1.8; }
.chat-msg { display: flex; flex-direction: column; max-width: 94%; }
.chat-msg--user { align-self: flex-end; align-items: flex-end; }
.chat-msg--assistant { align-self: flex-start; align-items: flex-start; }
.chat-msg__bubble { padding: 12px 16px; border-radius: 10px; font-size: 13px; line-height: 1.8; word-break: break-word; }
.chat-msg--user .chat-msg__bubble { background: var(--clr-gold); color: var(--clr-white); border-bottom-right-radius: 2px; }
.chat-msg--assistant .chat-msg__bubble { background: var(--clr-bg-section); color: var(--clr-gray-deep); border: 1px solid rgba(0, 0, 0, 0.05); border-bottom-left-radius: 2px; }
.chat-msg__text pre { white-space: pre-wrap; word-break: break-word; font-size: 13px; color: var(--clr-gray-deep); line-height: 1.8; font-family: var(--font-primary); max-height: 320px; overflow-y: auto; margin-top: 10px; }
.chat-msg__actions { margin-top: 10px; }
.chat-msg__actions .btn-outline-dark { padding: 7px 16px; font-size: 12px; }
.chat-msg__time { font-size: 10px; color: var(--clr-gray-light); margin-top: 4px; }
.chat-msg__thinking { display: flex; gap: 6px; align-items: center; min-width: 60px; justify-content: center; }
.chat-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--clr-gold); animation: chatPulse 1.2s infinite ease-in-out; }
.chat-dot:nth-child(2) { animation-delay: 0.2s; }
.chat-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes chatPulse { 0%, 100% { opacity: 0.3; transform: scale(0.85); } 50% { opacity: 1; transform: scale(1); } }
.chat-panel__chips { display: flex; gap: 8px; flex-wrap: wrap; padding: 12px 14px; border-top: 1px solid rgba(0, 0, 0, 0.05); }
.chat-chip { font-size: 12px; color: var(--clr-gold-dark); background: rgba(201, 169, 110, 0.08); border: 1px solid rgba(201, 169, 110, 0.35); padding: 6px 12px; cursor: pointer; transition: var(--transition-default); }
.chat-chip:hover { background: rgba(201, 169, 110, 0.18); }
.chat-chip:disabled { opacity: 0.5; cursor: not-allowed; }
.chat-panel__input { display: flex; gap: 10px; padding: 12px 14px; border-top: 1px solid rgba(0, 0, 0, 0.05); align-items: flex-end; }
.chat-panel__input .el-textarea { flex: 1; }
.chat-panel__send { padding: 12px 24px; white-space: nowrap; }

.ai-diet__extra { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px; }
.diet-checkin, .weekly-review { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.ai-extra__title { font-size: 15px; font-weight: 500; display: flex; align-items: center; gap: 8px; color: var(--clr-dark); margin-bottom: 14px; }
.ai-extra__title .el-icon { color: var(--clr-gold); }
.diet-checkin__compare { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
.diet-checkin__cmp-item { display: flex; flex-direction: column; gap: 2px; padding: 12px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); }
.diet-checkin__cmp-label { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.diet-checkin__cmp-item b { font-family: var(--font-display); font-size: 20px; color: var(--clr-dark); font-weight: 400; }
.diet-checkin__cmp-item b.good { color: #6b8e6b; }
.diet-checkin__cmp-item b.bad { color: #c0392b; }
.diet-checkin__cmp-unit { font-size: 11px; color: var(--clr-gray); }
.diet-checkin__form { display: flex; flex-direction: column; gap: 12px; }
.diet-checkin__row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.diet-checkin__field label { display: block; font-size: 12px; color: var(--clr-gray); margin-bottom: 6px; }
.diet-checkin__list { margin-top: 16px; display: flex; flex-direction: column; gap: 8px; }
.diet-checkin__item { display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--clr-bg-section); font-size: 12px; }
.diet-checkin__date { color: var(--clr-gray-deep); }
.diet-checkin__cal { color: var(--clr-dark); font-weight: 500; }
.diet-checkin__macros { color: var(--clr-gray); flex: 1; }
.table-btn { background: transparent; border: 1px solid rgba(0, 0, 0, 0.2); color: var(--clr-gray-deep); font-size: 12px; padding: 4px 12px; cursor: pointer; margin-right: 8px; transition: var(--transition-default); }
.table-btn:hover { border-color: var(--clr-gold); color: var(--clr-gold-dark); }
.table-btn--danger { border-color: rgba(179, 85, 74, 0.45); color: #b3554a; }
.table-btn--danger:hover { border-color: #b3554a; color: #b3554a; }

.weekly-review__desc { font-size: 12px; color: var(--clr-gray); line-height: 1.7; margin-bottom: 14px; }
.weekly-review__chips { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 16px; }
.weekly-review__chip { display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); }
.weekly-review__chip-label { font-size: 11px; color: var(--clr-gray); }
.weekly-review__chip b { font-size: 15px; font-weight: 500; color: var(--clr-dark); }
.weekly-review__text { margin-top: 14px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.06); padding: 14px; }
.weekly-review__text pre { white-space: pre-wrap; word-break: break-word; font-size: 12px; color: var(--clr-gray-deep); line-height: 1.8; font-family: var(--font-primary); }

.ai-diet__saved { margin-top: 28px; }
.ai-diet__saved-title { font-size: 15px; font-weight: 500; display: flex; align-items: center; gap: 8px; color: var(--clr-cream); margin-bottom: 14px; }
.ai-diet__saved-title .el-icon { color: var(--clr-gold); }
.ai-diet__saved-item { display: flex; align-items: center; justify-content: space-between; gap: 16px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.07); padding: 12px 16px; margin-bottom: 10px; }
.ai-diet__saved-info { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 13px; }
.ai-diet__saved-target { color: var(--clr-gold); font-weight: 500; }
.ai-diet__saved-date { color: var(--clr-gray); }
.ai-diet__saved-limit { color: var(--clr-gray-light); font-size: 12px; max-width: 360px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ai-diet__saved-actions { display: flex; gap: 4px; }

.plan-dialog__meta { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: var(--clr-gray); margin-bottom: 16px; }

@media (max-width: 1024px) {
  .ai-diet__main, .ai-diet__extra { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .diet-checkin__row { grid-template-columns: 1fr; }
  .diet-checkin__compare, .weekly-review__chips { grid-template-columns: 1fr 1fr; }
}
</style>
