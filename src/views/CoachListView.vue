<template>
  <div class="coach-list-page">
    <section class="coach-list-hero">
      <h1 class="coach-list-hero__title">认证教练</h1>
      <p class="coach-list-hero__sub">
        全部教练均通过实名与资质认证。申请绑定后，教练可以查看你的训练数据概览，为你提供针对性指导。
      </p>
    </section>

    <div v-if="loading" class="coach-list-loading" v-loading="true" element-loading-text="加载教练列表..." />

    <el-empty v-else-if="coaches.length === 0" description="暂无在营教练，稍后再来看看" />

    <div v-else class="coach-grid">
      <article v-for="c in coaches" :key="c.user_id" class="coach-card">
        <header class="coach-card__head">
          <el-avatar :size="56" :src="fullAvatar(c.avatar_url)">{{ (c.display_name || c.nickname || '教')[0] }}</el-avatar>
          <div class="coach-card__title">
            <h3>{{ c.display_name || c.nickname }}</h3>
            <p class="coach-card__meta">
              <el-tag size="small" effect="plain" type="success">已认证</el-tag>
              <span>执教 {{ c.years ?? 0 }} 年</span>
              <span>{{ c.students_count }} 位学员</span>
            </p>
          </div>
        </header>

        <div v-if="c.specialties" class="coach-card__tags">
          <el-tag v-for="t in c.specialties.split(',')" :key="t" size="small" type="info" effect="plain">{{ t }}</el-tag>
        </div>

        <p class="coach-card__bio">{{ c.bio || '这位教练还没有填写简介。' }}</p>

        <footer class="coach-card__foot">
          <template v-if="!c.relation">
            <el-button type="primary" size="small" @click="openApply(c)">
              <el-icon><Plus /></el-icon> 申请绑定
            </el-button>
          </template>
          <template v-else-if="c.relation.status === 'pending'">
            <el-tag size="small" type="warning">
              <el-icon style="vertical-align:-2px"><Clock /></el-icon> 等待教练确认
            </el-tag>
          </template>
          <template v-else-if="c.relation.status === 'active'">
            <el-tag size="small" type="success">已绑定</el-tag>
          </template>
          <template v-else>
            <el-button size="small" text type="primary" @click="openApply(c)">重新申请</el-button>
          </template>
        </footer>
      </article>
    </div>

    <!-- 申请绑定弹窗 -->
    <el-dialog v-model="applyVisible" :title="`申请绑定 · ${applyTarget?.display_name || ''}`" width="440px">
      <el-alert type="info" :closable="false" show-icon title="隐私提示"
        description="绑定成功后，教练可以查看你的训练数据概览（连续天数、训练容量、最近记录、个人纪录），无法查看你的身体隐私数据。" style="margin-bottom:16px;" />
      <el-input v-model="applyMessage" type="textarea" :rows="3" maxlength="256" show-word-limit
        placeholder="给教练留言：你的训练目标、每周训练频率等（可留空）" />
      <template #footer>
        <el-button @click="applyVisible = false">取消</el-button>
        <el-button type="primary" :loading="applying" @click="submitApply">发送申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { ElMessage } from "element-plus"
import { getCoachList, subscribeCoach } from "@/api/coach"
import { API_BASE_URL } from "@/api/http"

const coaches = ref<any[]>([])
const loading = ref(true)
const applyVisible = ref(false)
const applying = ref(false)
const applyTarget = ref<any>(null)
const applyMessage = ref("")

function fullAvatar(url?: string) {
  if (!url) return ""
  if (url.startsWith("http")) return url
  return API_BASE_URL.replace(/\/api$/, "") + url
}

async function load() {
  loading.value = true
  try {
    const res = await getCoachList()
    coaches.value = res.data.items
  } catch (e: any) {
    ElMessage.error(e?.message || "教练列表加载失败")
  } finally {
    loading.value = false
  }
}

function openApply(c: any) {
  applyTarget.value = c
  applyMessage.value = ""
  applyVisible.value = true
}

async function submitApply() {
  if (!applyTarget.value) return
  applying.value = true
  try {
    const res = await subscribeCoach(applyTarget.value.user_id, applyMessage.value)
    ElMessage.success(res.msg || "申请已发送")
    applyVisible.value = false
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "申请失败")
  } finally {
    applying.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.coach-list-page { max-width: 1100px; margin: 0 auto; padding: 112px 24px 60px; }
.coach-list-hero { margin-bottom: 28px; }
.coach-list-hero__title { font-family: "Playfair Display", serif; font-size: 32px; color: #1a1a1a; margin: 0 0 8px; }
.coach-list-hero__sub { color: #777; font-size: 14px; margin: 0; }
.coach-list-loading { height: 240px; }
.coach-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.coach-card {
  background: #fff; border: 1px solid #ececec; border-radius: 14px; padding: 20px;
  display: flex; flex-direction: column; gap: 12px; transition: box-shadow .2s;
}
.coach-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.07); }
.coach-card__head { display: flex; gap: 14px; align-items: center; }
.coach-card__title h3 { margin: 0 0 6px; font-size: 17px; color: #222; }
.coach-card__meta { margin: 0; display: flex; gap: 10px; align-items: center; font-size: 12px; color: #888; }
.coach-card__tags { display: flex; flex-wrap: wrap; gap: 6px; }
.coach-card__bio { margin: 0; font-size: 13px; color: #666; line-height: 1.7; flex: 1; }
.coach-card__foot { display: flex; justify-content: flex-end; }
</style>
