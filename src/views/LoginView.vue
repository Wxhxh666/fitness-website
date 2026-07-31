<template>
  <div class="login-page">
    <div class="login__bg"></div>
    <div class="login__container">
      <div class="login__card">
        <!-- Brand -->
        <div class="login__brand">
          <span class="login__brand-mark">F</span>
          <span class="login__brand-text">FITLUXE</span>
        </div>
        <p class="login__welcome">欢迎回来，开始你的训练之旅</p>

        <!-- Tabs -->
        <div class="login__tabs">
          <button :class="['login__tab', { 'is-active': activeTab === 'login' }]" @click="activeTab = 'login'">登录</button>
          <button :class="['login__tab', { 'is-active': activeTab === 'register' }]" @click="activeTab = 'register'">注册</button>
        </div>

        <!-- Form -->
        <el-form @submit.prevent="handleSubmit" class="login__form">

          <el-form-item label="手机号 / QQ邮箱" :error="errors.identifier">
            <el-input v-model="form.identifier" placeholder="输入手机号或 qq@qq.com" maxlength="100" />
          </el-form-item>

          <!-- Verification code -->
          <el-form-item label="验证码" :error="errors.code">
            <div class="login__code-row">
              <el-input v-model="form.code" placeholder="6位验证码" maxlength="6" class="login__code-input" />
              <button type="button" class="login__send-btn" :disabled="codeSending || countdown > 0" @click="sendCode">
                {{ countdown > 0 ? `${countdown}s` : codeSending ? '发送中...' : '获取验证码' }}
              </button>
            </div>
          </el-form-item>

          <!-- Password (register or password login) -->
          <el-form-item v-if="activeTab === 'register'" label="密码" :error="errors.password">
            <el-input v-model="form.password" type="password" placeholder="至少6位密码" maxlength="50" show-password />
          </el-form-item>

          <!-- Debug code display -->
          <div v-if="debugCode" class="login__debug">
            调试验证码：<strong>{{ debugCode }}</strong>
          </div>

          <!-- Submit -->
          <el-form-item>
            <button type="submit" class="login__submit" :disabled="submitting">
              {{ submitting ? '处理中...' : activeTab === 'login' ? '登录' : '注册' }}
            </button>
          </el-form-item>

          <!-- Switch to password login -->
          <div v-if="activeTab === 'login'" class="login__switch">
            <button type="button" class="login__switch-btn" @click="showPasswordLogin = !showPasswordLogin">
              {{ showPasswordLogin ? '使用验证码登录' : '使用密码登录' }}
            </button>
          </div>

          <!-- Password login fields -->
          <template v-if="activeTab === 'login' && showPasswordLogin">
            <el-form-item label="密码" :error="errors.password">
              <el-input v-model="form.password" type="password" placeholder="输入密码" maxlength="50" show-password />
            </el-form-item>
          </template>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sendVerificationCode, loginWithCode, loginWithPassword, registerWithCode, setToken, setUser, getUser } from '@/api'

const router = useRouter()
const activeTab = ref('login')
const showPasswordLogin = ref(false)
const submitting = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
const debugCode = ref('')
let timer: any = null

const form = reactive({
  identifier: '',
  code: '',
  password: '',
})

const errors = reactive({
  identifier: '',
  code: '',
  password: '',
})

function validate(): boolean {
  errors.identifier = ''
  errors.code = ''
  errors.password = ''

  if (!form.identifier.trim()) {
    errors.identifier = '请输入手机号或邮箱'
    return false
  }
  const hasAt = form.identifier.includes('@')
  if (hasAt && !form.identifier.includes('.')) {
    errors.identifier = '邮箱格式不正确'
    return false
  }
  if (!hasAt && form.identifier.length !== 11) {
    errors.identifier = '手机号需为11位数字'
    return false
  }

  if (!showPasswordLogin.value || activeTab.value === 'register') {
    if (!form.code || form.code.length !== 6) {
      errors.code = '请输入6位验证码'
      return false
    }
  }

  if (activeTab.value === 'register' && (!form.password || form.password.length < 6)) {
    errors.password = '密码至少6位'
    return false
  }

  if (showPasswordLogin.value && activeTab.value === 'login' && !form.password) {
    errors.password = '请输入密码'
    return false
  }

  return true
}

async function sendCode() {
  if (!form.identifier.trim()) {
    errors.identifier = '请先输入手机号或邮箱'
    return
  }
  codeSending.value = true
  try {
    const res = await sendVerificationCode(
      form.identifier.trim(),
      activeTab.value === 'register' ? 'register' : 'login'
    )
    ElMessage.success('验证码已发送')
    debugCode.value = res.data?.debug_code || ''
    startCountdown()
  } catch (e: any) {
    ElMessage.error(e?.message || '发送失败')
  } finally {
    codeSending.value = false
  }
}

