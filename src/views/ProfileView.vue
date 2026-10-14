<template>
  <div class="profile-page">
    <!-- ============ 顶部黑色标题横幅 ============ -->
    <section class="profile-hero">
      <div class="profile-hero__bg"></div>
      <div class="profile-hero__content container">
        <span class="profile-hero__label">MY PROFILE</span>
        <h1 class="profile-hero__title">个人中心</h1>
        <p class="profile-hero__desc">管理个人资料、身材数据、饮食方案与系统偏好</p>
      </div>
    </section>

    <!-- ============ 主体：左侧菜单 + 右侧多卡片内容区 ============ -->
    <section class="profile-body section">
      <div class="container profile-layout">
        <ProfileSidebar :active="activeMenu" @select="activeMenu = $event" />

        <main class="profile-content">
          <BasicInfoPanel v-show="activeMenu === 'basic'" />
          <DashboardPanel v-show="activeMenu === 'body'" />
          <DietPlanLibraryPanel v-show="activeMenu === 'diet'" />
          <MyPlansPanel v-show="activeMenu === 'plans'" />
          <WeeklyBriefPanel v-show="activeMenu === 'weekly'" />
          <PreferencesPanel v-show="activeMenu === 'prefs'" />
        </main>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ProfileSidebar from '@/components/profile/ProfileSidebar.vue'
import BasicInfoPanel from '@/components/profile/BasicInfoPanel.vue'
import DashboardPanel from '@/components/profile/DashboardPanel.vue'
import DietPlanLibraryPanel from '@/components/profile/DietPlanLibraryPanel.vue'
import MyPlansPanel from '@/components/profile/MyPlansPanel.vue'
import WeeklyBriefPanel from '@/components/profile/WeeklyBriefPanel.vue'
import PreferencesPanel from '@/components/profile/PreferencesPanel.vue'

/** 当前激活的侧边菜单项 */
const activeMenu = ref('basic')
</script>

<style scoped>
/* ---------- 顶部黑色横幅 ---------- */
.profile-hero {
  position: relative;
  padding: 150px 0 72px;
  background: #0A0A0A;
  overflow: hidden;
}
.profile-hero__bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 30% 60%, rgba(12, 216, 160, 0.08), transparent 50%);
}
.profile-hero__content { position: relative; z-index: 1; }
.profile-hero__label {
  font-size: 11px;
  letter-spacing: 4px;
  color: #0CD8A0;
  margin-bottom: 16px;
  display: inline-block;
}
.profile-hero__title {
  font-family: var(--font-display);
  font-size: 46px;
  font-weight: 400;
  color: #F5F0E8;
  margin-bottom: 16px;
  letter-spacing: 2px;
}
.profile-hero__desc { font-size: 15px; color: #A9A29A; max-width: 520px; }

/* ---------- 主体布局 ---------- */
.profile-body { padding: 44px 0 90px; }
.profile-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 28px;
  align-items: start;
}
.profile-content { min-height: 480px; display: flex; flex-direction: column; gap: 24px; }

@media (max-width: 900px) {
  .profile-layout { grid-template-columns: 1fr; }
  .p-sidebar { position: static; }
}
@media (max-width: 768px) {
  .profile-hero { padding: 120px 0 56px; }
  .profile-hero__title { font-size: 32px; }
}
</style>
