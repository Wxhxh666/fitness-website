<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="admin-sidebar">
      <div class="admin-sidebar__brand">
        <span class="admin-sidebar__logo">F</span>
        <span class="admin-sidebar__title">FITLUXE 管理</span>
      </div>
      <nav class="admin-sidebar__nav">
        <router-link v-for="item in menuItems" :key="item.path" :to="item.path"
          class="admin-sidebar__link"
          :class="{ 'is-active': currentRoute.startsWith(item.path) }">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="admin-sidebar__footer">
        <router-link to="/" class="admin-sidebar__link">
          <el-icon><HomeFilled /></el-icon>
          <span>返回前台</span>
        </router-link>
      </div>
    </aside>

    <!-- Main -->
    <div class="admin-main">
      <header class="admin-header">
        <h2 class="admin-header__title">{{ pageTitle }}</h2>
        <div class="admin-header__user">
          <span>{{ user?.nickname || "用户" }}</span>
          <button class="admin-header__logout" @click="logout">退出</button>
        </div>
      </header>
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { getUser, removeToken } from "@/api"
import {
  HomeFilled, Message, User, TrendCharts,
  List, Notebook, DataBoard
} from "@element-plus/icons-vue"

const route = useRoute()
const router = useRouter()
const user = ref(getUser())

const currentRoute = computed(() => route.path)

const pageTitle = computed(() => {
  const m: Record<string, string> = {
    "/admin": "控制台",
    "/admin/dashboard": "控制台",
    "/admin/messages": "留言管理",
    "/admin/users": "用户管理",
    "/admin/exercises": "动作管理",
    "/admin/plans": "计划管理",
  }
  return m[route.path] || "管理后台"
})

const menuItems = [
  { path: "/admin/dashboard", label: "控制台", icon: "DataBoard" },
  { path: "/admin/messages", label: "留言管理", icon: "Message" },
  { path: "/admin/users", label: "用户管理", icon: "User" },
  { path: "/admin/exercises", label: "动作管理", icon: "Notebook" },
  { path: "/admin/plans", label: "计划管理", icon: "List" },
  { path: "/admin/review", label: "申请审核", icon: "TrendCharts" },
]

function logout() {
  removeToken()
  router.push("/login")
}
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; background: #f5f5f5; }
.admin-sidebar {
  width: 220px; background: #1a1a1a; display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; height: 100vh; z-index: 100;
}
.admin-sidebar__brand {
  display: flex; align-items: center; gap: 10px; padding: 24px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.admin-sidebar__logo {
  font-family: "Playfair Display", serif; font-size: 24px; font-weight: 600;
  color: #c9a96e; font-style: italic;
}
.admin-sidebar__title { font-size: 14px; color: #f5f0e8; letter-spacing: 1px; }
.admin-sidebar__nav { flex: 1; padding: 12px 0; display: flex; flex-direction: column; gap: 2px; }
.admin-sidebar__link {
  display: flex; align-items: center; gap: 10px; padding: 12px 20px;
  font-size: 13px; color: #aaa; text-decoration: none; transition: all 0.2s;
  letter-spacing: 0.5px;
}
.admin-sidebar__link:hover { color: #c9a96e; background: rgba(255,255,255,0.03); }
.admin-sidebar__link.is-active { color: #c9a96e; background: rgba(201,169,110,0.08); }
.admin-sidebar__footer { border-top: 1px solid rgba(255,255,255,0.06); padding: 8px 0; }
.admin-main { margin-left: 220px; flex: 1; display: flex; flex-direction: column; }
.admin-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 32px; background: #fff; border-bottom: 1px solid #eee;
  position: sticky; top: 0; z-index: 50;
}
.admin-header__title { font-size: 18px; font-weight: 500; color: #222; }
.admin-header__user { display: flex; align-items: center; gap: 16px; font-size: 13px; color: #666; }
.admin-header__logout {
  padding: 6px 14px; background: none; border: 1px solid #ddd;
  font-size: 12px; cursor: pointer; color: #666; transition: all 0.2s;
}
.admin-header__logout:hover { border-color: #c9a96e; color: #c9a96e; }
.admin-content { padding: 24px 32px; flex: 1; }
</style>

