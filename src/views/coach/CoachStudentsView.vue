<template>
  <div class="coach-students">
    <el-tabs v-model="tab" @tab-change="load">
      <el-tab-pane name="pending">
        <template #label>
          <el-badge :value="pendingTotal" :hidden="pendingTotal === 0">待处理</el-badge>
        </template>
      </el-tab-pane>
      <el-tab-pane label="在学学员" name="active" />
      <el-tab-pane label="已终止" name="terminated" />
      <el-tab-pane label="全部" name="all" />
    </el-tabs>

    <el-empty v-if="!loading && items.length === 0"
      :description="tab === 'pending' ? '没有待处理的申请' : '暂无学员'" :image-size="90" />

    <el-table v-else :data="items" stripe flexible v-loading="loading">
      <el-table-column label="学员" min-width="200">
        <template #default="{ row }">
          <div class="stu-cell">
            <el-avatar :size="36" :src="fullAvatar(row.student?.avatar_url)">{{ (row.student?.nickname || '学')[0] }}</el-avatar>
            <div>
              <p class="stu-cell__name">{{ row.student?.nickname || '-' }}</p>
              <p class="stu-cell__sub">申请于 {{ fmtDate(row.created_at) }}</p>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="申请留言" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">{{ row.message || '-' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="row.status === 'active' ? 'success' : row.status === 'pending' ? 'warning' : 'info'">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="拒绝/备注" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.reject_reason || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="240" align="center" fixed="right">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" type="success" @click="accept(row)" :loading="actingId === row.id">接受</el-button>
            <el-button size="small" type="danger" plain @click="reject(row)">拒绝</el-button>
          </template>
          <template v-else-if="row.status === 'active'">
            <el-badge :value="row.unread" :hidden="!row.unread" :max="99">
              <el-button size="small" type="primary" plain @click="openChat(row)">
                <el-icon><ChatDotRound /></el-icon> 咨询
              </el-button>
            </el-badge>
            <el-button size="small" @click="openOverview(row)">训练数据</el-button>
          </template>
          <span v-else style="color:#bbb;font-size:12px;">—</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 学员训练数据抽屉 -->
    <el-drawer v-model="overviewVisible" :title="`训练数据 · ${overviewTarget?.student?.nickname || ''}`" size="560px">
      <div v-if="overviewLoading" style="text-align:center;padding:60px;color:#999;">加载中...</div>
      <template v-else-if="overview">
        <div class="ov-grid">
          <div class="ov-card"><span class="ov-card__v">{{ overview.overview.current_streak }}</span><span class="ov-card__l">连续天数</span></div>
          <div class="ov-card"><span class="ov-card__v">{{ overview.overview.longest_streak }}</span><span class="ov-card__l">最长连续</span></div>
          <div class="ov-card"><span class="ov-card__v">{{ overview.overview.month.sessions }}</span><span class="ov-card__l">本月次数</span></div>
          <div class="ov-card"><span class="ov-card__v">{{ fmtVol(overview.overview.month.volume) }}</span><span class="ov-card__l">本月容量 kg</span></div>
          <div class="ov-card"><span class="ov-card__v">{{ overview.overview.total.sessions }}</span><span class="ov-card__l">累计次数</span></div>
          <div class="ov-card"><span class="ov-card__v">{{ fmtVol(overview.overview.total.volume) }}</span><span class="ov-card__l">累计容量 kg</span></div>
        </div>

        <h4 class="ov-title">近 8 周训练容量</h4>
        <div class="ov-bars">
          <div v-for="w in overview.weekly_volume" :key="w.week_start" class="ov-bar-item"
            :title="`${w.week_start}：${fmtVol(w.volume)}kg / ${w.sessions} 次`">
            <div class="ov-bar" :style="{ height: barHeight(w.volume) }"></div>
            <span class="ov-bar-label">{{ w.week_start.slice(5).replace('-', '/') }}</span>
          </div>
        </div>

        <h4 class="ov-title">最近训练</h4>
        <el-empty v-if="overview.recent_sessions.length === 0" description="该学员还没有训练记录" :image-size="70" />
        <div v-else class="ov-sessions">
          <div v-for="s in overview.recent_sessions" :key="s.id" class="ov-session">
            <span class="ov-session__date">{{ (s.session_date || '').slice(5) }}</span>
            <span class="ov-session__note">{{ s.note || s.session_type || '训练' }}</span>
            <span class="ov-session__stat">{{ s.total_sets ?? 0 }} 组 · {{ fmtVol(s.total_volume) }}kg</span>
          </div>
        </div>
      </template>
    </el-drawer>

    <CoachChatDialog v-model="chatVisible" :relation-id="chatRelationId" :peer-name="chatPeerName"
      @closed="load" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  getCoachStudents, acceptStudent, rejectStudent, getStudentOverview,
} from "@/api/coach"
import { API_BASE_URL } from "@/api/http"
import CoachChatDialog from "@/components/coach/CoachChatDialog.vue"

