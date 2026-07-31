<template>
  <div class="admin-dashboard">
    <div v-if="loading" style="text-align:center;padding:80px;color:#999;">加载中...</div>
    <template v-else>
      <div class="stats-grid">
        <div v-for="s in stats" :key="s.key" class="stat-card">
          <div class="stat-card__icon" :style="{ background: s.bg }">
            <el-icon :size="24"><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">{{ s.value }}</span>
            <span class="stat-card__label">{{ s.label }}</span>
          </div>
        </div>
      </div>
      <div class="dashboard-hint" style="margin-top:48px;padding:24px;background:#fff;border:1px solid #eee;">
        <h3 style="font-size:15px;font-weight:500;margin-bottom:12px;color:#333;">快捷入口</h3>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <router-link to="/admin/messages" class="quick-link">查看留言</router-link>
          <router-link to="/admin/users" class="quick-link">用户列表</router-link>
          <router-link to="/admin/exercises" class="quick-link">动作库</router-link>
          <router-link to="/admin/plans" class="quick-link">训练计划</router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getAdminDashboard } from "@/api"
import { Message, User, Notebook, List } from "@element-plus/icons-vue"

const loading = ref(true)
const stats = ref<{ key: string; icon: any; label: string; value: number; bg: string }[]>([])

onMounted(async () => {
  try {
    const res = await getAdminDashboard()
    const d = res.data
    stats.value = [
      { key: "messages", icon: "Message", label: "留言总数", value: d.messages, bg: "rgba(201,169,110,0.12)" },
      { key: "unread", icon: "Message", label: "未读留言", value: d.unread_messages, bg: "rgba(192,57,43,0.1)" },
      { key: "users", icon: "User", label: "注册用户", value: d.users, bg: "rgba(52,152,219,0.1)" },
      { key: "exercises", icon: "Notebook", label: "动作数量", value: d.exercises, bg: "rgba(46,204,113,0.1)" },
      { key: "plans", icon: "List", label: "训练计划", value: d.plans, bg: "rgba(155,89,182,0.1)" },
    ]
  } catch { /* ignore */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.stat-card {
  display: flex; align-items: center; gap: 16px;
  padding: 24px; background: #fff; border: 1px solid #eee;
}
.stat-card__icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-card__info { display: flex; flex-direction: column; gap: 2px; }
.stat-card__value { font-size: 28px; font-weight: 500; color: #222; font-family: "Playfair Display", serif; }
.stat-card__label { font-size: 12px; color: #999; letter-spacing: 0.5px; }
.quick-link {
  padding: 10px 20px; border: 1px solid #e0e0e0; text-decoration: none;
  font-size: 13px; color: #666; transition: all 0.2s;
}
.quick-link:hover { border-color: #c9a96e; color: #c9a96e; }
</style>
