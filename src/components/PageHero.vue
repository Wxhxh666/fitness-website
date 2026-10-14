<template>
  <section class="page-hero">
    <div class="page-hero__bg">
      <span class="page-hero__orb page-hero__orb--1"></span>
      <span class="page-hero__orb page-hero__orb--2"></span>
      <span class="page-hero__scan"></span>
    </div>
    <div class="page-hero__content container">
      <span v-if="label" class="page-hero__label">{{ label }}</span>
      <h1 class="page-hero__title">{{ title }}</h1>
      <p v-if="desc" class="page-hero__desc">{{ desc }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  label?: string
  title: string
  desc?: string
}>()
</script>

<style scoped>
/* 顶部留出固定导航（72px）+ 呼吸空间，避免标题被导航遮挡 */
.page-hero { padding: 160px 0 80px; }
.page-hero__bg { position: absolute; inset: 0; }
.page-hero__orb { position: absolute; border-radius: 50%; filter: blur(52px); opacity: 0.55; z-index: 0; animation: floatOrb 12s ease-in-out infinite; }
.page-hero__orb--1 { width: 340px; height: 340px; background: radial-gradient(circle, rgba(182, 255, 60, 0.5), transparent 70%); top: -70px; left: -50px; }
.page-hero__orb--2 { width: 280px; height: 280px; background: radial-gradient(circle, rgba(53, 224, 232, 0.5), transparent 70%); bottom: -60px; right: 8%; animation-delay: 1.6s; }
.page-hero__scan { position: absolute; left: 0; right: 0; height: 120px; background: linear-gradient(to bottom, transparent, rgba(12, 216, 160, 0.08), transparent); animation: scanline 7s linear infinite; }
.page-hero__content { position: relative; z-index: 2; }
.page-hero__label { font-size: 12px; letter-spacing: 5px; color: var(--clr-volt); margin-bottom: 18px; display: inline-flex; align-items: center; gap: 10px; font-weight: 700; }
.page-hero__label::before { content: ""; width: 26px; height: 2px; background: var(--grad-brand); box-shadow: 0 0 10px rgba(12, 216, 160, 0.85); }
.page-hero__title { font-family: var(--font-display); font-size: 52px; font-weight: 700; color: var(--clr-cream); margin-bottom: 16px; letter-spacing: 1px; }
.page-hero__desc { font-size: 15px; color: var(--clr-gray-light); max-width: 500px; }

@media (max-width: 768px) {
  .page-hero { padding: 118px 0 56px; }
  .page-hero__title { font-size: 34px; }
}
</style>
