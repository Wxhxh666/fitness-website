<template>
  <header :class="['nav-header', { 'nav-header--scrolled': isScrolled, 'nav-header--transparent': !isScrolled && isHome }]">
    <div class="nav-header__inner container">
      <router-link to="/" class="nav-header__logo">
        <span class="nav-header__logo-mark">F</span>
        <span class="nav-header__logo-text">FITLUXE</span>
      </router-link>

      <nav class="nav-header__menu">
        <template v-for="item in menuItems" :key="item.path">
          <div
            v-if="item.path === '/body-data'"
            class="nav-header__item"
            @mouseenter="submenuOpen = true"
            @mouseleave="submenuOpen = false"
          >
            <router-link :to="item.path" class="nav-header__link" :class="{ 'is-active': isBodyDataActive }">
              <span class="nav-header__link-indicator"></span>
              {{ item.label }}
              <el-icon class="nav-header__caret" :class="{ 'is-open': submenuOpen }"><ArrowDown /></el-icon>
            </router-link>
            <transition name="submenu-fade">
              <div v-if="submenuOpen" class="nav-header__submenu">
                <router-link
                  v-for="s in bodyDataItems"
                  :key="s.path"
                  :to="s.path"
                  class="nav-header__submenu-item"
                  :class="{ 'is-active': currentRoute === s.path }"
                >{{ s.label }}</router-link>
              </div>
            </transition>
          </div>
          <router-link
            v-else
            :to="item.path"
            class="nav-header__link"
            :class="{ 'is-active': currentRoute === item.path }"
          >
            <span class="nav-header__link-indicator"></span>
            {{ item.label }}
          </router-link>
        </template>
      </nav>

      <div class="nav-header__actions">
        <template v-if="isLoggedIn">
          <div class="nav-header__avatar-wrap" @mouseenter="showDropdown=true" @mouseleave="showDropdown=false">
            <div class="nav-header__avatar">
              <img v-if="user?.avatar_url" :src="fullUrl(user.avatar_url)" class="nav-header__avatar-img" />
              <span v-else>{{ avatarLetter }}</span>
            </div>
            <transition name="dropdown-fade">
              <div v-if="showDropdown" class="nav-header__dropdown" @mouseenter="showDropdown=true" @mouseleave="showDropdown=false">
                <router-link to="/profile" class="nav-header__dropdown-item">个人中心</router-link>
                <router-link v-if="user?.is_coach" to="/coach/dashboard" class="nav-header__dropdown-item">教练工作台</router-link>
                <router-link v-if="user?.is_admin" to="/admin/dashboard" class="nav-header__dropdown-item">管理后台</router-link>
                <div class="nav-header__dropdown-divider"></div>
                <button class="nav-header__dropdown-item nav-header__dropdown-logout" @click="logout">退出</button>
              </div>
            </transition>
          </div>
        </template>
        <router-link v-else to="/login" class="nav-header__login-btn">
          <el-icon><User /></el-icon>
          <span>登录</span>
        </router-link>
      </div>

      <button class="nav-header__toggle" @click="mobileMenuOpen = !mobileMenuOpen">
        <span></span><span></span><span></span>
      </button>
    </div>

    <transition name="slide-fade">
      <div v-if="mobileMenuOpen" class="nav-header__mobile" @click.self="mobileMenuOpen = false">
        <template v-for="item in menuItems" :key="item.path">
          <router-link
            :to="item.path"
            class="nav-header__mobile-link"
            :class="{ 'is-active': item.path === '/body-data' ? isBodyDataActive : currentRoute === item.path }"
            @click="mobileMenuOpen = false"
          >{{ item.label }}</router-link>
          <div v-if="item.path === '/body-data'" class="nav-header__mobile-sub">
            <router-link
              v-for="s in bodyDataItems"
              :key="s.path"
              :to="s.path"
              class="nav-header__mobile-subitem"
              :class="{ 'is-active': currentRoute === s.path }"
              @click="mobileMenuOpen = false"
            >{{ s.label }}</router-link>
          </div>
        </template>
        <template v-if="isLoggedIn">
          <span class="nav-header__mobile-link" style="color:var(--clr-gold);border-bottom:none;">
            <el-icon><User /></el-icon> {{ user?.nickname || '用户' }}
          </span>
          <span class="nav-header__mobile-link" @click="logout(); mobileMenuOpen = false" style="cursor:pointer;">退出</span>
        </template>
        <router-link v-else to="/login" class="nav-header__mobile-link nav-header__mobile-login" @click="mobileMenuOpen = false">
          <el-icon><User /></el-icon> 登录
        </router-link>
      </div>
    </transition>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isLoggedIn as checkLogin, getUser, removeToken, API_BASE_URL } from '@/api'

