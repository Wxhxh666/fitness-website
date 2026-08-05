import http from './http'

export function submitContact(data: { name: string; email: string; phone?: string; subject: string; message: string }) {
  return http.post<any, { code: number; data: { id: number } }>('/contact', data)
}

export function getContactInfo() {
  return http.get<any, { code: number; data: { address: string; phone: string; email: string; business_hours: any; social_media: any[] } }>('/site/contact-info')
}
