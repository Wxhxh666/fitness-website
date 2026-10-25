<template>
  <div class="bodydata-page">
    <!-- ============ 页面标题 ============ -->
    <PageHero label="AI DIET PLAN" title="AI 智能饮食规划" desc="结合身体指标、健身目标与饮食偏好，生成科学饮食方案，配套每日打卡与每周复盘。" />

    <GuestNotice v-if="!authed" />

    <!-- ============ AI 智能饮食规划 ============ -->
    <section class="ai-diet section section-dark">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">AI DIET PLAN</p>
          <h2 class="section-title">AI 智能饮食规划</h2>
          <div class="gold-divider"></div>
          <p class="section-desc" style="color: var(--clr-gray)">结合身体指标、健身目标与饮食偏好生成科学饮食方案；配套每日打卡与每周复盘，并把数据同步到「计划制定」页，形成完整健身闭环。</p>
        </div>
        <DietPlanner
          :records="records"
          :results="results"
          :profile="profile"
          :activity-options="activityOptions"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import PageHero from '@/components/PageHero.vue'
import GuestNotice from '@/components/bodydata/GuestNotice.vue'
import DietPlanner from '@/components/bodydata/DietPlanner.vue'
import { useBodyData } from '@/composables/useBodyData'

const { records, results, profile, activityOptions, authed, loadAll } = useBodyData()

onMounted(() => loadAll())
</script>

<style scoped>
.ai-diet { padding: 100px 0; }
</style>
