<template>
  <section class="guest-notice">
    <div class="container">
      <div class="guest-notice__inner">
        <div class="guest-notice__icon"><el-icon :size="20"><Lock /></el-icon></div>
        <div class="guest-notice__text">
          <h3 class="guest-notice__title">{{ title }}</h3>
          <p class="guest-notice__desc">{{ desc }}</p>
        </div>
        <div class="guest-notice__actions">
          <button class="btn-primary" @click="onLogin">登录 / 注册</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { goLogin } from '@/utils/authGuard'

withDefaults(defineProps<{
  title?: string
  desc?: string
}>(), {
  title: '登录后即可保存并追踪你的身体数据',
  desc: '当前为访客模式，计算器可以正常使用；保存记录、目标管理与 AI 饮食方案需要登录。',
})

const route = useRoute()
const onLogin = () => goLogin(route.fullPath)
</script>

<style scoped>
.guest-notice { padding: 22px 0 0; }
.guest-notice__inner {
  display: flex; align-items: center; gap: 16px;
  padding: 16px 22px;
  background: rgba(12, 216, 160, 0.06);
  border: 1px solid rgba(12, 216, 160, 0.28);
  border-radius: 10px;
}
.guest-notice__icon {
  width: 38px; height: 38px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  background: rgba(12, 216, 160, 0.14);
  color: var(--clr-gold-dark);
}
.guest-notice__text { flex: 1; min-width: 0; }
.guest-notice__title { font-size: 14px; font-weight: 600; color: var(--clr-dark); margin-bottom: 3px; }
.guest-notice__desc { font-size: 12.5px; color: var(--clr-gray); line-height: 1.6; margin: 0; }
.guest-notice__actions { flex-shrink: 0; }
.guest-notice__actions .btn-primary { padding: 9px 20px; font-size: 13px; }

@media (max-width: 768px) {
  .guest-notice__inner { flex-direction: column; align-items: flex-start; gap: 10px; }
  .guest-notice__actions { width: 100%; }
  .guest-notice__actions .btn-primary { width: 100%; }
}
</style>
