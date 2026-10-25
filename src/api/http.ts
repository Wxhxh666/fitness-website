import axios from 'axios'

// 后端地址：默认走 127.0.0.1:8000，可用 VITE_API_BASE 环境变量覆盖（部署时无需改代码）
export const API_BASE_URL: string = (import.meta.env.VITE_API_BASE as string) || 'http://127.0.0.1:8000/api'

export function getToken(): string | null {
  return localStorage.getItem('fitluxe_token')
}

export function setToken(token: string) {
  localStorage.setItem('fitluxe_token', token)
}

export function removeToken() {
  localStorage.removeItem('fitluxe_token')
  localStorage.removeItem('fitluxe_user')
}

export function getUser(): any {
  const raw = localStorage.getItem('fitluxe_user')
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    // localStorage 被写坏时不能让整个应用崩在解析上
    localStorage.removeItem('fitluxe_user')
    return null
  }
}

export function setUser(user: any) {
  localStorage.setItem('fitluxe_user', JSON.stringify(user))
}

export function isLoggedIn(): boolean {
  return !!getToken()
}

/**
 * 会话失效的统一处理：
 * 只有“曾经登录过”才跳登录页（避免匿名访问公共页面时被反复踢走），
 * 并用模块级标记去重——一次刷页面并发 4 个请求时只跳一次。
 */
let redirectingToLogin = false

function handleUnauthorized() {
  const hadToken = !!getToken()
  removeToken()
  if (!hadToken || redirectingToLogin) return

  redirectingToLogin = true
  const current = window.location.pathname + window.location.search
  if (current.startsWith('/login')) {
    redirectingToLogin = false
    return
  }
  // 用 replace 而不是 push，避免用户点“返回”又回到失效页面
  window.location.replace(`/login?redirect=${encodeURIComponent(current)}`)
}

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach token to every request
http.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (err) => Promise.reject(err)
)

http.interceptors.response.use(
  (res) => {
    const d = res.data
    if (d && d.code === 401) {
      handleUnauthorized()
      return Promise.reject(new Error(d.msg || '登录已过期，请重新登录'))
    }
    if (d && d.code !== 0) {
      return Promise.reject(new Error(d.msg || '请求失败'))
    }
    return d
  },
  (err) => {
    const status = err.response?.status
    if (status === 401) {
      handleUnauthorized()
      return Promise.reject(new Error(err.response?.data?.msg || '登录已过期，请重新登录'))
    }

    let msg = err.response?.data?.msg
    if (!msg) {
      if (err.code === 'ECONNABORTED') msg = '请求超时，请稍后重试'
      else if (!err.response) msg = '无法连接服务器，请确认后端已启动'
      else msg = err.message || '请求失败'
    }
    if (status === 403) msg = msg || '没有操作权限'
    if (status === 429) msg = msg || '操作过于频繁，请稍后再试'
    return Promise.reject(new Error(msg))
  }
)

export default http