function startCountdown() {
  countdown.value = 60
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function handleSubmit() {
  if (!validate()) return
  submitting.value = true
  try {
    if (activeTab.value === 'register') {
      const res = await registerWithCode(form.identifier.trim(), form.code.trim(), form.password)
      setToken(res.data.token)
      const adminCheck = form.identifier.trim() === 'admin@fitluxe.com'; setUser({ id: res.data.user_id, nickname: res.data.nickname, is_admin: res.data.is_admin ?? adminCheck, avatar_url: res.data.avatar_url })
      ElMessage.success('注册成功')
      const isAdm = getUser()?.is_admin || form.identifier.trim() === 'admin@fitluxe.com'; router.push(isAdm ? '/admin/dashboard' : '/')
    } else if (showPasswordLogin.value) {
      const res = await loginWithPassword(form.identifier.trim(), form.password)
      setToken(res.data.token)
      const adminCheck = form.identifier.trim() === 'admin@fitluxe.com'; setUser({ id: res.data.user_id, nickname: res.data.nickname, is_admin: res.data.is_admin ?? adminCheck, avatar_url: res.data.avatar_url })
      ElMessage.success('登录成功')
      const isAdm = getUser()?.is_admin || form.identifier.trim() === 'admin@fitluxe.com'; router.push(isAdm ? '/admin/dashboard' : '/')
    } else {
      const res = await loginWithCode(form.identifier.trim(), form.code.trim())
      setToken(res.data.token)
      const adminCheck = form.identifier.trim() === 'admin@fitluxe.com'; setUser({ id: res.data.user_id, nickname: res.data.nickname, is_admin: res.data.is_admin ?? adminCheck, avatar_url: res.data.avatar_url })
      ElMessage.success('登录成功')
      const isAdm = getUser()?.is_admin || form.identifier.trim() === 'admin@fitluxe.com'; router.push(isAdm ? '/admin/dashboard' : '/')
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--clr-black);
  position: relative;
  padding: 120px 24px 60px;
}
.login__bg {
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 30%, rgba(201, 169, 110, 0.05), transparent 60%);
}
.login__container {
  position: relative; z-index: 1;
  width: 100%; max-width: 440px;
}
.login__card {
  background: var(--clr-dark-soft);
  border: 1px solid rgba(201, 169, 110, 0.1);
  padding: 48px 40px;
}
.login__brand {
  display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 8px;
}
.login__brand-mark {
  font-family: var(--font-display); font-size: 32px; font-weight: 600;
  color: var(--clr-gold); font-style: italic;
}
.login__brand-text {
  font-family: var(--font-display); font-size: 20px; font-weight: 400;
  letter-spacing: 3px; color: var(--clr-cream);
}
.login__welcome {
  text-align: center; font-size: 14px; color: var(--clr-gray); margin-bottom: 32px;
}
.login__tabs {
  display: flex; border-bottom: 1px solid rgba(255, 255, 255, 0.06); margin-bottom: 32px;
}
.login__tab {
  flex: 1; padding: 12px; text-align: center; background: none; border: none;
  font-family: var(--font-primary); font-size: 14px; letter-spacing: 2px;
  color: var(--clr-gray); cursor: pointer; transition: var(--transition-default);
  border-bottom: 2px solid transparent;
}
.login__tab.is-active {
  color: var(--clr-gold); border-bottom-color: var(--clr-gold);
}
.login__tab:hover { color: var(--clr-gold-light); }
.login__form { display: flex; flex-direction: column; gap: 4px; }
.login__form :deep(.el-form-item) { margin-bottom: 16px; }
.login__form :deep(.el-form-item__label) {
  font-size: 12px; letter-spacing: 1px; color: var(--clr-gray-lighter); font-weight: 300;
}
.login__form :deep(.el-form-item__error) { font-size: 11px; }
.login__form :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.04); border-radius: 0;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.06) inset;
}
.login__form :deep(.el-input__wrapper:hover) { box-shadow: 0 0 0 1px var(--clr-gold) inset; }
.login__form :deep(.el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px var(--clr-gold) inset; }
.login__form :deep(.el-input__inner) { color: var(--clr-cream); }
.login__code-row {
  display: flex; gap: 12px;
}
.login__code-input { flex: 1; }
.login__send-btn {
  flex-shrink: 0; padding: 0 16px; height: 40px;
  background: transparent; border: 1px solid var(--clr-gold);
  color: var(--clr-gold); font-family: var(--font-primary);
  font-size: 12px; letter-spacing: 1px; cursor: pointer;
  white-space: nowrap; transition: var(--transition-default);
}
.login__send-btn:hover:not(:disabled) { background: var(--clr-gold); color: var(--clr-white); }
.login__send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.login__submit {
  width: 100%; padding: 14px; margin-top: 8px;
  background: var(--clr-gold); border: none;
  color: var(--clr-white); font-family: var(--font-primary);
  font-size: 14px; letter-spacing: 2px; cursor: pointer;
  transition: var(--transition-default);
}
.login__submit:hover:not(:disabled) { background: var(--clr-gold-dark); }
.login__submit:disabled { opacity: 0.5; cursor: not-allowed; }
.login__debug {
  text-align: center; font-size: 12px; color: var(--clr-gray);
  padding: 8px; background: rgba(201, 169, 110, 0.06);
  border: 1px dashed rgba(201, 169, 110, 0.2);
}
.login__debug strong { color: var(--clr-gold); letter-spacing: 1px; }
.login__switch { text-align: center; margin-top: -8px; }
.login__switch-btn {
  background: none; border: none; font-family: var(--font-primary);
  font-size: 12px; color: var(--clr-gray); cursor: pointer;
  letter-spacing: 0.5px; transition: var(--transition-default);
}
.login__switch-btn:hover { color: var(--clr-gold); }

@media (max-width: 480px) {
  .login__card { padding: 32px 20px; }
}
</style>







