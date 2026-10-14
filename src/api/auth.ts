import http from './http'

// ---------- Auth（账号 + 密码，已移除验证码流程） ----------
export interface AuthResult {
  user_id: number
  nickname: string
  token: string
  is_admin?: boolean
  avatar_url?: string | null
}

/** 注册：仅需账号（手机号/邮箱）+ 密码 */
export function registerWithPassword(identifier: string, password: string) {
  return http.post<any, { code: number; msg: string; data: AuthResult }>('/auth/register', { identifier, password })
}

/** 登录：仅需账号（手机号/邮箱）+ 密码 */
export function loginWithPassword(identifier: string, password: string) {
  return http.post<any, { code: number; msg: string; data: AuthResult }>('/auth/password-login', { identifier, password })
}

export function fetchCurrentUser() {
  return http.get<any, { code: number; data: any }>('/auth/me')
}

// ---------- Profile ----------
export function getProfile() {
  return http.get<any, { code: number; data: any }>("/auth/profile")
}

export function updateProfile(field: string, value: string) {
  return http.post<any, { code: number; data: { id: number } }>("/auth/profile", { field, value })
}

// ---------- 个人中心新增接口 ----------
export function bindPhone(phone: string) {
  return http.post<any, { code: number; msg: string; data: { phone: string } }>('/auth/bind-phone', { phone })
}

export function changePassword(old_password: string, new_password: string) {
  return http.post<any, { code: number; msg: string }>('/auth/change-password', { old_password, new_password })
}

export function getPreferences() {
  return http.get<any, { code: number; data: { ai_model: string; unit_system: string; notification_enabled: boolean } }>('/auth/preferences')
}

export function updatePreferences(data: { ai_model?: string; unit_system?: string; notification_enabled?: boolean }) {
  return http.put<any, { code: number; data: any }>('/auth/preferences', data)
}

export function getDashboardStats() {
  return http.get<any, { code: number; data: any }>('/auth/dashboard-stats')
}
