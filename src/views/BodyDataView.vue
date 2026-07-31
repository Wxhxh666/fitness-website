<template>
  <div class="bodydata-page">
    <section class="page-hero">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">BODY ANALYTICS</span>
        <h1 class="page-hero__title">身材数据管理</h1>
        <p class="page-hero__desc">用数据量化每一分努力，科学追踪身体变化，让进步清晰可见。</p>
      </div>
    </section>

    <section class="metrics section section-light">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">KEY METRICS</p>
          <h2 class="section-title">身体核心指标</h2>
          <div class="gold-divider"></div>
        </div>
        <div class="metrics__grid">
          <div v-for="(m, idx) in metrics" :key="idx" class="metric-card">
            <div class="metric-card__icon"><el-icon :size="24"><component :is="m.icon" /></el-icon></div>
            <div class="metric-card__info"><span class="metric-card__value">{{ m.value }}</span><span class="metric-card__unit">{{ m.unit }}</span></div>
            <span class="metric-card__label">{{ m.label }}</span>
            <div class="metric-card__trend" :class="m.trend"><el-icon><component :is="m.trend === 'up' ? 'Top' : 'Bottom'" /></el-icon>{{ m.change }}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="bmi section section-white">
      <div class="container">
        <div class="bmi__layout">
          <div class="bmi__calc">
            <p class="section-subtitle">BMI CALCULATOR</p>
            <h2 class="section-title">身体质量指数</h2>
            <div class="gold-divider-left" style="margin:20px 0;"></div>
            <p class="bmi__desc">身体质量指数（BMI）是评估体重是否健康的常用指标。输入你的身高与体重即可计算。</p>
            <div class="bmi__form">
              <div class="bmi__row">
                <div class="bmi__field"><label>身高（cm）</label><el-input v-model="bmiHeight" placeholder="例如 175" /></div>
                <div class="bmi__field"><label>体重（kg）</label><el-input v-model="bmiWeight" placeholder="例如 70" /></div>
              </div>
              <button class="btn-primary" @click="calculateBMI">计算 BMI</button>
            </div>
            <transition name="fade">
              <div v-if="bmiResult !== null" class="bmi__result">
                <div class="bmi__result-value"><span class="bmi__result-number">{{ bmiResult }}</span><span class="bmi__result-unit">kg/m2</span></div>
                <div class="bmi__result-category" :class="`bmi--${bmiCategory}`">{{ bmiCategoryLabel }}</div>
                <div class="bmi__scale">
                  <div class="bmi__scale-bar"><div class="bmi__scale-fill" :style="{ width: bmiPercent + '%' }"></div><div class="bmi__scale-dot" :style="{ left: bmiPercent + '%' }"></div></div>
                  <div class="bmi__scale-labels"><span>偏瘦</span><span>正常</span><span>超重</span><span>肥胖</span></div>
                </div>
              </div>
            </transition>
          </div>
          <div class="bmi__guide">
            <div class="bmi__guide-card">
              <h3 class="bmi__guide-title">BMI 参考范围</h3>
              <div class="bmi__guide-row"><span class="bmi__guide-range">&lt; 18.5</span><span class="bmi__guide-label">偏瘦</span></div>
              <div class="bmi__guide-row"><span class="bmi__guide-range">18.5 – 24.9</span><span class="bmi__guide-label normal">正常</span></div>
              <div class="bmi__guide-row"><span class="bmi__guide-range">25 – 29.9</span><span class="bmi__guide-label">超重</span></div>
              <div class="bmi__guide-row"><span class="bmi__guide-range">&ge; 30</span><span class="bmi__guide-label">肥胖</span></div>
              <p class="bmi__guide-note">* BMI 仅供参考，运动员等肌肉量较高的人群可能不适用。</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="measurements section section-dark">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">BODY MEASUREMENTS</p>
          <h2 class="section-title">围度追踪</h2>
          <div class="gold-divider"></div>
          <p class="section-desc" style="color:var(--clr-gray);">定期记录身体各部位围度，用数据见证体型变化。</p>
        </div>
        <div class="measurements__grid">
          <div v-for="(item, idx) in measurements" :key="idx" class="measurement-card">
            <div class="measurement-card__icon"><el-icon :size="20"><component :is="item.icon" /></el-icon></div>
            <h4 class="measurement-card__label">{{ item.label }}</h4>
            <div class="measurement-card__value"><span class="measurement-card__num">{{ item.value }}</span><span class="measurement-card__unit">cm</span></div>
            <div class="measurement-card__input-area">
              <el-input v-model="item.input" placeholder="更新数据" size="small" />
              <el-button size="small" text @click="onUpdateMeasurement(item)"><el-icon><Upload /></el-icon></el-button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getBodyMetrics, getMeasurements, updateMeasurement } from '@/api'

