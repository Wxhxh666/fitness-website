<template>
  <div id="fitluxe-app">
    <template v-if="showChrome">
      <NavHeader />
    </template>
    <main class="main-content" :class="{ 'main-content--admin': isAdminRoute }">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <template v-if="showChrome">
      <FooterSection />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavHeader from '@/components/NavHeader.vue'
import FooterSection from '@/components/FooterSection.vue'

const route = useRoute()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
// 登录/注册页是独立整页布局，不显示站点导航栏与页脚
const isAuthRoute = computed(() => route.path === '/login')
const showChrome = computed(() => !isAdminRoute.value && !isAuthRoute.value)
</script>

<style scoped>
.main-content { min-height: 100vh; }
.main-content--admin { padding-top: 0; }
.page-fade-enter-active,
.page-fade-leave-active { transition: opacity 0.25s ease; }
.page-fade-enter-from,
.page-fade-leave-to { opacity: 0; }
</style>

<style scoped>
.main-content { min-height: 100vh; }
.main-content--admin { padding-top: 0; }
.page-fade-enter-active,
.page-fade-leave-active { transition: opacity 0.25s ease; }
.page-fade-enter-from,
.page-fade-leave-to { opacity: 0; }
</style>
