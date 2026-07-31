<template>
  <div class="admin-page">
    <div class="admin-page__toolbar">
      <span class="admin-page__count">共 {{ total }} 位用户</span>
    </div>
    <el-table :data="users" stripe style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="nickname" label="昵称" width="130" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column label="角色" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">{{ row.is_admin ? "管理员" : "用户" }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? "正常" : "禁用" }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="注册时间" width="160">
        <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace("T"," ") }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-button v-if="!row.is_admin" :type="row.is_active ? 'warning' : 'success'" size="small" @click="toggleStatus(row)" :disabled="togglingId === row.id">
            {{ row.is_active ? "禁用" : "启用" }}
          </el-button>
          <span v-else style="color:#ccc;font-size:12px;">-</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getAdminUsers, toggleUserStatus } from "@/api"
import { ElMessage } from "element-plus"

const users = ref<any[]>([])
const total = ref(0)
const loading = ref(true)
const togglingId = ref<number | null>(null)

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const res = await getAdminUsers()
    users.value = res.data.items
    total.value = res.data.total
  } catch { /* */ }
  finally { loading.value = false }
}

async function toggleStatus(user: any) {
  togglingId.value = user.id
  try {
    await toggleUserStatus(user.id)
    ElMessage.success(user.is_active ? "已禁用" : "已启用")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message?.includes("\\u8bf7\\u5148\\u767b\\u5f55") ? "登录已过期，请刷新页面后重新登录" : (e?.message || "操作失败"))
  } finally {
    togglingId.value = null
  }
}
</script>

