<template>
  <div class="p-card fade-in">
    <h3 class="p-card__title"><el-icon><Bowl /></el-icon>AI 饮食方案库</h3>

    <div v-if="loading" class="p-empty">加载中...</div>

    <div v-else-if="!plans.length" class="p-empty">
      <el-icon :size="36"><Bowl /></el-icon>
      <p>还没有保存过饮食方案</p>
      <button class="btn-primary" @click="go('/body-data')">去 AI 饮食规划生成</button>
    </div>

    <div v-else class="dpl-list">
      <div v-for="p in plans" :key="p.id" class="dpl-item">
        <div class="dpl-info">
          <span class="dpl-target">{{ targetLabel(p.target) }}方案</span>
          <span class="dpl-date">{{ (p.created_at || '').slice(0, 10) }}</span>
          <span v-if="p.diet_limit" class="dpl-limit">{{ p.diet_limit }}</span>
        </div>
        <div class="dpl-actions">
          <button class="btn-outline" @click="viewPlan(p.id)">查看</button>
          <el-popconfirm title="删除这份方案？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removePlan(p.id)">
            <template #reference>
              <button class="btn-outline btn-outline--danger">删除</button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <!-- 方案详情弹窗 -->
    <el-dialog v-model="detailVisible" title="饮食方案详情" width="720px">
      <DietPlanCards v-if="detail" :plan="detail.plan" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import DietPlanCards from '@/components/DietPlanCards.vue'
import { getDietPlans, getDietPlanDetail, deleteDietPlan } from '@/api'

const router = useRouter()
const loading = ref(true)
const plans = ref<any[]>([])
const detailVisible = ref(false)
const detail = ref<any>(null)

function targetLabel(target: string) {
  const map: Record<string, string> = { fatloss: '减脂', muscle: '增肌', maintain: '维持体重' }
  return map[target] || target
}

async function loadPlans() {
  loading.value = true
  try {
    const res = await getDietPlans()
    plans.value = res.data.items
  } catch {
    plans.value = []
  } finally {
    loading.value = false
  }
}

async function viewPlan(id: number) {
  try {
    const res = await getDietPlanDetail(id)
    detail.value = res.data
    detailVisible.value = true
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  }
}

async function removePlan(id: number) {
  try {
    await deleteDietPlan(id)
    ElMessage.success('已删除')
    await loadPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

function go(path: string) {
  router.push(path)
}

onMounted(loadPlans)
</script>

<style scoped>
.p-empty {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 64px 20px; color: var(--clr-gray); font-size: 14px;
}
.p-empty .el-icon { color: var(--clr-gold); }
.dpl-list { display: flex; flex-direction: column; gap: 12px; }
.dpl-item {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  background: #FBF8F2; border: 1px solid rgba(184, 156, 102, 0.18);
  border-radius: 10px; padding: 14px 18px;
}
.dpl-info { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 13px; }
.dpl-target { color: var(--clr-gold-dark); font-weight: 500; }
.dpl-date { color: var(--clr-gray); }
.dpl-limit { color: var(--clr-gray-light); font-size: 12px; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dpl-actions { display: flex; gap: 8px; flex-shrink: 0; }
.btn-outline--danger { color: #B96A5E; border-color: rgba(185, 106, 94, 0.45); }
.btn-outline--danger:hover { background: rgba(185, 106, 94, 0.08); }
</style>
