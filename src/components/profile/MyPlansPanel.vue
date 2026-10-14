<template>
  <div class="p-card fade-in">
    <h3 class="p-card__title"><el-icon><Calendar /></el-icon>我的训练计划</h3>

    <div v-if="loading" class="p-empty">加载中...</div>

    <div v-else-if="!plans.length" class="p-empty">
      <el-icon :size="36"><Calendar /></el-icon>
      <p>还没有制定训练计划</p>
      <button class="btn-primary" @click="go('/plans')">去计划制定页</button>
    </div>

    <div v-else class="mpl-list">
      <div v-for="p in plans" :key="p.id" class="mpl-item">
        <div class="mpl-info">
          <span class="mpl-name">{{ p.name }}</span>
          <span v-if="p.goal" class="mpl-tag">{{ goalLabel(p.goal) }}</span>
          <span v-if="p.difficulty_label" class="mpl-tag">{{ p.difficulty_label }}</span>
          <span v-if="p.duration" class="mpl-meta">{{ p.duration }}</span>
          <span v-if="p.frequency" class="mpl-meta">{{ p.frequency }}</span>
        </div>
        <div class="mpl-actions">
          <el-popconfirm title="删除这个计划？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removePlan(p.id)">
            <template #reference>
              <button class="btn-outline btn-outline--danger">删除</button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserPlans, deleteUserPlan } from '@/api'

const router = useRouter()
const loading = ref(true)
const plans = ref<any[]>([])

function goalLabel(goal: string) {
  const map: Record<string, string> = { muscle: '增肌', fatloss: '减脂', strength: '力量', endurance: '耐力' }
  return map[goal] || goal
}

async function loadPlans() {
  loading.value = true
  try {
    const res = await getUserPlans()
    plans.value = res.data.items
  } catch {
    plans.value = []
  } finally {
    loading.value = false
  }
}

async function removePlan(id: number) {
  try {
    await deleteUserPlan(id)
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
.mpl-list { display: flex; flex-direction: column; gap: 12px; }
.mpl-item {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  background: #EAF6F2; border: 1px solid rgba(12, 216, 160, 0.18);
  border-radius: 10px; padding: 14px 18px;
}
.mpl-info { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.mpl-name { font-size: 14px; font-weight: 500; color: var(--clr-dark); }
.mpl-tag {
  font-size: 11px; color: var(--clr-gold-dark);
  border: 1px solid rgba(12, 216, 160, 0.4); border-radius: 6px; padding: 2px 8px;
}
.mpl-meta { font-size: 12px; color: var(--clr-gray); }
.mpl-actions { flex-shrink: 0; }
.btn-outline--danger { color: #B96A5E; border-color: rgba(185, 106, 94, 0.45); }
.btn-outline--danger:hover { background: rgba(185, 106, 94, 0.08); }
</style>
