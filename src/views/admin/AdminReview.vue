<template>
  <div class="admin-page">
    <div class="admin-page__toolbar">
      <el-radio-group v-model="statusFilter" @change="load">
        <el-radio-button value="pending">待审核</el-radio-button>
        <el-radio-button value="approved">已通过</el-radio-button>
        <el-radio-button value="rejected">已拒绝</el-radio-button>
      </el-radio-group>
    </div>
    <el-table :data="items" stripe v-loading="loading" @row-click="showDetail" style="cursor:pointer;">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="用户" width="180">
        <template #default="{ row }">{{ row.user_nickname || row.user_email }}</template>
      </el-table-column>
      <el-table-column prop="field_name" label="字段" width="100" />
      <el-table-column label="旧值" width="150">
        <template #default="{ row }">{{ row.old_value || "-" }}</template>
      </el-table-column>
      <el-table-column label="申请值" width="150">
        <template #default="{ row }">{{ row.new_value }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'" size="small">
            {{ row.status === 'pending' ? '待审核' : row.status === 'approved' ? '已通过' : '已拒绝' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="160">
        <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace("T"," ") }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" type="success" @click.stop="handleAction(row.id, 'approve')">通过</el-button>
            <el-button size="small" type="danger" @click.stop="handleAction(row.id, 'reject')">拒绝</el-button>
          </template>
          <span v-else style="color:#ccc;font-size:12px;">-</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getReviewRequests, approveReview, rejectReview } from "@/api"
import { ElMessage, ElMessageBox } from "element-plus"

const items = ref<any[]>([])
const loading = ref(true)
const statusFilter = ref("pending")

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const res = await getReviewRequests(statusFilter.value)
    items.value = res.data.items
  } catch { /* */ }
  finally { loading.value = false }
}

function showDetail(row: any) {
  ElMessageBox.alert(
    `<div style="font-size:13px;line-height:2;">
      <p><b>用户：</b>${row.user_nickname || row.user_email}</p>
      <p><b>字段：</b>${row.field_name === "nickname" ? "昵称" : "头像"}</p>
      <p><b>旧值：</b>${row.old_value || "-"}</p>
      <p><b>申请值：</b>${row.new_value}</p>
      <p><b>时间：</b>${row.created_at?.slice(0,16)?.replace("T"," ")}</p>
    </div>`,
    "申请详情",
    { dangerouslyUseHTMLString: true }
  )
}

async function handleAction(id: number, action: string) {
  try {
    if (action === "approve") await approveReview(id)
    else await rejectReview(id)
    ElMessage.success(action === "approve" ? "已通过审核" : "已拒绝")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  }
}
</script>

<style scoped>
.admin-page__toolbar { margin-bottom: 16px; }
:deep(.el-table th) { background: #fafafa !important; color: #555; font-weight: 500; font-size: 13px; }
</style>



