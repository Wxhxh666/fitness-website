<template>
  <div class="admin-page">
    <div class="admin-page__toolbar">
      <el-radio-group v-model="statusFilter" @change="load">
        <el-radio-button value="pending">待审核</el-radio-button>
        <el-radio-button value="approved">已通过</el-radio-button>
        <el-radio-button value="rejected">已驳回</el-radio-button>
        <el-radio-button value="all">全部</el-radio-button>
      </el-radio-group>
    </div>

    <el-table :data="items" flexible stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="申请人" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">{{ row.user_nickname || row.user_email }}</template>
      </el-table-column>
      <el-table-column prop="real_name" label="真实姓名" width="110" />
      <el-table-column prop="phone" label="联系电话" width="130" />
      <el-table-column label="资质类型" width="150">
        <template #default="{ row }">{{ certLabel(row.cert_type) }}</template>
      </el-table-column>
      <el-table-column label="专长" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.specialties || "-" }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="提交时间" width="160">
        <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" align="center" fixed="right">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" text type="primary" @click="showDetail(row)">查看</el-button>
            <el-button size="small" type="success" @click="approve(row)">通过</el-button>
            <el-button size="small" type="danger" @click="reject(row)">驳回</el-button>
          </template>
          <el-button v-else size="small" text type="primary" @click="showDetail(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 详情：证件受保护加载 -->
    <el-dialog v-model="detailVisible" title="认证申请详情" width="680px" :close-on-click-modal="false">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="申请人">{{ detail?.user_nickname || detail?.user_email }}</el-descriptions-item>
        <el-descriptions-item label="真实姓名">{{ detail?.real_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail?.phone }}</el-descriptions-item>
        <el-descriptions-item label="资质类型">{{ detail ? certLabel(detail.cert_type) : "" }}</el-descriptions-item>
        <el-descriptions-item label="个人简介" :span="2">{{ detail?.bio || "-" }}</el-descriptions-item>
        <el-descriptions-item label="专长标签" :span="2">{{ detail?.specialties || "-" }}</el-descriptions-item>
        <el-descriptions-item v-if="detail?.status === 'rejected'" label="驳回原因" :span="2">
          {{ detail?.reject_reason }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="cred-grid">
        <div class="cred-grid__item">
          <span class="cred-grid__label">身份证人像面</span>
          <img v-if="credUrls.front" :src="credUrls.front" alt="身份证人像面" />
          <el-button v-else-if="!credLoading" text @click="loadCreds(detail.id)">重新加载</el-button>
        </div>
        <div class="cred-grid__item">
          <span class="cred-grid__label">身份证国徽面</span>
          <img v-if="credUrls.back" :src="credUrls.back" alt="身份证国徽面" />
        </div>
        <div class="cred-grid__item">
          <span class="cred-grid__label">资质凭证</span>
          <img v-if="credUrls.cert" :src="credUrls.cert" alt="资质凭证" />
        </div>
      </div>

      <template #footer>
        <template v-if="detail?.status === 'pending'">
          <el-button type="danger" @click="reject(detail)">驳回</el-button>
          <el-button type="success" @click="approve(detail)">通过认证</el-button>
        </template>
        <el-button v-else @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCoachApplications, approveCoachApplication, rejectCoachApplication, fetchCredentialBlobUrl } from '@/api/coach'

const items = ref<any[]>([])
const loading = ref(true)
const statusFilter = ref('pending')
const detail = ref<any>(null)
const detailVisible = ref(false)
const credLoading = ref(false)
const credUrls = reactive<Record<string, string>>({})

const CERT_LABELS: Record<string, string> = {
  national: '国家职业资格（国职）', ace: 'ACE', nssa: 'NSCA-CPT', other: '其他',
}
function certLabel(k: string) { return CERT_LABELS[k] || k }
function statusLabel(s: string) {
  return s === 'pending' ? '待审核' : s === 'approved' ? '已通过' : '已驳回'
}
function fmtTime(s?: string) { return s ? s.slice(0, 16).replace('T', ' ') : '-' }

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const res = await getCoachApplications(statusFilter.value)
    items.value = res.data.items
  } catch { /* */ }
  finally { loading.value = false }
}

async function showDetail(row: any) {
  detail.value = row
  detailVisible.value = true
  await loadCreds(row.id)
}

async function loadCreds(id: number) {
  credLoading.value = true
  Object.keys(credUrls).forEach(k => {
    URL.revokeObjectURL(credUrls[k])
    delete credUrls[k]
  })
  try {
    credUrls.front = await fetchCredentialBlobUrl(id, 'front')
    credUrls.back = await fetchCredentialBlobUrl(id, 'back')
    credUrls.cert = await fetchCredentialBlobUrl(id, 'cert')
  } catch (e: any) {
    ElMessage.error(e?.message || '证件加载失败')
  } finally {
    credLoading.value = false
  }
}

async function approve(row: any) {
  try {
    await ElMessageBox.confirm(
      `确认通过「${row.real_name}」的教练认证？通过后该用户将获得教练工作台权限。`,
      '通过认证', { type: 'warning' },
    )
  } catch { return }
  try {
    await approveCoachApplication(row.id)
    ElMessage.success('已通过认证')
    detailVisible.value = false
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

async function reject(row: any) {
  let reason = ''
  try {
    const res = await ElMessageBox.prompt('请填写驳回原因（申请人会在个人中心看到）', '驳回申请', {
      type: 'warning',
      inputPlaceholder: '例如：资质证书照片模糊，无法辨认编号',
      inputValidator: (v: string) => (v && v.trim() ? true : '驳回原因不能为空'),
    })
    reason = res.value.trim()
  } catch { return }
  try {
    await rejectCoachApplication(row.id, reason)
    ElMessage.success('已驳回')
    detailVisible.value = false
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}
</script>

<style scoped>
.admin-page__toolbar { margin-bottom: 16px; }
:deep(.el-table th) { background: #fafafa !important; color: #555; font-weight: 500; font-size: 13px; }
.cred-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }
.cred-grid__item { display: flex; flex-direction: column; gap: 6px; }
.cred-grid__label { font-size: 12px; color: #999; }
.cred-grid__item img {
  width: 100%; height: 130px; object-fit: cover; border-radius: 8px;
  border: 1px solid #e5e5e5; background: #fafafa;
}
</style>
