<template>
  <aside class="p-sidebar p-card">
    <div class="p-sidebar__head">
      <span class="p-sidebar__label">MY CENTER</span>
      <h3 class="p-sidebar__title">个人中心</h3>
    </div>
    <nav class="p-sidebar__menu">
      <button
        v-for="item in items"
        :key="item.key"
        class="p-sidebar__item"
        :class="{ 'is-active': active === item.key }"
        @click="emit('select', item.key)"
      >
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<script setup lang="ts">
defineProps<{ active: string }>()

const emit = defineEmits<{
  (e: 'select', key: string): void
}>()

const items = [
  { key: 'basic', label: '基础资料', icon: 'User' },
  { key: 'body', label: '我的身材档案', icon: 'DataAnalysis' },
  { key: 'diet', label: 'AI饮食方案库', icon: 'Bowl' },
  { key: 'plans', label: '我的训练计划', icon: 'Calendar' },
  { key: 'weekly', label: '饮食打卡周报', icon: 'DocumentChecked' },
  { key: 'prefs', label: '系统偏好设置', icon: 'Setting' },
]
</script>

<style scoped>
.p-sidebar { position: sticky; top: 24px; padding: 24px 18px; }
.p-sidebar__head { padding: 4px 10px 18px; border-bottom: 1px solid rgba(184, 156, 102, 0.2); margin-bottom: 14px; }
.p-sidebar__label { font-size: 10px; letter-spacing: 3px; color: var(--clr-gold); display: block; margin-bottom: 6px; }
.p-sidebar__title { font-size: 17px; font-weight: 500; color: var(--clr-dark); }
.p-sidebar__menu { display: flex; flex-direction: column; gap: 4px; }
.p-sidebar__item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 14px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: var(--clr-gray);
  cursor: pointer;
  text-align: left;
  transition: all 0.25s ease;
}
.p-sidebar__item .el-icon { color: var(--clr-gray-light); transition: color 0.25s ease; }
.p-sidebar__item:hover { background: rgba(184, 156, 102, 0.08); color: var(--clr-gold-dark); }
.p-sidebar__item.is-active {
  background: linear-gradient(135deg, #C6A878, #B89C66);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(184, 156, 102, 0.28);
}
.p-sidebar__item.is-active .el-icon { color: #FFFFFF; }
</style>
