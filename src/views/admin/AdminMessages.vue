<template>
  <div class="admin-page">
    <div class="admin-page__toolbar">
      <span class="admin-page__count">鍏?{{ total }} 鏉＄暀瑷€</span>
    </div>
    <el-table :data="messages" stripe style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="subject" label="主题" width="100" />
      <el-table-column label="留言内容" min-width="200">
        <template #default="{ row }">
          <span style="color:#666;font-size:13px;">{{ row.message.length > 50 ? row.message.slice(0,50) + "..." : row.message }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_read ? 'info' : 'warning'" size="small">{{ row.is_read ? "已读" : "未读" }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="160">
        <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace("T"," ") }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-button v-if="!row.is_read" size="small" type="primary" link @click="markRead(row.id)">标为已读</el-button>
          <span v-else style="color:#ccc;font-size:12px;">已处理</span>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="total > 0" style="margin-top:16px;text-align:right;">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="load" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getAdminMessages, markMessageRead } from "@/api"
import { ElMessage } from "element-plus"

const messages = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(true)

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const res = await getAdminMessages(page.value)
    messages.value = res.data.items
    total.value = res.data.total
  } catch { /* */ }
  finally { loading.value = false }
}

async function markRead(id: number) {
  try {
    await markMessageRead(id)
    ElMessage.success("已标为已读")
    load()
  } catch { /* */ }
}
</script>

<style scoped>
.admin-page__toolbar { margin-bottom: 16px; display: flex; align-items: center; gap: 12px; }
.admin-page__count { font-size: 13px; color: #999; }
:deep(.el-table th) { background: #fafafa !important; color: #555; font-weight: 500; font-size: 13px; }
</style>

