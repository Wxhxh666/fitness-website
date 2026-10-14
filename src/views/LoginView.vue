<template>
  <div class="auth">
    <!-- 背景装饰 -->
    <span class="auth__blob auth__blob--a"></span>
    <span class="auth__blob auth__blob--b"></span>
    <span class="auth__ring auth__ring--a"></span>
    <span class="auth__ring auth__ring--b"></span>

    <div class="auth__card">
      <!-- 顶部圆形标识 -->
      <div class="auth__badge" aria-hidden="true">
        <span class="auth__badge-mark">F</span>
      </div>

      <h1 class="auth__title">{{ isRegister ? '创建账号' : '欢迎回来' }}</h1>
      <p class="auth__subtitle">
        {{ isRegister ? '注册后即可开始你的训练计划' : '登录以继续你的训练之旅' }}
      </p>

      <form class="auth__form" novalidate @submit.prevent="onSubmit">
        <!-- 账号（浮动标签） -->
        <div :class="['field', { 'is-filled': !!form.identifier, 'is-invalid': !!errors.identifier }]">
          <input
            id="auth-identifier"
            v-model="form.identifier"
            class="field__input"
            type="text"
            autocomplete="username"
            placeholder=" "
            maxlength="100"
            @keyup.enter="onSubmit"
          />
          <label class="field__label" for="auth-identifier">邮箱 / 手机号</label>
        </div>
        <p v-if="errors.identifier" class="field__error">{{ errors.identifier }}</p>

        <!-- 密码（浮动标签 + 显示/隐藏） -->
        <div :class="['field', { 'is-filled': !!form.password, 'is-invalid': !!errors.password }]">
          <input
            id="auth-password"
            v-model="form.password"
            class="field__input field__input--pw"
            :type="showPassword ? 'text' : 'password'"
            :autocomplete="isRegister ? 'new-password' : 'current-password'"
            placeholder=" "
            maxlength="50"
            @keyup.enter="onSubmit"
          />
          <label class="field__label" for="auth-password">密码</label>
          <button
            type="button"
            class="field__eye"
            :aria-label="showPassword ? '隐藏密码' : '显示密码'"
            @click="showPassword = !showPassword"
          >
            <svg v-if="!showPassword" viewBox="0 0 24 24" width="18" height="18">
              <path
                d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"
                fill="none" stroke="currentColor" stroke-width="1.7"
              />
              <circle cx="12" cy="12" r="2.8" fill="none" stroke="currentColor" stroke-width="1.7" />
            </svg>
            <svg v-else viewBox="0 0 24 24" width="18" height="18">
              <path
                d="M2 12s3.6-6.5 10-6.5c2 0 3.7.6 5.1 1.5M22 12s-3.6 6.5-10 6.5c-2 0-3.7-.6-5.1-1.5"
                fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"
              />
              <path d="M3 3l18 18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
            </svg>
          </button>
        </div>
        <p v-if="errors.password" class="field__error">{{ errors.password }}</p>

        <!-- 注册模式：确认密码 -->
        <template v-if="isRegister">
          <div :class="['field', { 'is-filled': !!form.confirm, 'is-invalid': !!errors.confirm }]">
            <input
              id="auth-confirm"
              v-model="form.confirm"
              class="field__input"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              placeholder=" "
              maxlength="50"
              @keyup.enter="onSubmit"
            />
            <label class="field__label" for="auth-confirm">确认密码</label>
          </div>
          <p v-if="errors.confirm" class="field__error">{{ errors.confirm }}</p>
        </template>

        <!-- 登录模式：忘记密码 -->
        <div v-if="!isRegister" class="auth__forgot-row">
          <button type="button" class="auth__link auth__link--sm" @click="onForgotPassword">忘记密码？</button>
        </div>

        <!-- 提交 -->
        <button type="submit" class="auth__submit" :disabled="submitting">
          <span v-if="submitting" class="auth__spinner" aria-hidden="true"></span>
          {{ submitting ? '处理中…' : isRegister ? '注册' : '登录' }}
        </button>
      </form>

      <!-- 底部切换 -->
      <div class="auth__footer">
        <template v-if="isRegister">
          <button type="button" class="auth__link" @click="switchMode(false)">返回登录</button>
        </template>
        <template v-else>
          <button type="button" class="auth__link" @click="switchMode(true)">注册新账号</button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginWithPassword, registerWithPassword, setToken, setUser, getUser } from '@/api'

const router = useRouter()
const submitting = ref(false)
const showPassword = ref(false)
const mode = ref<'login' | 'register'>('login')

const isRegister = computed(() => mode.value === 'register')

const form = reactive({
  identifier: '',
  password: '',
  confirm: '',
})

const errors = reactive({
  identifier: '',
  password: '',
  confirm: '',
})

function clearErrors() {
  errors.identifier = ''
  errors.password = ''
  errors.confirm = ''
}

