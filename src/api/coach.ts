import http, { API_BASE_URL } from './http'

/** 证件图片走受保护接口（带 token 的 blob），不能用 <img src> 直连 */
export async function fetchCredentialBlobUrl(applicationId: number, kind: 'front' | 'back' | 'cert'): Promise<string> {
  const token = localStorage.getItem('fitluxe_token')
  const res = await fetch(`${API_BASE_URL}/coaches/applications/${applicationId}/file/${kind}`, {
    headers: token ? { Authorization: 'Bearer ' + token } : {},
  })
  if (!res.ok) throw new Error('证件加载失败')
  return URL.createObjectURL(await res.blob())
}

export function getMyApplication() {
  return http.get<any, { code: number; data: { is_coach: boolean; application: any; profile: any } }>('/coaches/my-application')
}

export function applyCoach(form: {
  real_name: string
  phone: string
  cert_type: string
  bio?: string
  specialties?: string
  id_card_front: File
  id_card_back: File
  cert_file: File
}) {
  const fd = new FormData()
  Object.entries(form).forEach(([k, v]) => {
    if (v !== undefined && v !== null) fd.append(k, v as any)
  })
  return http.post<any, { code: number; msg: string; data: any }>('/coaches/apply', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ---------- 管理员审核 ----------
export function getCoachApplications(status = 'pending', page = 1, pageSize = 20) {
  return http.get<any, { code: number; data: { items: any[]; total: number } }>(
    '/admin/coach-applications',
    { params: { status, page, page_size: pageSize } },
  )
}

export function approveCoachApplication(id: number) {
  return http.put<any, { code: number; data: any }>(`/admin/coach-applications/${id}/approve`)
}

export function rejectCoachApplication(id: number, reason: string) {
  return http.put<any, { code: number; data: any }>(`/admin/coach-applications/${id}/reject`, { reason })
}

// ---------- 教练工作台 ----------
export function getCoachProfile() {
  return http.get<any, { code: number; data: any }>('/coaches/profile')
}

export function updateCoachProfile(data: Partial<{
  display_name: string
  bio: string
  specialties: string
  years: number
  avatar_url: string
}>) {
  return http.patch<any, { code: number; data: any }>('/coaches/profile', data)
}

export function getCoachDashboard() {
  return http.get<any, { code: number; data: any }>('/coaches/dashboard')
}

// ---------- M3 学员体系 ----------
export function getCoachList() {
  return http.get<any, { code: number; data: { items: any[] } }>('/coaches')
}

export function subscribeCoach(coachUserId: number, message?: string) {
  return http.post<any, { code: number; msg: string; data: any }>(
    `/coaches/${coachUserId}/subscribe`,
    { message: message || '' },
  )
}

export function getMyCoaches() {
  return http.get<any, { code: number; data: { items: any[] } }>('/coaches/mine')
}

export function terminateCoach(coachUserId: number) {
  return http.delete<any, { code: number; msg: string }>(`/coaches/mine/${coachUserId}`)
}

export function getCoachStudents(status = 'all') {
  return http.get<any, { code: number; data: { items: any[]; pending_total: number } }>(
    '/coaches/students',
    { params: { status } },
  )
}

export function acceptStudent(relationId: number) {
  return http.put<any, { code: number; msg: string; data: any }>(`/coaches/students/${relationId}/accept`)
}

export function rejectStudent(relationId: number, reason: string) {
  return http.put<any, { code: number; data: any }>(`/coaches/students/${relationId}/reject`, { reason })
}

export function getStudentOverview(relationId: number) {
  return http.get<any, { code: number; data: any }>(`/coaches/students/${relationId}/overview`)
}

export function getMessages(relationId: number, afterId = 0) {
  return http.get<any, { code: number; data: { relation: any; me: number; items: any[] } }>(
    `/coaches/students/${relationId}/messages`,
    { params: { after_id: afterId } },
  )
}

export function sendMessage(relationId: number, content: string) {
  return http.post<any, { code: number; data: any }>(
    `/coaches/students/${relationId}/messages`,
    { content },
  )
}

export function getUnreadTotal() {
  return http.get<any, { code: number; data: { total: number } }>('/coaches/unread-total')
}
