<template>
  <div class="coach-layout">
    <!-- Sidebar -->
    <aside class="coach-sidebar">
      <div class="coach-sidebar__brand">
        <span class="coach-sidebar__logo">C</span>
        <span class="coach-sidebar__title">教练工作台</span>
      </div>
      <nav class="coach-sidebar__nav">
        <router-link v-for="item in menuItems" :key="item.path" :to="item.path"
          class="coach-sidebar__link"
          :class="{ 'is-active': route.path === item.path }">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
        <span class="coach-sidebar__link is-disabled" title="M3 即将上线">
          <el-icon><UserFilled /></el-icon>
          <span>学员管理</span>
          <em class="coach-sidebar__soon">即将上线</em>
        </span>
      </nav>
      <div class="coach-sidebar__footer">
        <router-link to="/profile" class="coach-sidebar__link">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </router-link>
        <router-link to="/" class="coach-sidebar__link">
          <el-icon><HomeFilled /></el-icon>
          <span>返回前台</span>
        </router-link>
      </div>
    </aside>

    <!-- Main -->
    <div class="coach-main">
      <header class="coach-header">
        <h2 class="coach-header__title">{{ pageTitle }}</h2>
        <div class="coach-header__user">
          <el-tag type="success" size="small" effect="plain">认证教练</el-tag>
          <span>{{ user?.nickname || "教练" }}</span>
        </div>
      </header>
      <main class="coach-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue"
import { useRoute } from "vue-router"
import { getUser } from "@/api"
import { DataBoard, User, UserFilled, HomeFilled } from "@element-plus/icons-vue"

const route = useRoute()
const user = ref(getUser())

const pageTitle = computed(() => {
  const m: Record<string, string> = {
    "/coach/dashboard": "工作台概览",
    "/coach/profile": "我的教练资料",
  }
  return m[route.path] || "教练工作台"
})

const menuItems = [
  { path: "/coach/dashboard", label: "工作台概览", icon: "DataBoard" },
  { path: "/coach/profile", label: "我的教练资料", icon: "Notebook" },
]
</script>

<style scoped>
.coach-layout { display: flex; min-height: 100vh; background: #f5f5f5; }
.coach-sidebar {
  width: 220px; background: #0f1f1a; display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; height: 100vh; z-index: 100;
}
.coach-sidebar__brand {
  display: flex; align-items: center; gap: 10px; padding: 24px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.coach-sidebar__logo {
  font-family: "Playfair Display", serif; font-size: 24px; font-weight: 600;
  color: #0CD8A0; font-style: italic;
}
.coach-sidebar__title { font-size: 14px; color: #f5f0e8; letter-spacing: 1px; }
.coach-sidebar__nav { flex: 1; padding: 12px 0; display: flex; flex-direction: column; gap: 2px; }
.coach-sidebar__link {
  display: flex; align-items: center; gap: 10px; padding: 12px 20px;
  font-size: 13px; color: #9db3ac; text-decoration: none; transition: all 0.2s;
  letter-spacing: 0.5px; cursor: pointer;
}
.coach-sidebar__link:hover { color: #0CD8A0; background: rgba(255,255,255,0.03); }
.coach-sidebar__link.is-active { color: #0CD8A0; background: rgba(12,216,160,0.08); }
.coach-sidebar__link.is-disabled { opacity: 0.55; cursor: not-allowed; }
.coach-sidebar__soon {
  margin-left: auto; font-size: 10px; font-style: normal; color: #6d837c;
  border: 1px solid #2c443c; border-radius: 8px; padding: 1px 6px;
}
.coach-sidebar__footer { border-top: 1px solid rgba(255,255,255,0.06); padding: 8px 0; }
.coach-main { margin-left: 220px; flex: 1; display: flex; flex-direction: column; min-width: 0; }
.coach-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 32px; background: #fff; border-bottom: 1px solid #eee;
  position: sticky; top: 0; z-index: 50;
}
.coach-header__title { font-size: 18px; font-weight: 500; color: #222; }
.coach-header__user { display: flex; align-items: center; gap: 12px; font-size: 13px; color: #666; }
.coach-content { padding: 24px 32px; flex: 1; min-width: 0; }
</style>