const route = useRoute()
const isScrolled = ref(false)
const mobileMenuOpen = ref(false)
const showDropdown = ref(false)
const submenuOpen = ref(false)
const isLoggedIn = ref(checkLogin())
const user = ref(getUser())

/** 将后端返回的相对路径（/static/...）补全为完整 URL，否则会解析到前端端口导致 404 */
function fullUrl(path?: string) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return API_BASE_URL.replace(/\/api$/, '') + path
}

// Update auth state on route change (NavHeader is outside router-view)
watch(() => route.path, () => {
  isLoggedIn.value = checkLogin()
  user.value = getUser()
  submenuOpen.value = false
}, { immediate: false })
const router = useRouter()

function logout() {
  removeToken()
  isLoggedIn.value = checkLogin()
  user.value = getUser()
  router.push('/')
}

const menuItems = [
  { path: '/', label: '首页' },
  { path: '/exercises', label: '动作教学' },
  { path: '/plans', label: '计划制定' },
  { path: '/workouts', label: '运动记录' },
  { path: '/body-data', label: '身材数据管理' },
  { path: '/contact', label: '联系' },
]

const bodyDataItems = [
  { path: '/body-data', label: '身体概览' },
  { path: '/body-data/trends', label: '指标趋势' },
  { path: '/body-data/diet', label: 'AI 饮食' },
  { path: '/body-data/records', label: '数据管理' },
]
const isBodyDataActive = computed(() => route.path === '/body-data' || route.path.startsWith('/body-data/'))

const currentRoute = computed(() => route.path)
const isHome = computed(() => route.path === '/')
const avatarLetter = computed(() => {
  const n = user.value?.nickname || user.value?.email || "U"
  return n.charAt(0).toUpperCase()
})

const handleScroll = () => { isScrolled.value = window.scrollY > 80 }

