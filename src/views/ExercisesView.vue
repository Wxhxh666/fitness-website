<template>
  <div class="exercises-page">
    <section class="page-hero">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">EXERCISE LIBRARY</span>
        <h1 class="page-hero__title">动作教学</h1>
        <p class="page-hero__desc">百种专业健身动作，高清演示与详细分解，助你精准发力。</p>
      </div>
    </section>

    <section class="exercises__body section section-light">
      <div class="container">
       <div class="exercises__tabs">
         <button v-for="cat in categories" :key="cat.key"
           :class="['tab-btn', { 'is-active': activeCategory === cat.key }]"
           @click="switchCategory(cat.key)"
          >
           <el-icon style="margin-right:6px;"><component :is="cat.icon" /></el-icon>{{ cat.label }}
         </button>
        </div>

        <div class="exercises__grid">
          <div v-for="(ex, index) in filteredExercises" :key="ex.name"
            class="exercise-card animate-in" :class="`animate-in-delay-${index % 4}`"
          >
            <div class="exercise-card__image">
              <img v-if="ex.cover_url" :src="fullUrl(ex.cover_url)" class="exercise-card__cover" />
              <div v-else class="exercise-card__img-placeholder" :style="{ background: ex.gradient }">
                <span class="exercise-card__img-icon">{{ ex.icon }}</span>
              </div>
            </div>
            <div class="exercise-card__body">
              <div class="exercise-card__tag">{{ ex.categoryLabel }}</div>
              <h3 class="exercise-card__title">{{ ex.name }}</h3>
              <p class="exercise-card__desc">{{ ex.desc }}</p>
              <div class="exercise-card__meta">
                <span class="exercise-card__difficulty" :class="`diff--${ex.difficulty}`">
                  {{ ex.difficulty === 'beginner' ? '入门' : ex.difficulty === 'intermediate' ? '中级' : '高级' }}
                </span>
                <span class="exercise-card__target"><el-icon><Timer /></el-icon>{{ ex.duration }}</span>              <span v-if="ex.video_url" class="exercise-card__video" @click.stop="openVideo(ex.video_url)">
                <el-icon><VideoCamera /></el-icon> 教学视频
              </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Timer, VideoCamera } from '@element-plus/icons-vue'
 import { getExerciseCategories, getExercises } from '@/api'

const activeCategory = ref('chest')
const categories = ref<any[]>([])
const exercises = ref<any[]>([])
const loading = ref(true)

async function loadCategories() {
  try {
    const res = await getExerciseCategories()
    categories.value = res.data
    if (categories.value.length > 0) activeCategory.value = categories.value[0].key
  } catch { /* fallback to static */ }
}
async function loadExercises() {
  loading.value = true
  try {
    const res = await getExercises({ category: activeCategory.value })
    exercises.value = res.data.items
  } catch { /* fallback */ }
  finally { loading.value = false }
}

function switchCategory(key: string) {
  activeCategory.value = key
  loadExercises()
}

function fullUrl(path: string) {
  if (!path) return ""
  if (path.startsWith("http")) return path
  return "http://127.0.0.1:8000" + path
}

function openVideo(url: string) { if (url.startsWith("/")) url = "http://127.0.0.1:8000" + url
  window.open(url, '_blank')
}

onMounted(async () => {
  await loadCategories()
  await loadExercises()
})

const filteredExercises = computed(() => exercises.value)
</script>

<style scoped>
.page-hero { position:relative; padding:160px 0 80px; background:var(--clr-black); overflow:hidden; }
.page-hero__bg { position:absolute; inset:0; background:radial-gradient(ellipse at 30% 60%,rgba(201,169,110,0.05),transparent 50%); }
.page-hero__content { position:relative; z-index:1; }
.page-hero__label { font-size:11px; letter-spacing:4px; color:var(--clr-gold); margin-bottom:16px; display:inline-block; }
.page-hero__title { font-family:var(--font-display); font-size:48px; font-weight:400; color:var(--clr-cream); margin-bottom:16px; letter-spacing:2px; }
.page-hero__desc { font-size:15px; color:var(--clr-gray-light); max-width:500px; }

.exercises__tabs { display:flex; gap:8px; margin-bottom:48px; flex-wrap:wrap; }
.tab-btn { display:inline-flex; align-items:center; padding:12px 28px; background:transparent; border:1px solid rgba(0,0,0,0.08); font-family:var(--font-primary); font-size:13px; letter-spacing:1px; color:var(--clr-gray); cursor:pointer; transition:var(--transition-default); }
.tab-btn:hover { border-color:var(--clr-gold); color:var(--clr-gold); }
.tab-btn.is-active { background:var(--clr-gold); border-color:var(--clr-gold); color:var(--clr-white); }

.exercises__grid { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }
.exercise-card { background:var(--clr-white); border:1px solid rgba(0,0,0,0.05); transition:var(--transition-default); }
.exercise-card:hover { transform:translateY(-4px); box-shadow:0 12px 40px rgba(0,0,0,0.08); }
.exercise-card__image { width:100%; aspect-ratio:16/10; overflow:hidden; }
.exercise-card__img-placeholder { width:100%; height:100%; display:flex; align-items:center; justify-content:center; transition:var(--transition-default); }
.exercise-card__cover { width:100%; height:100%; object-fit:cover; transition:var(--transition-default); }
.exercise-card:hover .exercise-card__img-placeholder { transform:scale(1.03); }
.exercise-card__img-icon { font-size:36px; color:rgba(255,255,255,0.15); font-family:var(--font-mono); font-weight:100; }
.exercise-card__body { padding:24px; }
.exercise-card__tag { display:inline-block; font-size:10px; letter-spacing:2px; color:var(--clr-gold); text-transform:uppercase; margin-bottom:8px; }
.exercise-card__title { font-family:var(--font-display); font-size:20px; font-weight:400; color:var(--clr-dark); margin-bottom:8px; letter-spacing:1px; }
.exercise-card__desc { font-size:13px; line-height:1.7; color:var(--clr-gray); margin-bottom:16px; }
.exercise-card__meta { display:flex; align-items:center; gap:16px; }
.exercise-card__difficulty { font-size:11px; letter-spacing:1px; padding:4px 12px; border:1px solid; }
.diff--beginner { color:#6b8e6b; border-color:#6b8e6b; }
.diff--intermediate { color:#c9a96e; border-color:#c9a96e; }
.diff--advanced { color:#c0392b; border-color:#c0392b; }
.exercise-card__target { font-size:12px; color:var(--clr-gray); display:flex; align-items:center; gap:4px; }.exercise-card__video { font-size:12px; color:var(--clr-gold); display:flex; align-items:center; gap:4px; margin-left:auto; cursor:pointer; }
.exercise-card__video:hover { color:var(--clr-gold-dark); }

@media (max-width:1024px) { .exercises__grid { grid-template-columns:repeat(2,1fr); } }
@media (max-width:768px) {
  .page-hero__title { font-size:32px; }
  .exercises__grid { grid-template-columns:1fr; }
  .exercises__tabs { flex-wrap:nowrap; overflow-x:auto; padding-bottom:8px; }
  .tab-btn { white-space:nowrap; }
}
</style>






