import http from './http'

export interface Plan {
  id: number; name: string; goal: string; badge: string; description: string
  duration: string; frequency: string; difficulty: string; difficulty_label: string
  focus: string[]
}

export function getPlanGoals() {
  return http.get<any, { code: number; data: { key: string; label: string }[] }>('/plans/goals')
}

export function getPlans(params?: { goal?: string; difficulty?: string }) {
  return http.get<any, { code: number; data: { items: Plan[]; total: number } }>('/plans', { params })
}

export function getPlanDetail(id: number) {
  return http.get<any, { code: number; data: Plan }>(`/plans/${id}`)
}

// ---------- User Plans ----------
export function cloneOfficialPlan(officialPlanId: number) {
  return http.post<any, any>('/user-plans/clone/' + officialPlanId)
}

export function getUserPlans() {
  return http.get<any, { code: number; data: { items: any[] } }>('/user-plans')
}

export function createUserPlan(data: any) {
  return http.post<any, any>('/user-plans', data)
}

export function updateUserPlan(id: number, data: any) {
  return http.put<any, any>('/user-plans/' + id, data)
}

export function deleteUserPlan(id: number) {
  return http.delete<any, any>('/user-plans/' + id)
}

export function getUserPlanDetail(id: number) {
  return http.get<any, any>('/user-plans/' + id)
}

// ---------- Training Logs ----------
export function logTraining(data: { plan_id: number; is_official: boolean; log_date?: string; focus?: string; exercises?: any[]; note?: string }) {
  return http.post<any, any>('/user-plans/training/log', data)
}

export function getTrainingLogs(params?: { days?: number; plan_id?: number }) {
  return http.get<any, any>('/user-plans/training/logs', { params })
}

export function getTrainingStats() {
  return http.get<any, any>('/user-plans/training/stats')
}