onMounted(() => window.addEventListener('scroll', handleScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<style scoped>
.nav-header {
  position: fixed; top: 0; left: 0; width: 100%; z-index: 1000;
  background: rgba(13, 13, 13, 0.95);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  transition: var(--transition-default);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.nav-header--transparent {
  background: transparent; backdrop-filter: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.nav-header--scrolled {
  background: rgba(13, 13, 13, 0.98); backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(12, 216, 160, 0.15);
}
.nav-header__inner { display: flex; align-items: center; justify-content: space-between; height: 72px; }

.nav-header__logo { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.nav-header__logo-mark {
  font-family: var(--font-display); font-size: 24px; font-weight: 600;
  color: var(--clr-gold); font-style: italic;
}
.nav-header__logo-text {
  font-family: var(--font-display); font-size: 16px; font-weight: 400;
  letter-spacing: 3px; color: var(--clr-cream);
}

.nav-header__menu { display: flex; align-items: center; gap: 4px; }

.nav-header__link {
  position: relative; display: flex; align-items: center; gap: 6px;
  padding: 8px 18px;
  font-size: 13px; font-weight: 400; letter-spacing: 1.5px;
  color: var(--clr-gray-lighter); text-decoration: none;
  transition: var(--transition-default);
}
.nav-header__link-indicator {
  display: block; width: 4px; height: 4px; border-radius: 50%;
  background: transparent; transition: var(--transition-default);
}
.nav-header__link:hover { color: var(--clr-gold-light); }
.nav-header__link:hover .nav-header__link-indicator { background: var(--clr-gold); }
.nav-header__link.is-active { color: var(--clr-gold); }
.nav-header__link.is-active .nav-header__link-indicator { background: var(--clr-gold); }

/* ---------- 身材数据管理 下拉子菜单 ---------- */
.nav-header__item { position: relative; }
.nav-header__caret { width: 13px; height: 13px; transition: transform var(--transition-default); }
.nav-header__caret.is-open { transform: rotate(180deg); }
.nav-header__submenu {
  position: absolute; top: calc(100% + 14px); left: 50%; transform: translateX(-50%);
  min-width: 180px; padding: 8px;
  background: rgba(13, 20, 27, 0.98); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(12, 216, 160, 0.22); border-radius: 12px;
  box-shadow: 0 22px 54px rgba(0, 0, 0, 0.5); z-index: 1001;
}
.nav-header__submenu::before {
  content: ""; position: absolute; top: -16px; left: 0; right: 0; height: 16px;
}
.nav-header__submenu-item {
  display: block; padding: 10px 14px; font-size: 13px; letter-spacing: 1px;
  color: var(--clr-gray-lighter); text-decoration: none; border-radius: 8px; white-space: nowrap;
  transition: var(--transition-default);
}
.nav-header__submenu-item:hover { color: var(--clr-gold); background: rgba(12, 216, 160, 0.08); }
.nav-header__submenu-item.is-active { color: var(--clr-gold); background: rgba(12, 216, 160, 0.14); }

.submenu-fade-enter-active,
.submenu-fade-leave-active { transition: all 0.22s ease; }
.submenu-fade-enter-from,
.submenu-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(-8px); }

/* 移动端子菜单 */
.nav-header__mobile-sub { padding-left: 14px; }
.nav-header__mobile-subitem {
  display: block; padding: 10px 0 10px 12px; font-size: 13px; letter-spacing: 1px;
  color: var(--clr-gray); text-decoration: none; border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  transition: var(--transition-default);
}
.nav-header__mobile-subitem:hover,
.nav-header__mobile-subitem.is-active { color: var(--clr-gold); }

/* Login button */
.nav-header__actions { display: flex; align-items: center; }
.nav-header__login-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 20px;
  font-size: 13px; letter-spacing: 1px;
  color: var(--clr-gold); text-decoration: none;
  border: 1px solid var(--clr-gold);
  transition: var(--transition-default);
}
.nav-header__login-btn:hover {
  background: var(--clr-gold);
  color: var(--clr-white);
}

.nav-header__toggle {
  display: none; flex-direction: column; gap: 5px;
  background: none; border: none; cursor: pointer; padding: 8px;
}
.nav-header__toggle span {
  display: block; width: 22px; height: 1.5px;
  background: var(--clr-cream); transition: var(--transition-default);
}

.nav-header__mobile {
  position: fixed; top: 72px; left: 0; width: 100%;
  background: rgba(13, 13, 13, 0.98); backdrop-filter: blur(16px);
  padding: 20px 24px; display: flex; flex-direction: column; gap: 4px;
  border-bottom: 1px solid rgba(12, 216, 160, 0.15);
}
.nav-header__mobile-link {
  padding: 14px 0; font-size: 14px; letter-spacing: 1.5px;
  color: var(--clr-gray-lighter); text-decoration: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: var(--transition-default);
}
.nav-header__mobile-link:hover,
.nav-header__mobile-link.is-active { color: var(--clr-gold); }
.nav-header__mobile-login { color: var(--clr-gold); border-bottom: none; }

.slide-fade-enter-active { transition: all 0.3s ease; }
.slide-fade-leave-active { transition: all 0.2s ease; }
.slide-fade-enter-from,
.slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }

.nav-header__avatar-wrap { position:relative; }
.nav-header__avatar { width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#0CD8A0,#0CD8A0);display:flex;align-items:center;justify-content:center;color:#fff;font-size:15px;font-weight:500;cursor:pointer;overflow:hidden; }
.nav-header__avatar-img { width:100%;height:100%;object-fit:cover; }
.nav-header__dropdown { position:absolute;top:calc(100% + 8px);right:0;background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);min-width:140px;z-index:100; }
.nav-header__dropdown-item { display:block;padding:10px 18px;font-size:13px;color:#ccc;text-decoration:none;background:none;border:none;width:100%;text-align:left;cursor:pointer;font-family:inherit;transition:all .2s;letter-spacing:.5px; }
.nav-header__dropdown-item:hover { color:#0CD8A0;background:rgba(255,255,255,0.03); }
.nav-header__dropdown-divider { height:1px;background:rgba(255,255,255,0.06);margin:4px 0; }
.nav-header__dropdown-logout { color:#999; }
.nav-header__dropdown-logout:hover { color:#c0392b!important; }
.dropdown-fade-enter-active,.dropdown-fade-leave-active { transition:all .2s ease; }
.dropdown-fade-enter-from,.dropdown-fade-leave-to { opacity:0;transform:translateY(-4px); }
@media (max-width: 768px) {
  .nav-header__menu { display: none; }
  .nav-header__actions { display: none; }
  .nav-header__toggle { display: flex; }
}
</style>




