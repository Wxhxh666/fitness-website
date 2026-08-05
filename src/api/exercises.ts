import http from './http'

export interface Exercise {
  id: number; name: string; category: string; category_label: string
  description: string; difficulty: string; difficulty_label: string
  duration: string; cover_url: string; steps?: any[]; target_muscles?: string[]
}

export function getExerciseCategories() {
  return http.get<any, { code: number; data: { key: string; label: string }[] }>('/exercises/categories')
}

export function getExercises(params?: { category?: string; difficulty?: string; keyword?: string }) {
  return http.get<any, { code: number; data: { items: Exercise[]; total: number } }>('/exercises', { params })
}

export function getExerciseDetail(id: number) {
  return http.get<any, { code: number; data: Exercise }>(`/exercises/${id}`)
}
