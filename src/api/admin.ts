import http from './http'

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

export function togglePlanStatus(planId: number) {
  return http.put<any, any>('/admin/plans/' + planId + '/toggle-status')
}

export function createPlan(data: any) {
  return http.post<any, { code: number; data: any }>('/admin/plans', data)
}

export function updatePlan(planId: number, data: any) {
  return http.put<any, { code: number; data: any }>('/admin/plans/' + planId, data)
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
