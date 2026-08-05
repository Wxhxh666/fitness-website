import http from './http'

export function generateDietPlan(data: any, regenerate = false) {
  return http.post<any, { code: number; data: any }>('/ai/diet-plan', { ...data, regenerate }, { timeout: 120000 })
}

export function saveDietPlan(data: any) {
  return http.post<any, { code: number; data: any }>('/ai/diet-plans', data)
}

export function getDietPlans() {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>('/ai/diet-plans')
}

export function getDietPlanDetail(id: number) {
  return http.get<any, { code: number; data: any }>(`/ai/diet-plans/${id}`)
}

export function deleteDietPlan(id: number) {
  return http.delete<any, { code: number; msg: string }>(`/ai/diet-plans/${id}`)
}

export function saveDietLog(data: any) {
  return http.post<any, { code: number; data: any }>('/ai/diet-logs', data)
}

export function getDietLogs(params?: { days?: number }) {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>('/ai/diet-logs', { params })
}

export function deleteDietLog(id: number) {
  return http.delete<any, { code: number; msg: string }>(`/ai/diet-logs/${id}`)
}

export function generateWeeklyReview() {
  return http.post<any, { code: number; data: any }>('/ai/weekly-review', {}, { timeout: 120000 })
}
