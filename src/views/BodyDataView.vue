<template>
  <div class="bodydata-page">
    <!-- ============ 页面标题 ============ -->
    <PageHero label="BODY ANALYTICS" title="身体概览" desc="个人基础档案与核心指标总览，快速掌握身体状态。" />

    <!-- ============ 个人基础档案 ============ -->
    <ProfileStrip
      :profile="profile"
      :unit="unit"
      :activity-options="activityOptions"
      @save="handleSave"
      @update:unit="unit = $event"
    />

    <!-- ============ 核心指标总览 ============ -->
    <MetricOverview :metrics="topMetrics" />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHero from '@/components/PageHero.vue'
import ProfileStrip from '@/components/bodydata/ProfileStrip.vue'
import MetricOverview from '@/components/bodydata/MetricOverview.vue'
import { useBodyData } from '@/composables/useBodyData'

const { unit, profile, activityOptions, topMetrics, loadAll, saveProfile } = useBodyData()

async function handleSave() {
  try {
    await saveProfile()
    ElMessage.success('档案已保存')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

onMounted(() => loadAll())
</script>

<style scoped>
/* 主题与动效由 src/styles/global.css 的 .bodydata-page 提供 */
</style>