const tab = ref("pending")
const items = ref<any[]>([])
const pendingTotal = ref(0)
const loading = ref(true)
const actingId = ref<number | null>(null)

const overviewVisible = ref(false)
const overviewLoading = ref(false)
const overview = ref<any>(null)
const overviewTarget = ref<any>(null)

const chatVisible = ref(false)
const chatRelationId = ref(0)
const chatPeerName = ref("")

const maxWeeklyVolume = ref(1)

function fullAvatar(url?: string) {
  if (!url) return ""
  if (url.startsWith("http")) return url
  return API_BASE_URL.replace(/\/api$/, "") + url
}
function fmtDate(s?: string) { return s ? s.slice(0, 10) : "" }
function fmtVol(v?: number) { return Math.round(v ?? 0).toLocaleString() }
function statusLabel(s: string) {
  return { pending: "待处理", active: "在学", terminated: "已终止" }[s] || s
}
function barHeight(v: number) {
  return Math.max(4, Math.round((v / (maxWeeklyVolume.value || 1)) * 120)) + "px"
}

async function load() {
  loading.value = true
  try {
    const res = await getCoachStudents(tab.value)
    items.value = res.data.items
    pendingTotal.value = res.data.pending_total
    maxWeeklyVolume.value = 1
  } catch (e: any) {
    ElMessage.error(e?.message || "加载失败")
  } finally {
    loading.value = false
  }
}

async function accept(row: any) {
  actingId.value = row.id
  try {
    const res = await acceptStudent(row.id)
    ElMessage.success(res.msg || "已接受")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  } finally {
    actingId.value = null
  }
}

async function reject(row: any) {
  let reason = ""
  try {
    const r = await ElMessageBox.prompt("请填写拒绝原因（学员会在申请状态里看到）", "拒绝申请", {
      inputPlaceholder: "例如：目前学员已满 / 方向不匹配",
      inputValidator: (v: string) => (v && v.trim() ? true : "原因不能为空"),
      type: "warning",
    })
    reason = r.value.trim()
  } catch { return }
  try {
    await rejectStudent(row.id, reason)
    ElMessage.success("已拒绝")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  }
}

function openChat(row: any) {
  chatRelationId.value = row.id
  chatPeerName.value = row.student?.nickname || "学员"
  chatVisible.value = true
}

async function openOverview(row: any) {
  overviewTarget.value = row
  overviewVisible.value = true
  overviewLoading.value = true
  overview.value = null
  try {
    const res = await getStudentOverview(row.id)
    overview.value = res.data
    maxWeeklyVolume.value = Math.max(1, ...res.data.weekly_volume.map((w: any) => w.volume))
  } catch (e: any) {
    ElMessage.error(e?.message || "数据加载失败")
    overviewVisible.value = false
  } finally {
    overviewLoading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.stu-cell { display: flex; align-items: center; gap: 10px; }
.stu-cell__name { margin: 0; font-size: 14px; color: #333; font-weight: 500; }
.stu-cell__sub { margin: 0; font-size: 12px; color: #999; }
.ov-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.ov-card { background: #f7f8f7; border-radius: 10px; padding: 14px 10px; text-align: center; display: flex; flex-direction: column; gap: 4px; }
.ov-card__v { font-size: 20px; font-weight: 600; color: #1a1a1a; font-family: "Playfair Display", serif; }
.ov-card__l { font-size: 11px; color: #999; }
.ov-title { margin: 20px 0 10px; font-size: 14px; color: #333; font-weight: 500; }
.ov-bars { display: flex; align-items: flex-end; gap: 8px; height: 150px; padding: 0 4px; }
.ov-bar-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%; justify-content: flex-end; }
.ov-bar { width: 100%; max-width: 34px; background: linear-gradient(180deg, #0CD8A0, #0aa97f); border-radius: 4px 4px 0 0; }
.ov-bar-label { font-size: 10px; color: #aaa; }
.ov-sessions { display: flex; flex-direction: column; gap: 8px; }
.ov-session {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px;
  background: #fafafa; border: 1px solid #eee; border-radius: 8px; font-size: 13px;
}
.ov-session__date { color: #0aa97f; font-weight: 600; }
.ov-session__note { flex: 1; color: #555; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ov-session__stat { color: #999; font-size: 12px; }
</style>