/** 账号既支持邮箱也支持 11 位手机号 */
function validateIdentifier(): boolean {
  const v = form.identifier.trim()
  if (!v) {
    errors.identifier = '请输入邮箱或手机号'
    return false
  }
  if (v.includes('@')) {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) {
      errors.identifier = '邮箱格式不正确'
      return false
    }
  } else if (!/^\d{11}$/.test(v)) {
    errors.identifier = '手机号需为 11 位数字'
    return false
  }
  return true
}

function validate(): boolean {
  clearErrors()
  let ok = validateIdentifier()

  if (!form.password) {
    errors.password = '请输入密码'
    ok = false
  } else if (isRegister.value && form.password.length < 6) {
    errors.password = '密码至少 6 位'
    ok = false
  }

  if (isRegister.value) {
    if (!form.confirm) {
      errors.confirm = '请再次输入密码'
      ok = false
    } else if (form.confirm !== form.password) {
      errors.confirm = '两次输入的密码不一致'
      ok = false
    }
  }
  return ok
}

/** 把后端返回的错误提示落到对应输入框上，而不是只弹一个 toast */
function applyServerError(msg: string) {
  if (/验证码/.test(msg)) {
    // 后端若仍要求验证码，说明注册接口未更新，直接说明原因
    ElMessage.error('后端仍在校验验证码，请重启后端以加载新的注册逻辑')
    return
  }
  if (/密码/.test(msg)) {
    errors.password = msg
  } else if (/账号|邮箱|手机号|用户/.test(msg)) {
    errors.identifier = msg
  }
  ElMessage.error(msg)
}

/** 登录成功后的统一收尾：落库用户信息 + 按角色跳转 */
function finishAuth(data: any, successMsg: string) {
  setToken(data.token)
  const identifier = form.identifier.trim()
  // 后端已返回 is_admin，仅在缺失时才回退到本地判断
  const isAdmin = data.is_admin ?? identifier === 'admin@fitluxe.com'
  setUser({
    id: data.user_id,
    nickname: data.nickname,
    is_admin: isAdmin,
    avatar_url: data.avatar_url,
  })
  ElMessage.success(successMsg)
  router.push(getUser()?.is_admin ? '/admin/dashboard' : '/')
}

