import axios from 'axios'
import http, { API_BASE_URL, getToken } from './http'

export interface BodyMetric {
  id: number; key: string; label: string; value: number; unit: string
  change: number; trend: string
}

export interface Measurement {
  id: number; key: string; label: string; value: number; unit: string
}

export interface BodyRecord {
  id: number
  record_date: string
  stage: string | null
  gender: string
  age: number | null
  activity_level: string
  height_cm: number | null
  weight_kg: number | null
  waist_cm: number | null
  hip_cm: number | null
  chest_cm: number | null
  shoulder_cm: number | null
  thigh_cm: number | null
  arm_cm: number | null
  calf_cm: number | null
  bmi: number | null
  body_fat: number | null
  bmr: number | null
  tdee: number | null
  whr: number | null
  muscle_mass: number | null
  standard_weight: number | null
}

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

export function calculateBodyMetrics(data: any) {
  return http.post<any, { code: number; data: any }>('/body-metrics/calculate', data)
}

export function saveBodyRecord(data: any) {
  return http.post<any, { code: number; data: BodyRecord }>('/body-metrics/records', data)
}

export function getBodyRecords(params?: { days?: number; limit?: number }) {
  return http.get<any, { code: number; data: { items: BodyRecord[]; total: number } }>('/body-metrics/records', { params })
}

export function deleteBodyRecord(id: number) {
  return http.delete<any, { code: number; msg: string }>(`/body-metrics/records/${id}`)
}

export function deleteAllBodyRecords() {
  return http.delete<any, { code: number; msg: string }>('/body-metrics/records')
}

export function compareBodyRecords(a: number, b: number) {
  return http.get<any, { code: number; data: any }>('/body-metrics/records/compare', { params: { a, b } })
}

export async function exportBodyRecords(): Promise<Blob> {
  const res = await axios.get(API_BASE_URL + '/body-metrics/export', {
    responseType: 'blob',
    headers: { Authorization: `Bearer ${getToken() || ''}` },
  })
  return res.data as Blob
}

export function getBodyProfile() {
  return http.get<any, { code: number; data: any }>('/body-metrics/profile')
}

export function saveBodyProfile(data: any) {
  return http.post<any, { code: number; data: any }>('/body-metrics/profile', data)
}

export function getBodyGoals() {
  return http.get<any, { code: number; data: { items: any[] } }>('/body-metrics/goals')
}

export function saveBodyGoal(data: any) {
  return http.post<any, { code: number; data: any }>('/body-metrics/goals', data)
}

export function deleteBodyGoal(id: number) {
  return http.delete<any, { code: number; msg: string }>(`/body-metrics/goals/${id}`)
}
