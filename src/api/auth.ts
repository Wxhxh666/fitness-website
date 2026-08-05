import http from './http'

// ---------- Auth ----------
export function sendVerificationCode(identifier: string, purpose = 'login') {
  return http.post('/auth/send-code', { identifier, purpose })
}

export function registerWithCode(identifier: string, code: string, password: string) {
  return http.post('/auth/register', { identifier, code, password })
}

export function loginWithCode(identifier: string, code: string) {
  return http.post('/auth/login', { identifier, code })
}

export function loginWithPassword(identifier: string, password: string) {
  return http.post('/auth/password-login', { identifier, password })
}

export function fetchCurrentUser() {
  return http.get<any, { code: number; data: any }>('/auth/me')
}

export function loginUser(identifier: string, code: string) {
  return http.post<any, { code: number; data: { user_id: number; nickname: string; token: string } }>('/auth/login', { identifier, code })
}

export function registerUser(identifier: string, code: string, password: string) {
  return http.post<any, { code: number; data: { user_id: number; nickname: string; token: string } }>('/auth/register', { identifier, code, password })
}

export function passwordLogin(identifier: string, password: string) {
  return http.post<any, { code: number; data: { user_id: number; nickname: string; token: string } }>('/auth/password-login', { identifier, password })
}

export function sendCode(identifier: string, purpose = 'login') {
  return http.post<any, { code: number; data: { debug_code: string } }>('/auth/send-code', { identifier, purpose })
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
