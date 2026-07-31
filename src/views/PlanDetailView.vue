<template>
  <div class="plan-detail-page">
    <section class="page-hero" v-if="plan">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">TRAINING PROGRAM</span>
        <h1 class="page-hero__title">{{ plan.name }}</h1>
        <div class="plan-detail__meta">
          <span class="plan-detail__badge">{{ plan.badge }}</span>
          <span class="plan-detail__info">{{ plan.duration }} · {{ plan.frequency }}</span>
          <span class="plan-detail__info plan-detail__diff" :class="`diff--${plan.difficulty}`">{{ plan.difficulty_label }}</span>
        </div>
        <p class="plan-detail__desc">{{ plan.desc || plan.description }}</p>
        <div class="plan-detail__tags" v-if="plan.focus_tags || plan.focus">
          <span v-for="t in (plan.focus_tags || plan.focus)" :key="t" class="plan-detail__tag">{{ t }}</span>
        </div>
      </div>
    </section>

    <section class="plan-schedule section section-light" v-if="plan?.weekly_schedule">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">WEEKLY SCHEDULE</p>
          <h2 class="section-title">每周训练安排</h2>
          <div class="gold-divider"></div>
        </div>
        <div class="schedule__list">
          <div v-for="(day, idx) in plan.weekly_schedule" :key="idx" class="schedule-day">
            <div class="schedule-day__header">
              <span class="schedule-day__name">{{ day.day }}</span>
              <span class="schedule-day__focus">{{ day.focus }}</span>
            </div>
            <div class="schedule-day__exercises">
              <div v-for="ex in day.exercises" :key="ex.exercise_id" class="schedule-exercise">
                <span class="schedule-exercise__name">{{ ex.name }}</span>
                <span class="schedule-exercise__specs">{{ ex.sets }}组 × {{ ex.reps }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" v-else-if="!loading">
      <div class="container text-center">
        <p style="color:var(--clr-gray);font-size:15px;">该计划暂无详细周训安排</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPlanDetail } from '@/api'

const route = useRoute()
const router = useRouter()
const plan = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  const id = route.params.id
  if (!id) { router.push('/plans'); return }
  try {
    const res = await getPlanDetail(Number(id))
    plan.value = res.data
  } catch {
    plan.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-hero { position:relative; padding:160px 0 80px; background:var(--clr-black); overflow:hidden; }
.page-hero__bg { position:absolute; inset:0; background:radial-gradient(ellipse at 30% 60%,rgba(201,169,110,0.05),transparent 50%); }
.page-hero__content { position:relative; z-index:1; }
.page-hero__label { font-size:11px; letter-spacing:4px; color:var(--clr-gold); margin-bottom:16px; display:inline-block; }
.page-hero__title { font-family:var(--font-display); font-size:48px; font-weight:400; color:var(--clr-cream); margin-bottom:16px; letter-spacing:2px; }
.plan-detail__meta { display:flex; gap:16px; align-items:center; margin-bottom:16px; flex-wrap:wrap; }
.plan-detail__badge { font-size:10px; letter-spacing:2px; padding:4px 14px; color:var(--clr-gold); border:1px solid var(--clr-gold); }
.plan-detail__info { font-size:13px; color:var(--clr-gray-light); letter-spacing:1px; }
.plan-detail__diff.diff--beginner { color:#6b8e6b; } .plan-detail__diff.diff--intermediate { color:#c9a96e; } .plan-detail__diff.diff--advanced { color:#c0392b; }
.plan-detail__desc { font-size:15px; color:var(--clr-gray-light); line-height:1.8; max-width:600px; }
.plan-detail__tags { display:flex; gap:8px; margin-top:16px; flex-wrap:wrap; }
.plan-detail__tag { font-size:11px; letter-spacing:1px; padding:4px 12px; background:rgba(255,255,255,0.05); color:var(--clr-gray); }

.schedule__list { max-width:720px; margin:48px auto 0; display:flex; flex-direction:column; gap:16px; }
.schedule-day { border:1px solid rgba(0,0,0,0.05); background:var(--clr-white); overflow:hidden; }
.schedule-day__header { display:flex; align-items:center; gap:16px; padding:16px 24px; background:var(--clr-bg-section); border-bottom:1px solid rgba(0,0,0,0.04); }
.schedule-day__name { font-family:var(--font-display); font-size:16px; font-weight:400; color:var(--clr-gold); letter-spacing:1px; min-width:48px; }
.schedule-day__focus { font-size:13px; color:var(--clr-gray); letter-spacing:1px; }
.schedule-day__exercises { padding:8px 24px; }
.schedule-exercise { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid rgba(0,0,0,0.03); }
.schedule-exercise:last-child { border-bottom:none; }
.schedule-exercise__name { font-size:14px; color:var(--clr-dark); }
.schedule-exercise__specs { font-size:12px; color:var(--clr-gray); letter-spacing:0.5px; }

@media (max-width:768px) {
  .page-hero__title { font-size:32px; }
}
</style>
