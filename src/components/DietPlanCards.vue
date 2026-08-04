<template>
  <div v-if="plan" class="diet-cards">
    <div class="diet-summary">
      <div class="diet-summary__cal">
        <span class="diet-summary__num">{{ plan.summary?.calories ?? '--' }}</span>
        <span class="diet-summary__unit">kcal / 天</span>
      </div>
      <div class="diet-macros">
        <div class="diet-macro">
          <span class="diet-macro__val">{{ plan.summary?.protein_g ?? '--' }}</span>
          <span class="diet-macro__label">蛋白质 g</span>
        </div>
        <div class="diet-macro">
          <span class="diet-macro__val">{{ plan.summary?.carbs_g ?? '--' }}</span>
          <span class="diet-macro__label">碳水 g</span>
        </div>
        <div class="diet-macro">
          <span class="diet-macro__val">{{ plan.summary?.fat_g ?? '--' }}</span>
          <span class="diet-macro__label">脂肪 g</span>
        </div>
      </div>
      <p v-if="plan.summary?.note" class="diet-summary__note">{{ plan.summary.note }}</p>
    </div>

    <div v-if="(plan.meals || []).length" class="diet-meals">
      <div v-for="(m, i) in plan.meals" :key="i" class="diet-meal">
        <h4 class="diet-meal__name">{{ m.name }}</h4>
        <ul class="diet-meal__items">
          <li v-for="(it, j) in m.items || []" :key="j" class="diet-meal__item">
            <span class="diet-meal__food">{{ it.food }}</span>
            <span class="diet-meal__weight">{{ it.weight }}</span>
            <span class="diet-meal__cal">{{ it.calories ?? '--' }} kcal</span>
          </li>
        </ul>
        <p v-if="m.note" class="diet-meal__note">{{ m.note }}</p>
      </div>
    </div>

    <div v-if="plan.water_tips" class="diet-block">
      <h4 class="diet-block__title"><el-icon><CoffeeCup /></el-icon>饮水建议</h4>
      <p class="diet-block__text">{{ plan.water_tips }}</p>
    </div>

    <div v-if="(plan.taboos || []).length" class="diet-block">
      <h4 class="diet-block__title"><el-icon><Warning /></el-icon>饮食禁忌</h4>
      <ul class="diet-block__list">
        <li v-for="(t, i) in plan.taboos" :key="i">{{ t }}</li>
      </ul>
    </div>

    <div v-if="(plan.tips || []).length" class="diet-block">
      <h4 class="diet-block__title"><el-icon><ChatDotRound /></el-icon>健身小贴士</h4>
      <ul class="diet-block__list">
        <li v-for="(t, i) in plan.tips" :key="i">{{ t }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ plan: any }>()
</script>

<style scoped>
.diet-summary {
  background: var(--clr-bg-section);
  border: 1px solid rgba(201, 169, 110, 0.25);
  padding: 22px 24px;
  margin-bottom: 18px;
}
.diet-summary__cal { display: flex; align-items: baseline; gap: 8px; margin-bottom: 14px; }
.diet-summary__num { font-family: var(--font-display); font-size: 40px; color: var(--clr-gold-dark); }
.diet-summary__unit { font-size: 14px; color: var(--clr-gray); }
.diet-macros { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; }
.diet-macro { display: flex; flex-direction: column; gap: 2px; padding: 12px; background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); text-align: center; }
.diet-macro__val { font-family: var(--font-display); font-size: 22px; color: var(--clr-dark); }
.diet-macro__label { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.diet-summary__note { font-size: 13px; color: var(--clr-gray-deep); line-height: 1.7; }

.diet-meals { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 18px; }
.diet-meal { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.06); padding: 18px 20px; }
.diet-meal__name { font-size: 14px; font-weight: 500; letter-spacing: 1px; color: var(--clr-dark); margin-bottom: 12px; border-left: 3px solid var(--clr-gold); padding-left: 10px; }
.diet-meal__items { display: flex; flex-direction: column; gap: 8px; }
.diet-meal__item { display: flex; align-items: baseline; gap: 10px; font-size: 13px; color: var(--clr-gray-deep); }
.diet-meal__food { font-weight: 400; }
.diet-meal__weight { color: var(--clr-gray); font-size: 12px; flex: 1; text-align: right; }
.diet-meal__cal { color: var(--clr-gold-dark); font-size: 12px; white-space: nowrap; }
.diet-meal__note { margin-top: 10px; font-size: 12px; color: var(--clr-gray); }

.diet-block { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.06); padding: 18px 20px; margin-bottom: 14px; }
.diet-block__title { font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 8px; color: var(--clr-dark); margin-bottom: 10px; }
.diet-block__title .el-icon { color: var(--clr-gold); }
.diet-block__text { font-size: 13px; color: var(--clr-gray-deep); line-height: 1.8; }
.diet-block__list { display: flex; flex-direction: column; gap: 8px; }
.diet-block__list li { font-size: 13px; color: var(--clr-gray-deep); padding-left: 14px; position: relative; line-height: 1.7; }
.diet-block__list li::before { content: ""; position: absolute; left: 0; top: 9px; width: 5px; height: 5px; border-radius: 50%; background: var(--clr-gold); }

@media (max-width: 768px) {
  .diet-meals { grid-template-columns: 1fr; }
  .diet-macros { grid-template-columns: 1fr 1fr 1fr; }
}
/* FITLUXE 质感升级：数值金色放大加粗、卡片圆角阴影 */
.diet-summary {
  background: linear-gradient(135deg, #FBF7EC, #F6EEDD);
  border: 1px solid rgba(184, 156, 102, 0.3);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(184, 156, 102, 0.12);
}
.diet-summary__num {
  font-size: 52px;
  font-weight: 700;
  color: #B89C66;
  letter-spacing: -1px;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.diet-summary__unit {
  color: #8B7355;
  font-weight: 500;
}
.diet-macro {
  background: #FFFFFF;
  border: 1px solid rgba(184, 156, 102, 0.2);
  border-radius: 12px;
  box-shadow: 0 4px 14px rgba(184, 156, 102, 0.08);
}
.diet-macro__val {
  font-size: 28px;
  font-weight: 700;
  color: #B89C66;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.diet-macro__label {
  color: #8B7355;
  font-weight: 500;
  letter-spacing: 1px;
}
.diet-summary__note {
  color: #6F675D;
}
.diet-meal {
  border: 1px solid rgba(184, 156, 102, 0.16);
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(184, 156, 102, 0.08);
}
.diet-meal__name {
  border-left: 3px solid #B89C66;
  color: #1A1A1A;
  font-weight: 600;
}
.diet-meal__cal {
  color: #B89C66;
  font-weight: 700;
  font-size: 13px;
}
.diet-meal__food {
  font-weight: 500;
}
.diet-block {
  border: 1px solid rgba(184, 156, 102, 0.16);
  border-radius: 12px;
  box-shadow: 0 4px 14px rgba(184, 156, 102, 0.06);
}
.diet-block__title {
  color: #1A1A1A;
  font-weight: 600;
}
.diet-block__title .el-icon {
  color: #B89C66;
}
.diet-block__list li::before {
  background: #B89C66;
}
</style>
