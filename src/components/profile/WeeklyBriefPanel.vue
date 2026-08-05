<template>
  <div class="p-card fade-in">
    <h3 class="p-card__title"><el-icon><DocumentChecked /></el-icon>本周健身简报</h3>

    <div v-if="loading" class="p-empty">加载中...</div>

    <template v-else>
      <!-- 最新身材记录 -->
      <div class="wb-section">
        <h4 class="wb-title">最新身材记录</h4>
        <div v-if="latest" class="wb-grid">
          <div class="wb-item"><span class="wb-item__label">记录日期</span><b>{{ latest.record_date }}</b></div>
          <div class="wb-item"><span class="wb-item__label">体重</span><b>{{ latest.weight_kg != null ? latest.weight_kg + ' kg' : '--' }}</b></div>
          <div class="wb-item"><span class="wb-item__label">BMI</span><b>{{ latest.bmi != null ? latest.bmi : '--' }}</b></div>
          <div class="wb-item"><span class="wb-item__label">TDEE</span><b>{{ latest.tdee != null ? latest.tdee + ' kcal' : '--' }}</b></div>
        </div>
        <div v-else class="wb-empty">暂无身材记录，先去身材管理页保存一条</div>
      </div>

      <!-- 一周饮食打卡 -->
      <div class="wb-section">
        <h4 class="wb-title">本周饮食打卡（近 7 天）</h4>
        <div v-if="logs.length" class="wb-grid">
          <div class="wb-item"><span class="wb-item__label">打卡天数</span><b>{{ logs.length }} / 7</b></div>
          <div class="wb-item"><span class="wb-item__label">日均摄入</span><b>{{ avgCalories }} kcal</b></div>
          <div class="wb-item"><span class="wb-item__label">日均蛋白质</span><b>{{ avgProtein }} g</b></div>
        </div>
        <div v-else class="wb-empty">本周还没有饮食打卡</div>
      </div>

      <!-- AI 周复盘 -->
      <div class="wb-section wb-section--last">
        <h4 class="wb-title">AI 周复盘</h4>
        <div class="wb-ai-actions">
          <button class="btn-primary" :disabled="reviewLoading" @click="generateReview">
            {{ reviewLoading ? 'AI 生成中…' : '生成 AI 周复盘' }}
          </button>
          <span v-if="review && review.model" class="wb-model">模型：{{ review.model }}</span>
        </div>
        <div v-if="review" class="wb-review">
          <div v-if="review.mock" class="wb-mock">演示模式：当前未配置可用 API Key</div>
          <pre>{{ review.review_text }}</pre>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardStats, getDietLogs, generateWeeklyReview } from '@/api'

const loading = ref(true)
const latest = ref<any>(null)
const logs = ref<any[]>([])
const review = ref<any>(null)
const reviewLoading = ref(false)

const avgCalories = computed(() => {
  if (!logs.value.length) return 0
  return Math.round(logs.value.reduce((s, l) => s + (l.calories || 0), 0) / logs.value.length)
})

const avgProtein = computed(() => {
  if (!logs.value.length) return 0
  return Math.round(logs.value.reduce((s, l) => s + (l.protein_g || 0), 0) / logs.value.length)
})

async function loadBrief() {
  loading.value = true
  try {
    const [statsRes, logRes] = await Promise.all([
      getDashboardStats(),
      getDietLogs({ days: 7 }),
    ])
    latest.value = statsRes.data.latest_record
    logs.value = logRes.data.items || []
  } catch {
    latest.value = null
    logs.value = []
  } finally {
    loading.value = false
  }
}

async function generateReview() {
  reviewLoading.value = true
  try {
    const res = await generateWeeklyReview()
    review.value = res.data
    ElMessage.success('AI 周复盘已生成并保存')
  } catch (e: any) {
    ElMessage.error(e?.message || '复盘生成失败')
  } finally {
    reviewLoading.value = false
  }
}

onMounted(loadBrief)
</script>

<style scoped>
.p-empty { padding: 60px 20px; text-align: center; color: var(--clr-gray); font-size: 14px; }
.wb-section { padding: 18px 0; border-bottom: 1px solid rgba(184, 156, 102, 0.14); }
.wb-section--last { border-bottom: none; }
.wb-title { font-size: 14px; font-weight: 500; color: var(--clr-dark); margin-bottom: 12px; }
.wb-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.wb-item {
  background: #FBF8F2; border: 1px solid rgba(184, 156, 102, 0.18);
  border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 4px;
}
.wb-item__label { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.wb-item b { font-size: 18px; font-weight: 600; color: var(--clr-gold-dark); }
.wb-empty { font-size: 13px; color: var(--clr-gray-light); padding: 10px 0; }
.wb-ai-actions { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.wb-model { font-size: 12px; color: var(--clr-gray); }
.wb-review {
  background: #FBF8F2; border: 1px solid rgba(184, 156, 102, 0.22);
  border-radius: 10px; padding: 16px;
}
.wb-review pre {
  white-space: pre-wrap; word-break: break-word;
  font-size: 13px; line-height: 1.9; color: var(--clr-dark);
  font-family: var(--font-primary);
}
.wb-mock {
  font-size: 12px; color: #8a6d3b; background: rgba(201, 169, 110, 0.1);
  border: 1px dashed rgba(201, 169, 110, 0.5); border-radius: 8px;
  padding: 8px 12px; margin-bottom: 10px;
}

@media (max-width: 768px) {
  .wb-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
