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
  return raw ? JSON.parse(raw) : null
}

export function setUser(user: any) {
  localStorage.setItem('fitluxe_user', JSON.stringify(user))
}

export function isLoggedIn(): boolean {
  return !!getToken()
}

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
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
    if (d.code !== 0) {
      return Promise.reject(new Error(d.msg || '请求失败'))
    }
    return d
  },
  (err) => {
    const msg = err.response?.data?.msg || err.message || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

export default http
