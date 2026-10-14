<template>
  <div class="bodydata-page">
    <!-- ============ 页面标题 ============ -->
    <PageHero label="METRICS & TRENDS" title="指标计算与趋势" desc="计算 BMI、体脂率、BMR、TDEE 等多维指标，跟踪历史身材数据趋势。" />

    <!-- ============ 指标计算与趋势 ============ -->
    <section class="analytics section section-light">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">METRICS &amp; TRENDS</p>
          <h2 class="section-title">指标计算与趋势</h2>
          <div class="gold-divider"></div>
          <p class="section-desc">左侧计算 BMI、体脂率、BMR、TDEE 等多维指标；右侧对照 BMI 参考标准，并查看历史身材数据趋势。</p>
        </div>
        <div class="analytics__grid">
          <BodyCalculator
            :profile="profile"
            :unit="unit"
            :activity-options="activityOptions"
            @calculated="onCalculated"
            @saved="loadRecords"
          />
          <TrendHistory :records="records" :unit="unit" @open-history="historyDialog.visible = true" />
        </div>
      </div>
    </section>

    <!-- ============ 历史数据存档弹窗 ============ -->
    <HistoryArchiveDialog v-model:visible="historyDialog.visible" :records="records" :unit="unit" @changed="loadRecords" />
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import PageHero from '@/components/PageHero.vue'
import BodyCalculator from '@/components/bodydata/BodyCalculator.vue'
import TrendHistory from '@/components/bodydata/TrendHistory.vue'
import HistoryArchiveDialog from '@/components/bodydata/HistoryArchiveDialog.vue'
import { useBodyData } from '@/composables/useBodyData'

const { unit, profile, records, activityOptions, onCalculated, loadAll, loadRecords } = useBodyData()
const historyDialog = reactive({ visible: false })

onMounted(() => loadAll())
</script>

<style scoped>
.analytics { padding: 100px 0; }
.analytics__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 56px; align-items: start; }

@media (max-width: 1024px) {
  .analytics__grid { grid-template-columns: 1fr; }
}
</style>
