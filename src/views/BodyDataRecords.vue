<template>
  <div class="bodydata-page">
    <!-- ============ 页面标题 ============ -->
    <PageHero label="DATA MANAGEMENT" title="数据管理" desc="围度记录、身材目标与历史数据存档，集中管理你的全部身体数据。" />

    <!-- ============ 数据管理入口 ============ -->
    <DataEntryCards
      :meas-latest-text="measLatestText"
      :goal="goal"
      :record-count="recordCount"
      @open-measurements="measDialog.visible = true"
      @open-goals="goalDialog.visible = true"
      @open-history="historyDialog.visible = true"
    />

    <!-- ============ 对话框 ============ -->
    <MeasurementDialog v-model:visible="measDialog.visible" :records="records" :unit="unit" @saved="loadRecords" />
    <GoalManagerDialog
      v-model:visible="goalDialog.visible"
      :records="records"
      :goal="goal"
      :goal-saved-at="goalSavedAt"
      :unit="unit"
      @saved="onGoalSaved"
      @cleared="onGoalCleared"
    />
    <HistoryArchiveDialog v-model:visible="historyDialog.visible" :records="records" :unit="unit" @changed="loadRecords" />
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import PageHero from '@/components/PageHero.vue'
import DataEntryCards from '@/components/bodydata/DataEntryCards.vue'
import MeasurementDialog from '@/components/bodydata/MeasurementDialog.vue'
import GoalManagerDialog from '@/components/bodydata/GoalManagerDialog.vue'
import HistoryArchiveDialog from '@/components/bodydata/HistoryArchiveDialog.vue'
import { useBodyData } from '@/composables/useBodyData'

const {
  unit,
  records,
  goal,
  goalSavedAt,
  measLatestText,
  recordCount,
  loadAll,
  loadRecords,
  onGoalSaved,
  onGoalCleared,
} = useBodyData()

const measDialog = reactive({ visible: false })
const goalDialog = reactive({ visible: false })
const historyDialog = reactive({ visible: false })

onMounted(() => loadAll())
</script>

<style scoped>
/* 主题与动效由 src/styles/global.css 的 .bodydata-page 提供 */
</style>
