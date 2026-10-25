import http from './http'

// ---------- 类型 ----------
export interface WorkoutSetPayload {
  exercise_name: string
  exercise_id?: number | null
  weight_kg?: number
  reps?: number
  rpe?: number | null
  is_warmup?: boolean
  note?: string
}

export interface WorkoutSetItem {
  id: number
  session_id: number
  exercise_id: number | null
  exercise_name: string
  set_index: number
  weight_kg: number
  reps: number
  rpe: number | null
  is_warmup: boolean
  note: string
  volume: number
  e1rm: number
}

export interface WorkoutGroup {
  exercise_name: string
  exercise_id: number | null
  sets: WorkoutSetItem[]
  total_volume: number
  best_e1rm: number
}

export interface WorkoutSessionItem {
  id: number
  session_date: string
  title: string
  focus: string
  plan_id: number | null
  note: string
  duration_min: number
  feeling: number | null
  total_sets: number
  total_reps: number
  total_volume: number
}

export interface RangeStats {
  sessions: number
  sets: number
  reps: number
  volume: number
  minutes: number
  avg_duration: number
}

export interface WorkoutOverview {
  today: RangeStats
  week: RangeStats
  month: RangeStats
  total: RangeStats
  current_streak: number
  longest_streak: number
  week_start: string
}

// ---------- 训练会话 ----------
export function listWorkoutSessions(params?: { days?: number; limit?: number; offset?: number }) {
  return http.get<any, any>('/workouts', { params })
}

export function createWorkoutSession(data: {
  session_date?: string
  title?: string
  focus?: string
  plan_id?: number | null
  note?: string
  duration_min?: number
  feeling?: number | null
}) {
  return http.post<any, any>('/workouts', data)
}

export function getWorkoutSession(id: number) {
  return http.get<any, any>(`/workouts/${id}`)
}

export function updateWorkoutSession(id: number, data: Partial<WorkoutSessionItem>) {
  return http.put<any, any>(`/workouts/${id}`, data)
}

export function deleteWorkoutSession(id: number) {
  return http.delete<any, any>(`/workouts/${id}`)
}

// ---------- 组 ----------
export function addWorkoutSets(sessionId: number, payload: WorkoutSetPayload | { sets: WorkoutSetPayload[] }) {
  return http.post<any, any>(`/workouts/${sessionId}/sets`, payload)
}

export function updateWorkoutSet(sessionId: number, setId: number, data: Partial<WorkoutSetPayload>) {
  return http.put<any, any>(`/workouts/${sessionId}/sets/${setId}`, data)
}

export function deleteWorkoutSet(sessionId: number, setId: number) {
  return http.delete<any, any>(`/workouts/${sessionId}/sets/${setId}`)
}

// ---------- 统计 ----------
export function getWorkoutOverview() {
  return http.get<any, any>('/workouts/overview')
}

export function getVolumeSeries(weeks = 12) {
  return http.get<any, any>('/workouts/volume-series', { params: { weeks } })
}

export function getWorkoutCalendar(month?: string) {
  return http.get<any, any>('/workouts/calendar', { params: month ? { month } : {} })
}

export function getPersonalRecords() {
  return http.get<any, any>('/workouts/prs')
}

export function getMyExercises() {
  return http.get<any, any>('/workouts/exercises')
}

export function getExerciseHistory(name: string, limit = 30) {
  return http.get<any, any>(`/workouts/exercises/${encodeURIComponent(name)}/history`, { params: { limit } })
}