const bmiHeight = ref('')
const bmiWeight = ref('')
const bmiResult = ref<number | null>(null)
const bmiCategory = ref('')
const bmiCategoryLabel = ref('')
const bmiPercent = ref(0)

const metrics = ref<any[]>([])
const measurements = ref<any[]>([])
const loading = ref(true)

async function loadData() {
  try {
    const [mRes, measRes] = await Promise.all([getBodyMetrics(), getMeasurements()])
    metrics.value = mRes.data
    measurements.value = measRes.data.map((m: any) => ({ ...m, input: '' }))
  } catch { /* keep defaults */ }
  finally { loading.value = false }
}
onMounted(loadData)

function calculateBMI() {
  const h = parseFloat(bmiHeight.value) / 100
  const w = parseFloat(bmiWeight.value)
  if (!h || !w || h <= 0 || w <= 0) return
  const bmi = w / (h * h)
  bmiResult.value = parseFloat(bmi.toFixed(1))
  if (bmi < 18.5) { bmiCategory.value = 'underweight'; bmiPercent.value = Math.max(5, (bmi / 40) * 100) }
  else if (bmi < 25) { bmiCategory.value = 'normal'; bmiPercent.value = (bmi / 40) * 100 }
  else if (bmi < 30) { bmiCategory.value = 'overweight'; bmiPercent.value = (bmi / 40) * 100 }
  else { bmiCategory.value = 'obese'; bmiPercent.value = Math.min(95, (bmi / 40) * 100) }
  const map: Record<string, string> = { underweight: '偏瘦', normal: '正常范围', overweight: '超重', obese: '肥胖' }
  bmiCategoryLabel.value = map[bmiCategory.value] || ''
}

async function onUpdateMeasurement(item: any) {
  if (!item.input || isNaN(parseFloat(item.input))) return
  try {
    await updateMeasurement(item.id, parseFloat(item.input))
    item.value = item.input
    item.input = ''
    ElMessage.success(`${item.label} 已更新`)
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.message || '更新失败')
  }
}
</script>

<style scoped>
.page-hero { position:relative; padding:160px 0 80px; background:var(--clr-black); overflow:hidden; }
.page-hero__bg { position:absolute; inset:0; background:radial-gradient(ellipse at 30% 60%,rgba(201,169,110,0.05),transparent 50%); }
.page-hero__content { position:relative; z-index:1; }
.page-hero__label { font-size:11px; letter-spacing:4px; color:var(--clr-gold); margin-bottom:16px; display:inline-block; }
.page-hero__title { font-family:var(--font-display); font-size:48px; font-weight:400; color:var(--clr-cream); margin-bottom:16px; letter-spacing:2px; }
.page-hero__desc { font-size:15px; color:var(--clr-gray-light); max-width:500px; }

