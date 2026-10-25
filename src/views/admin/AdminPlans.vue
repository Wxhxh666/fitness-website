<template>
  <div class="admin-page">
    <!-- 工具栏：数量 + 右上角新增按钮（与动作管理一致） -->
    <div class="admin-page__toolbar">
      <span class="admin-page__count">共 {{ total }} 个计划</span>
      <div style="flex:1"></div>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon> 新增计划
      </el-button>
    </div>

    <el-table :data="plans" flexible stripe style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="计划名称" width="160" />
      <el-table-column prop="badge" label="标签" width="80" />
      <el-table-column prop="goal" label="目标" width="100" />
      <el-table-column prop="duration" label="周期" width="80" />
      <el-table-column prop="frequency" label="频次" width="100" />
      <el-table-column prop="difficulty_label" label="难度" width="80" />
      <el-table-column label="描述" min-width="200">
        <template #default="{ row }">{{ row.desc || row.description }}</template>
      </el-table-column>
      <el-table-column label="状态" width="130" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small" style="margin-right:4px;">{{ row.is_active ? "上架" : "下架" }}</el-tag>
          <el-button size="small" text :type="row.is_active ? 'warning' : 'success'"
            @click="toggleStatus(row)" :loading="togglingId === row.id">
            {{ row.is_active ? "下架" : "上架" }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑计划弹窗（表单样式与动作管理一致：label 置顶） -->
    <el-dialog v-model="showAddDialog" :title="editingId ? '编辑计划' : '新增计划'" width="560px" :close-on-click-modal="false">
      <el-form :model="form" label-position="top" ref="formRef" :rules="formRules">
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="训练目标" prop="goal">
              <el-select v-model="form.goal" placeholder="选择目标" style="width:100%">
                <el-option v-for="g in goals" :key="g.key" :label="g.label" :value="g.key" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度等级" prop="difficulty">
              <el-select v-model="form.difficulty" placeholder="选择难度" style="width:100%">
                <el-option label="入门" value="beginner" />
                <el-option label="中级" value="intermediate" />
                <el-option label="高级" value="advanced" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="标签" prop="badge">
              <el-input v-model="form.badge" placeholder="例如：推荐 / 进阶 / 高效" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="封面图 URL" prop="cover_url">
              <el-input v-model="form.cover_url" placeholder="可选，填写图片地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="周期" prop="duration">
              <el-input v-model="form.duration" placeholder="例如：12 周" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="频次" prop="frequency">
              <el-input v-model="form.frequency" placeholder="例如：5 天 / 周" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="计划描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="简要描述该计划" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPlan" :loading="submitting">{{ editingId ? "保存修改" : "提交创建" }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { Plus } from "@element-plus/icons-vue"
import { getAdminPlans, togglePlanStatus, createPlan, updatePlan, getPlanGoals } from "@/api"
import { ElMessage } from "element-plus"
import type { FormInstance, FormRules } from "element-plus"

const plans = ref<any[]>([])
const total = ref(0)
const loading = ref(true)
const togglingId = ref<number | null>(null)
const goals = ref<any[]>([])

const showAddDialog = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive({
  name: "",
  goal: "muscle",
  difficulty: "intermediate",
  badge: "推荐",
  duration: "",
  frequency: "",
  description: "",
  cover_url: "",
})

const formRules: FormRules = {
  name: [{ required: true, message: "请输入计划名称", trigger: "blur" }],
}

onMounted(async () => {
  load()
  try {
    const res = await getPlanGoals()
    goals.value = res.data
  } catch { /* 目标下拉加载失败时使用默认值 */ }
})

async function load() {
  loading.value = true
  try {
    const res = await getAdminPlans()
    plans.value = res.data.items
    total.value = res.data.total
  } catch { /* */ }
  finally { loading.value = false }
}

async function toggleStatus(plan: any) {
  togglingId.value = plan.id
  try {
    await togglePlanStatus(plan.id)
    ElMessage.success(plan.is_active ? "已下架" : "已上架")
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "操作失败")
  } finally {
    togglingId.value = null
  }
}

function resetForm() {
  form.name = ""; form.goal = "muscle"; form.difficulty = "intermediate"
  form.badge = "推荐"; form.duration = ""; form.frequency = ""
  form.description = ""; form.cover_url = ""
}

function openCreate() {
  editingId.value = null
  resetForm()
  showAddDialog.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  form.name = row.name || ""
  form.goal = row.goal || "muscle"
  form.difficulty = row.difficulty || "intermediate"
  form.badge = row.badge || ""
  form.duration = row.duration || ""
  form.frequency = row.frequency || ""
  form.description = row.description || row.desc || ""
  form.cover_url = row.cover_url || ""
  showAddDialog.value = true
}

async function submitPlan() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (editingId.value) {
      await updatePlan(editingId.value, { ...form })
      ElMessage.success("计划已更新")
    } else {
      await createPlan({ ...form })
      ElMessage.success("计划创建成功")
    }
    showAddDialog.value = false
    editingId.value = null
    resetForm()
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || "提交失败")
  } finally {
    submitting.value = false
  }
}
</script>
