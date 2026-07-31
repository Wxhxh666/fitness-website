<template>
  <div class="home-page">
    <section class="hero">
      <div class="hero__bg"></div>
      <div class="hero__overlay"></div>
      <div class="hero__content container">
        <div class="hero__text">
          <span class="hero__label">SCULPT YOUR LEGACY</span>
          <h1 class="hero__title">以极致匠心<br /><span class="text-gold">重塑身体</span></h1>
          <p class="hero__desc">FITLUXE 融合运动科学与优雅美学，为追求卓越的你<br class="hero__br" />提供专业动作指导、个性化训练计划与数据化管理。</p>
          <div class="hero__actions">
            <router-link to="/exercises" class="btn-primary">探索课程<el-icon><ArrowRight /></el-icon></router-link>
            <router-link to="/plans" class="btn-outline">定制计划</router-link>
          </div>
        </div>
        <div class="hero__scroll">
          <span>SCROLL</span>
          <div class="hero__scroll-line"></div>
        </div>
      </div>
    </section>

    <section class="features section section-white">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">WHY FITLUXE</p>
          <h2 class="section-title">不止于健身</h2>
          <div class="gold-divider"></div>
          <p class="section-desc">我们相信，真正的改变源于科学的方法与持续的精进。</p>
        </div>
        <div class="features__grid">
          <div v-for="(feat, index) in features" :key="index" class="feature-card animate-in" :class="`animate-in-delay-${index}`">
            <div class="feature-card__icon"><el-icon :size="32"><component :is="feat.icon" /></el-icon></div>
            <h3 class="feature-card__title">{{ feat.title }}</h3>
            <p class="feature-card__desc">{{ feat.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="philosophy section section-dark">
      <div class="container">
        <div class="philosophy__inner">
          <div class="philosophy__text">
            <p class="section-subtitle">OUR PHILOSOPHY</p>
            <h2 class="section-title">运动，是一种生活态度</h2>
            <div class="gold-divider-left"></div>
            <p class="philosophy__desc">FITLUXE 诞生于对完美身体比例的追求。我们拒绝流于表面的健身潮流，专注于运动科学的本质——每一块肌肉的发力、每一次呼吸的节奏、每一个动作的轨迹，都值得被精确对待。</p>
            <p class="philosophy__desc">在这里，你获得的不仅是训练计划，更是一套科学、可持续的身体管理方案。</p>
            <router-link to="/contact" class="btn-outline" style="margin-top:12px;">了解更多</router-link>
          </div>
          <div class="philosophy__image">
            <div class="philosophy__image-placeholder"><span>ELEGANCE · STRENGTH · BALANCE</span></div>
          </div>
        </div>
      </div>
    </section>

    <section class="stats section section-light">
      <div class="container">
        <div class="stats__grid">
          <div v-for="(stat, index) in stats" :key="index" class="stat-item">
            <span class="stat-item__number">{{ stat.number }}</span>
            <span class="stat-item__label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="cta section section-dark">
      <div class="container text-center">
        <p class="section-subtitle">BEGIN YOUR JOURNEY</p>
        <h2 class="section-title">准备好开始改变了吗？</h2>
        <div class="gold-divider"></div>
        <p class="section-desc" style="color:var(--clr-gray);">无论你的目标是什么，我们都有适合你的方案。</p>
        <div style="margin-top:36px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">
          <router-link to="/body-data" class="btn-primary">开始评估<el-icon><ArrowRight /></el-icon></router-link>
          <router-link to="/contact" class="btn-outline">预约咨询</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
const features = [
  { icon: 'Notebook', title: '科学动作库', desc: '百种训练动作的详细分解与要点提示，搭配高清演示，确保每一个动作都标准到位。' },
  { icon: 'TrendCharts', title: '智能计划生成', desc: '根据你的身体数据与目标，AI 动态生成个性化训练方案，随阶段自动调整强度。' },
  { icon: 'DataAnalysis', title: '数据追踪管理', desc: '系统记录体重、体脂、围度等关键指标，用可视化的成长曲线见证每一次进步。' },
  { icon: 'UserFilled', title: '专业教练团队', desc: '汇聚国家认证健身教练与运动康复专家，为你提供一对一的远程指导与答疑。' },
]
const stats = [
  { number: '15,000+', label: '活跃学员' },
  { number: '320+', label: '专业动作课程' },
  { number: '98.6%', label: '学员满意率' },
  { number: '4.8/5', label: '综合评分' },
]
</script>

<style scoped>
.hero { position:relative; height:100vh; min-height:600px; display:flex; align-items:center; overflow:hidden; background:var(--clr-black); }
.hero__bg { position:absolute; inset:0; background:linear-gradient(135deg,rgba(10,10,10,0.85) 0%,rgba(20,20,20,0.6) 100%), repeating-linear-gradient(0deg,transparent,transparent 60px,rgba(201,169,110,0.03) 60px,rgba(201,169,110,0.03) 61px); }
.hero__overlay { position:absolute; inset:0; background:radial-gradient(ellipse at 70% 50%,rgba(201,169,110,0.06),transparent 60%); }
.hero__content { position:relative; z-index:2; width:100%; }
.hero__text { max-width:680px; }
.hero__label { display:inline-block; font-size:12px; letter-spacing:4px; color:var(--clr-gold); margin-bottom:24px; font-weight:400; }
.hero__title { font-family:var(--font-display); font-size:64px; font-weight:400; line-height:1.15; color:var(--clr-cream); margin-bottom:20px; letter-spacing:1px; }
.hero__desc { font-size:16px; line-height:1.8; color:var(--clr-gray-light); margin-bottom:40px; }
.hero__actions { display:flex; gap:16px; }
.hero__scroll { position:absolute; bottom:40px; left:50%; transform:translateX(-50%); display:flex; flex-direction:column; align-items:center; gap:12px; font-size:10px; letter-spacing:3px; color:var(--clr-gray); }
.hero__scroll-line { width:1px; height:40px; background:linear-gradient(to bottom,var(--clr-gold),transparent); }

.features__grid { display:grid; grid-template-columns:repeat(4,1fr); gap:24px; margin-top:60px; }
.feature-card { text-align:center; padding:48px 28px; border:1px solid rgba(0,0,0,0.05); background:var(--clr-white); transition:var(--transition-default); }
.feature-card:hover { border-color:var(--clr-gold); transform:translateY(-6px); box-shadow:0 16px 48px rgba(201,169,110,0.1); }
.feature-card__icon { width:64px; height:64px; margin:0 auto 24px; display:flex; align-items:center; justify-content:center; color:var(--clr-gold); border:1px solid rgba(201,169,110,0.2); }
.feature-card__title { font-family:var(--font-display); font-size:18px; font-weight:400; margin-bottom:12px; letter-spacing:1px; color:var(--clr-dark); }
.feature-card__desc { font-size:14px; line-height:1.7; color:var(--clr-gray); }

.philosophy__inner { display:grid; grid-template-columns:1fr 1fr; gap:80px; align-items:center; }
.philosophy__desc { font-size:15px; line-height:1.9; color:var(--clr-gray-light); margin-bottom:16px; }
.philosophy__image-placeholder { width:100%; aspect-ratio:4/5; background:linear-gradient(135deg,var(--clr-dark-soft),var(--clr-dark-mid)); border:1px solid rgba(201,169,110,0.08); display:flex; align-items:center; justify-content:center; color:var(--clr-gray-deep); font-family:var(--font-display); font-size:14px; letter-spacing:3px; font-style:italic; }

.stats__grid { display:grid; grid-template-columns:repeat(4,1fr); gap:24px; }
.stat-item { text-align:center; padding:48px 24px; }
.stat-item__number { display:block; font-family:var(--font-display); font-size:42px; font-weight:400; color:var(--clr-gold); margin-bottom:8px; }
.stat-item__label { font-size:13px; letter-spacing:2px; color:var(--clr-gray); }

.cta { border-top:1px solid rgba(201,169,110,0.06); border-bottom:1px solid rgba(201,169,110,0.06); }

@media (max-width:1024px) {
  .features__grid { grid-template-columns:repeat(2,1fr); }
  .philosophy__inner { grid-template-columns:1fr; gap:48px; }
  .philosophy__image { order:-1; }
}
@media (max-width:768px) {
  .hero__title { font-size:36px; }
  .hero__desc { font-size:14px; }
  .hero__actions { flex-direction:column; }
  .hero__scroll { display:none; }
  .features__grid { grid-template-columns:1fr; }
  .stats__grid { grid-template-columns:repeat(2,1fr); }
  .stat-item__number { font-size:32px; }
}
</style>