.metrics__grid { display:grid; grid-template-columns:repeat(4,1fr); gap:20px; margin-top:48px; }
.metric-card { background:var(--clr-white); border:1px solid rgba(0,0,0,0.05); padding:32px 24px; text-align:center; transition:var(--transition-default); }
.metric-card:hover { transform:translateY(-4px); box-shadow:0 12px 40px rgba(0,0,0,0.06); }
.metric-card__icon { margin-bottom:16px; color:var(--clr-gold); }
.metric-card__info { display:flex; align-items:baseline; justify-content:center; gap:4px; margin-bottom:4px; }
.metric-card__value { font-family:var(--font-display); font-size:32px; color:var(--clr-dark); }
.metric-card__unit { font-size:14px; color:var(--clr-gray); }
.metric-card__label { font-size:13px; color:var(--clr-gray); letter-spacing:1px; }
.metric-card__trend { margin-top:12px; font-size:12px; display:flex; align-items:center; justify-content:center; gap:4px; }
.metric-card__trend.up { color:#6b8e6b; } .metric-card__trend.down { color:#888; }

.bmi__layout { display:grid; grid-template-columns:1fr 1fr; gap:64px; align-items:start; }
.bmi__desc { font-size:15px; color:var(--clr-gray); margin-bottom:28px; line-height:1.7; }
.bmi__form { display:flex; flex-direction:column; gap:20px; }
.bmi__row { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.bmi__field label { display:block; font-size:12px; letter-spacing:1px; color:var(--clr-gray); margin-bottom:6px; }
.bmi__result { margin-top:28px; padding:24px; border:1px solid rgba(201,169,110,0.2); background:var(--clr-bg-section); }
.bmi__result-value { display:flex; align-items:baseline; gap:6px; margin-bottom:8px; }
.bmi__result-number { font-family:var(--font-display); font-size:42px; color:var(--clr-dark); }
.bmi__result-unit { font-size:14px; color:var(--clr-gray); }
.bmi__result-category { font-size:13px; letter-spacing:1px; margin-bottom:20px; }
.bmi__result-category.bmi--underweight { color:#c9a96e; } .bmi__result-category.bmi--normal { color:#6b8e6b; } .bmi__result-category.bmi--overweight { color:#c9a96e; } .bmi__result-category.bmi--obese { color:#c0392b; }
.bmi__scale { margin-top:12px; }
.bmi__scale-bar { position:relative; height:4px; background:linear-gradient(to right,#c9a96e 0%,#6b8e6b 25%,#c9a96e 60%,#c0392b 100%); border-radius:2px; }
.bmi__scale-fill { position:absolute; top:0; left:0; height:100%; background:var(--clr-dark); border-radius:2px; opacity:0; }
.bmi__scale-dot { position:absolute; top:-4px; width:12px; height:12px; border-radius:50%; background:var(--clr-dark); border:2px solid var(--clr-white); transform:translateX(-6px); z-index:2; }
.bmi__scale-labels { display:flex; justify-content:space-between; margin-top:8px; font-size:11px; color:var(--clr-gray-light); }
.bmi__guide-card { background:var(--clr-bg-section); border:1px solid rgba(0,0,0,0.04); padding:36px 32px; }
.bmi__guide-title { font-family:var(--font-display); font-size:18px; font-weight:400; letter-spacing:1px; margin-bottom:24px; }
.bmi__guide-row { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(0,0,0,0.04); }
.bmi__guide-range { font-family:var(--font-display); font-size:16px; color:var(--clr-dark); }
.bmi__guide-label { font-size:13px; color:var(--clr-gray); letter-spacing:1px; }
.bmi__guide-label.normal { color:#6b8e6b; }
.bmi__guide-note { margin-top:16px; font-size:12px; color:var(--clr-gray-light); line-height:1.6; }

.measurements__grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:48px; }
.measurement-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); padding:28px 24px; text-align:center; transition:var(--transition-default); }
.measurement-card:hover { border-color:rgba(201,169,110,0.2); transform:translateY(-3px); }
.measurement-card__icon { margin-bottom:12px; color:var(--clr-gold); }
.measurement-card__label { font-size:13px; letter-spacing:1px; color:var(--clr-gray-lighter); margin-bottom:8px; font-weight:400; }
.measurement-card__value { display:flex; align-items:baseline; justify-content:center; gap:4px; margin-bottom:16px; }
.measurement-card__num { font-family:var(--font-display); font-size:28px; color:var(--clr-cream); }
.measurement-card__unit { font-size:13px; color:var(--clr-gray); }
.measurement-card__input-area { display:flex; align-items:center; gap:4px; justify-content:center; }
.fade-enter-active, .fade-leave-active { transition:opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity:0; }

@media (max-width:1024px) {
  .metrics__grid { grid-template-columns:repeat(2,1fr); }
  .bmi__layout { grid-template-columns:1fr; gap:40px; }
  .measurements__grid { grid-template-columns:repeat(2,1fr); }
}
@media (max-width:768px) {
  .metrics__grid { grid-template-columns:1fr 1fr; }
  .bmi__row { grid-template-columns:1fr; }
  .measurements__grid { grid-template-columns:1fr; }
}
</style>