async function onSubmit() {
  if (submitting.value) return
  if (!validate()) return

  submitting.value = true
  try {
    const identifier = form.identifier.trim()
    if (isRegister.value) {
      const res = await registerWithPassword(identifier, form.password)
      finishAuth(res.data, '注册成功')
    } else {
      const res = await loginWithPassword(identifier, form.password)
      finishAuth(res.data, '登录成功')
    }
  } catch (e: any) {
    applyServerError(e?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

function switchMode(toRegister: boolean) {
  mode.value = toRegister ? 'register' : 'login'
  clearErrors()
  form.password = ''
  form.confirm = ''
  showPassword.value = false
}

function onForgotPassword() {
  ElMessage.info('请联系管理员重置密码')
}
</script>

<style scoped>
/* ============ 页面容器：浅紫底 + 居中卡片 ============ */
.auth {
  --indigo: #3B4388;
  --indigo-deep: #2F376F;
  --indigo-hover: #4A53A0;
  --ink: #1F2440;
  --ink-soft: #6A6F8C;
  --field-bg: #FFFFFF;
  --field-border: #E4E6F2;
  --danger: #D9534F;
  --lavender: #E9EAF6;

  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  overflow: hidden;
  background: linear-gradient(160deg, #EEEFF9 0%, #E7E9F7 55%, #E3E6F5 100%);
  font-family: var(--font-primary);
}

/* 背景装饰：柔和光斑 + 细描边圆环。
   max-width/height 限制在容器内，避免撑出横向滚动条把卡片挤偏 */
.auth__blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  pointer-events: none;
  max-width: 100%;
  max-height: 100%;
}
.auth__blob--a {
  width: 380px; height: 380px; top: -120px; left: -110px;
  background: rgba(94, 104, 190, 0.20);
}
.auth__blob--b {
  width: 320px; height: 320px; bottom: -110px; right: -90px;
  background: rgba(140, 130, 210, 0.18);
}
.auth__ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(59, 67, 136, 0.10);
  pointer-events: none;
  max-width: 100%;
  max-height: 100%;
}
.auth__ring--a { width: 420px; height: 420px; top: -160px; right: -140px; }
.auth__ring--b { width: 300px; height: 300px; bottom: -130px; left: -110px; }

/* ============ 卡片 ============ */
.auth__card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  padding: 44px 34px 30px;
  border-radius: 30px;
  background: var(--field-bg);
  box-shadow:
    0 24px 60px -20px rgba(47, 55, 111, 0.22),
    0 2px 8px rgba(47, 55, 111, 0.04);
}

/* 顶部圆形标识 */
.auth__badge {
  width: 96px;
  height: 96px;
  margin: 0 auto 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 32% 28%, #4E58A8 0%, var(--indigo) 45%, var(--indigo-deep) 100%);
  box-shadow: 0 12px 26px -8px rgba(47, 55, 111, 0.55);
}
.auth__badge-mark {
  font-family: var(--font-display);
  font-size: 42px;
  font-weight: 600;
  font-style: italic;
  color: #FFFFFF;
  line-height: 1;
  transform: translateY(-1px);
}

.auth__title {
  font-size: 21px;
  font-weight: 600;
  color: var(--ink);
  text-align: center;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}
.auth__subtitle {
  font-size: 13px;
  color: var(--ink-soft);
  text-align: center;
  margin-bottom: 30px;
}

/* ============ 表单 ============ */
.auth__form {
  display: flex;
  flex-direction: column;
}

/* 浮动标签输入框 */
.field {
  position: relative;
  margin-bottom: 14px;
}
.field__input {
  width: 100%;
  height: 58px;
  /* 上内边距给上浮标签留出位置，输入文字落在下半部分，避免与标签贴在一起 */
  padding: 24px 16px 6px;
  font-size: 15px;
  font-family: inherit;
  color: var(--ink);
  background: var(--field-bg);
  border: 1.5px solid var(--field-border);
  border-radius: 16px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.field__input--pw { padding-right: 46px; }
.field__input::placeholder { color: transparent; }

.field__input:hover { border-color: #D3D6E8; }
.field__input:focus {
  border-color: var(--indigo);
  box-shadow: 0 0 0 3px rgba(59, 67, 136, 0.10);
}

.field__label {
  position: absolute;
  left: 17px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 15px;
  color: #9AA0BC;
  pointer-events: none;
  transition: all 0.18s cubic-bezier(0.22, 0.61, 0.36, 1);
}
/* 聚焦或有内容时标签上浮 */
.field__input:focus ~ .field__label,
.field.is-filled .field__label {
  top: 15px;
  transform: translateY(0);
  font-size: 11.5px;
  letter-spacing: 0.4px;
  color: var(--indigo);
}

.field.is-invalid .field__input { border-color: var(--danger); }
.field.is-invalid .field__label { color: var(--danger); }

/* 密码显示/隐藏 */
.field__eye {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  padding: 0;
  color: #A7ACC6;
  cursor: pointer;
  border-radius: 50%;
  transition: color 0.2s ease, background 0.2s ease;
}
.field__eye:hover { color: var(--indigo); background: rgba(59, 67, 136, 0.07); }

/* 校验提示 */
.field__error {
  margin: -8px 0 10px;
  padding-left: 4px;
  font-size: 12px;
  color: var(--danger);
  line-height: 1.4;
}

.auth__forgot-row {
  display: flex;
  justify-content: flex-end;
  margin: 2px 2px 0;
}

/* ============ 按钮与链接 ============ */
.auth__submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 54px;
  margin-top: 18px;
  border: none;
  border-radius: 999px;
  background: var(--indigo);
  color: #FFFFFF;
  font-family: inherit;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 3px;
  cursor: pointer;
  transition: background 0.22s ease, transform 0.12s ease, box-shadow 0.22s ease;
  box-shadow: 0 12px 24px -10px rgba(47, 55, 111, 0.65);
}
.auth__submit:hover:not(:disabled) {
  background: var(--indigo-hover);
  box-shadow: 0 14px 28px -10px rgba(47, 55, 111, 0.7);
}
.auth__submit:active:not(:disabled) { transform: translateY(1px); }
.auth__submit:disabled { opacity: 0.65; cursor: not-allowed; box-shadow: none; }

.auth__spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: auth-spin 0.7s linear infinite;
}
@keyframes auth-spin { to { transform: rotate(360deg); } }

.auth__footer {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 22px;
  min-height: 22px;
}

.auth__link {
  background: none;
  border: none;
  padding: 2px 4px;
  font-family: inherit;
  font-size: 13.5px;
  color: var(--ink-soft);
  cursor: pointer;
  border-radius: 6px;
  transition: color 0.2s ease;
}
.auth__link:hover { color: var(--indigo); text-decoration: underline; }
.auth__link--sm { font-size: 12.5px; }

/* ============ 响应式 ============ */
@media (max-width: 480px) {
  .auth { padding: 24px 14px; }
  .auth__card { padding: 34px 22px 24px; border-radius: 26px; }
  .auth__badge { width: 82px; height: 82px; margin-bottom: 22px; }
  .auth__badge-mark { font-size: 36px; }
  .auth__ring--a, .auth__ring--b { display: none; }
}

/* 尊重“减少动态效果”偏好 */
@media (prefers-reduced-motion: reduce) {
  .field__input, .field__label, .auth__submit, .auth__link, .field__eye {
    transition: none;
  }
  .auth__spinner { animation-duration: 1.4s; }
}
</style>

<!-- 整页浅紫背景 + 锁定横向溢出 -->
<!-- 说明：全局 body 只设了 overflow-x:hidden，html 仍会横向滚动，
     导致窄屏下卡片被推偏、右侧被裁切，所以这里对 html/body 一起处理 -->
<style>
html:has(.auth),
body:has(.auth) {
  background-color: #E9EAF6;
}
html:has(.auth),
body:has(.auth) {
  overflow-x: clip;
  max-width: 100%;
}
</style>
