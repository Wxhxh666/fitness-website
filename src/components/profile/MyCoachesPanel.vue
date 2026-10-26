<template>
  <div class="my-coaches">
    <div class="my-coaches__toolbar">
      <h3 class="my-coaches__title">我的教练</h3>
      <el-button size="small" type="primary" text @click="$router.push('/coaches')">
        <el-icon><Plus /></el-icon> 找教练
      </el-button>
    </div>

    <el-empty v-if="!loading && items.length === 0" description="还没有绑定教练，去「找教练」看看吧"
      :image-size="90" />

    <div v-else class="my-coaches__list">
      <div v-for="r in items" :key="r.id" class="rel-card">
        <el-avatar :size="44" :src="fullAvatar(r.coach?.avatar_url)">{{ (r.coach_display_name || '教')[0] }}</el-avatar>
        <div class="rel-card__info">
          <p class="rel-card__name">{{ r.coach_display_name || r.coach?.nickname }}</p>
          <p class="rel-card__sub">
            <template v-if="r.status === 'pending'">
              <el-tag size="small" type="warning">等待教练确认</el-tag>
              <span v-if="r.message" class="rel-card__msg">留言：{{ r.message }}</span>
            </template>
            <template v-else-if="r.status === 'active'">
              <el-tag size="small" type="success">已绑定</el-tag>
              <span class="rel-card__msg">绑定于 {{ fmtDate(r.created_at) }}</span>
            </template>
            <template v-else>
              <el-tag size="small" type="info">已终止</el-tag>
              <span v-if="r.reject_reason" class="rel-card__msg rel-card__msg--danger">拒绝原因：{{ r.reject_reason }}</span>
            </template>
          </p>
        </div>
        <div class="rel-card__actions">
          <el-badge v-if="r.unread > 0" :value="r.unread" :max="99">
            <el-button size="small" type="primary" plain :disabled="r.status !== 'active'"
              @click="openChat(r)">
              <el-icon><ChatDotRound /></el-icon> 咨询
            </el-button>
          </el-badge>
          <el-button v-else size="small" type="primary" plain :disabled="r.status !== 'active'"
            @click="openChat(r)">
            <el-icon><ChatDotRound /></el-icon> 咨询
          </el-button>
          <el-button v-if="r.status === 'pending'" size="small" text type="danger" @click="cancel(r)">撤回申请</el-button>
          <el-button v-else-if="r.status === 'active'" size="small" text type="danger" @click="unbind(r)">解绑</el-button>
        </div>
      </div>
    </div>

    <CoachChatDialog v-model="chatVisible" :relation-id="chatRelationId" :peer-name="chatPeerName"
      @closed="load" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { getMyCoaches, terminateCoach } from "@/api/coach"
import { API_BASE_URL } from "@/api/http"
import CoachChatDialog from "@/components/coach/CoachChatDialog.vue"

const items = ref<any[]>([])
const loading = ref(true)
const chatVisible = ref(false)
const chatRelationId = ref(0)
const chatPeerName = ref("")

function fullAvatar(url?: string) {
  if (!url) return ""
  if (url.startsWith("http")) return url
  return API_BASE_URL.replace(/\/api$/, "") + url
}

function fmtDate(s?: string) {
  return s ? s.slice(0, 10) : ""
}

async function load() {
  loading.value = true
  try {
    const res = await getMyCoaches()
    items.value = res.data.items
  } catch (e: any) {
    ElMessage.error(e?.message || "加载失败")
  } finally {
    loading.value = false
  }
}

function openChat(r: any) {
  chatRelationId.value = r.id
  chatPeerName.value = r.coach_display_name || r.coach?.nickname || "教练"
  chatVisible.value = true
}

async function cancel(r: any) {
  const { value } = await ElMessageBox.confirm("确定撤回这条申请吗？", "撤回申请", { type: "warning" }).catch(() => ({ value: false }))
  if (!value) return
  try {
    await terminateCoach(r.coach_user_id)
    ElMessage.success("已撤回")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  }
}

async function unbind(r: any) {
  const { value } = await ElMessageBox.confirm(
    `解绑后教练将无法再查看你的训练数据，历史咨询记录保留但不能再发消息。确定解绑「${r.coach_display_name}」吗？`,
    "解除绑定", { type: "warning" },
  ).catch(() => ({ value: false }))
  if (!value) return
  try {
    await terminateCoach(r.coach_user_id)
    ElMessage.success("已解绑")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  }
}

onMounted(load)
</script>

<style scoped>
.my-coaches { display: flex; flex-direction: column; gap: 16px; }
.my-coaches__toolbar { display: flex; justify-content: space-between; align-items: center; }
.my-coaches__title { margin: 0; font-size: 16px; color: #333; }
.my-coaches__list { display: flex; flex-direction: column; gap: 12px; }
.rel-card {
  display: flex; align-items: center; gap: 14px; padding: 14px 16px;
  border: 1px solid #eee; border-radius: 12px; background: #fafafa;
}
.rel-card__info { flex: 1; min-width: 0; }
.rel-card__name { margin: 0 0 6px; font-size: 15px; font-weight: 600; color: #333; }
.rel-card__sub { margin: 0; display: flex; align-items: center; gap: 10px; font-size: 12px; color: #999; }
.rel-card__msg { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 320px; }
.rel-card__msg--danger { color: #c45656; }
.rel-card__actions { display: flex; align-items: center; gap: 8px; }
</style>
