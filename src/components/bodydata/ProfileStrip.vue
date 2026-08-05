<template>
  <section class="profile-strip section section-light">
    <div class="container">
      <div class="profile-strip__inner">
        <div class="profile-strip__title">
          <span class="profile-strip__label">PERSONAL PROFILE</span>
          <h2 class="profile-strip__heading">个人基础档案</h2>
        </div>
        <div class="profile-strip__fields">
          <div class="profile-strip__field">
            <label>性别</label>
            <el-radio-group v-model="profile.gender" size="small">
              <el-radio-button value="male">男</el-radio-button>
              <el-radio-button value="female">女</el-radio-button>
            </el-radio-group>
          </div>
          <div class="profile-strip__field">
            <label>年龄</label>
            <el-input-number v-model="profile.age" :min="10" :max="100" :controls="false" style="width: 90px" />
          </div>
          <div class="profile-strip__field">
            <label>运动强度</label>
            <el-select v-model="profile.activity_level" style="width: 170px" size="small">
              <el-option v-for="opt in activityOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </div>
          <div class="profile-strip__field">
            <label>单位</label>
            <el-radio-group v-model="unitModel" size="small">
              <el-radio-button value="metric">公制 cm/kg</el-radio-button>
              <el-radio-button value="imperial">英制 in/lb</el-radio-button>
            </el-radio-group>
          </div>
          <button class="btn-primary profile-strip__save" @click="emit('save')">保存档案</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Unit } from '@/utils/units'

const props = defineProps<{
  profile: any
  unit: Unit
  activityOptions: { value: string; label: string }[]
}>()

const emit = defineEmits<{
  (e: 'save'): void
  (e: 'update:unit', v: Unit): void
}>()

const unitModel = computed({
  get: () => props.unit,
  set: (v: any) => emit('update:unit', v),
})
</script>

<style scoped>
.profile-strip { padding: 36px 0; }
.profile-strip__inner { display: flex; align-items: center; justify-content: space-between; gap: 32px; flex-wrap: wrap; }
.profile-strip__label { font-size: 11px; letter-spacing: 3px; color: var(--clr-gold); display: block; margin-bottom: 4px; }
.profile-strip__heading { font-family: var(--font-display); font-size: 24px; font-weight: 400; }
.profile-strip__fields { display: flex; align-items: flex-end; gap: 24px; flex-wrap: wrap; }
.profile-strip__field label { display: block; font-size: 12px; color: var(--clr-gray); margin-bottom: 6px; letter-spacing: 1px; }
.profile-strip__save { padding: 11px 24px; }

@media (max-width: 768px) {
  .profile-strip__inner { flex-direction: column; align-items: flex-start; }
}
</style>
