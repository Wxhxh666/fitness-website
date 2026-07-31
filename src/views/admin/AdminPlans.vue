<template>
  <div class="admin-page">
    <div class="admin-page__toolbar">
      <span class="admin-page__count">共 {{ total }} 个计划</span>
    </div>
    <el-table :data="plans" stripe style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="计划名称" width="160" />
      <el-table-column prop="badge" label="标签" width="80" />
      <el-table-column prop="duration" label="周期" width="80" />
      <el-table-column prop="frequency" label="频次" width="100" />
      <el-table-column prop="difficulty_label" label="难度" width="80" />
      <el-table-column prop="goal" label="目标" width="100" />
      <el-table-column label="描述" min-width="200">
        <template #default="{ row }">{{ row.desc || row.description }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? "上架" : "下架" }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getAdminPlans } from "@/api"

const plans = ref<any[]>([])
const total = ref(0)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getAdminPlans()
    plans.value = res.data.items
    total.value = res.data.total
  } catch { /* */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.admin-page__toolbar { margin-bottom: 16px; }
.admin-page__count { font-size: 13px; color: #999; }
:deep(.el-table th) { background: #fafafa !important; color: #555; font-weight: 500; font-size: 13px; }
</style>


