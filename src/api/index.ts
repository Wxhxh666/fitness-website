import axios from 'axios'
import type { AxiosInstance } from 'axios'

// ====== Token Management ======
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
  baseURL: 'http://127.0.0.1:8000/api',
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

export interface Exercise {
  id: number; name: string; category: string; category_label: string
  description: string; difficulty: string; difficulty_label: string
  duration: string; cover_url: string; steps?: any[]; target_muscles?: string[]
}

export interface Plan {
  id: number; name: string; goal: string; badge: string; description: string
  duration: string; frequency: string; difficulty: string; difficulty_label: string
  focus: string[]
}

export interface BodyMetric {
  id: number; key: string; label: string; value: number; unit: string
  change: number; trend: string
}

export interface Measurement {
  id: number; key: string; label: string; value: number; unit: string
}

// ---------- Exercises ----------
export function getExerciseCategories() {
  return http.get<any, { code: number; data: { key: string; label: string }[] }>('/exercises/categories')
}

export function getExercises(params?: { category?: string; difficulty?: string; keyword?: string }) {
  return http.get<any, { code: number; data: { items: Exercise[]; total: number } }>('/exercises', { params })
}

export function getExerciseDetail(id: number) {
  return http.get<any, { code: number; data: Exercise }>(`/exercises/${id}`)
}

// ---------- Plans ----------
export function getPlanGoals() {
  return http.get<any, { code: number; data: { key: string; label: string }[] }>('/plans/goals')
}

export function getPlans(params?: { goal?: string; difficulty?: string }) {
  return http.get<any, { code: number; data: { items: Plan[]; total: number } }>('/plans', { params })
}

export function getPlanDetail(id: number) {
  return http.get<any, { code: number; data: Plan }>(`/plans/${id}`)
}
export function cloneOfficialPlan(officialPlanId: number) {
  return http.post<any, any>('/plans/user/clone/' + officialPlanId)
}

// ---------- User Plans ----------
export function getUserPlans() {
  return http.get<any, { code: number; data: { items: any[] } }>('/plans/user')
}
export function createUserPlan(data: any) {
  return http.post<any, any>('/plans/user', data)
}
export function updateUserPlan(id: number, data: any) {
  return http.put<any, any>('/plans/user/' + id, data)
}
export function deleteUserPlan(id: number) {
  return http.delete<any, any>('/plans/user/' + id)
}
export function getUserPlanDetail(id: number) {
  return http.get<any, any>('/plans/user/' + id)
}

// ---------- Training Logs ----------
export function logTraining(data: { plan_id: number; is_official: boolean; log_date?: string; focus?: string; exercises?: any[]; note?: string }) {
  return http.post<any, any>('/plans/user/training/log', data)
}
export function getTrainingLogs(params?: { days?: number; plan_id?: number }) {
  return http.get<any, any>('/plans/user/training/logs', { params })
}
export function getTrainingStats() {
  return http.get<any, any>('/plans/user/training/stats')
}

// ---------- Body Metrics ----------
export function getBodyMetrics() {
  return http.get<any, { code: number; data: BodyMetric[] }>('/body-metrics')
}

export function calculateBMI(heightCm: number, weightKg: number) {
  return http.post<any, { code: number; data: { bmi: number; category: string; category_label: string } }>('/body-metrics/bmi', { height_cm: heightCm, weight_kg: weightKg })
}

export function getMeasurements() {
  return http.get<any, { code: number; data: Measurement[] }>('/body-metrics/measurements')
}

export function updateMeasurement(id: number, value: number) {
  return http.put<any, { code: number; data: Measurement }>(`/body-metrics/measurements/${id}`, { value })
}

export function getMetricHistory(metricKey?: string, days?: number) {
  return http.get<any, { code: number; data: { metric_key: string; records: { date: string; value: number }[] }[] }>('/body-metrics/history', { params: { metric_key: metricKey, days } })
}

// ---------- Contact ----------
export function submitContact(data: { name: string; email: string; phone?: string; subject: string; message: string }) {
  return http.post<any, { code: number; data: { id: number } }>('/contact', data)
}

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

// ---------- Auth ----------
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


// ---------- Admin ----------
export function getAdminDashboard() {
  return http.get<any, { code: number; data: { users: number; messages: number; unread_messages: number; exercises: number; plans: number } }>('/admin/dashboard')
}
export function getAdminMessages(page = 1) {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>('/admin/messages', { params: { page, page_size: 20 } })
}
export function markMessageRead(id: number) {
  return http.put<any, any>('/admin/messages/' + id + '/read')
}
export function toggleUserStatus(userId: number) {
  return http.put<any, any>('/admin/users/' + userId + '/toggle-status')
}

export function getAdminUsers() {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>('/admin/users')
}
export function getAdminExercises() {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>('/admin/exercises')
}
export function toggleExerciseStatus(exerciseId: number) {
  return http.put<any, any>('/admin/exercises/' + exerciseId + '/toggle-status')
}
export function createExercise(data: {
  name: string; category: string; description?: string
  difficulty?: string; duration?: string; cover_url?: string; video_url?: string
}) {
  return http.post<any, { code: number; data: any }>('/admin/exercises', data)
}
export function updateExercise(id: number, data: any) {
  return http.put<any, { code: number; data: any }>('/admin/exercises/' + id, data)
}
export function getAdminPlans() {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>('/admin/plans')
}

// ---------- Profile ----------
export function getProfile() {
  return http.get<any, { code: number; data: any }>("/auth/profile")
}
export function updateProfile(field: string, value: string) {
  return http.post<any, { code: number; data: { id: number } }>("/auth/profile", { field, value })
}

// ---------- Site ----------
export function getContactInfo() {
  return http.get<any, { code: number; data: { address: string; phone: string; email: string; business_hours: any; social_media: any[] } }>('/site/contact-info')
}







// ---------- Review ----------
export function getReviewRequests(status = "pending") {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>("/admin/review-requests", { params: { status, page_size: 50 } })
}
export function getReviewDetail(id: number) {
  return http.get<any, { code: number; data: any }>("/admin/review-requests/" + id)
}
export function approveReview(id: number) {
  return http.put<any, any>("/admin/review-requests/" + id + "/approve")
}
export function rejectReview(id: number) {
  return http.put<any, any>("/admin/review-requests/" + id + "/reject")
}
