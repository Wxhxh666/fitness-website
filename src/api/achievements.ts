import http from './http'

export interface AchievementItem {
  key: string
  name: string
  desc: string
  category: 'training' | 'streak' | 'body'
  category_label: string
  tier: 'gold' | 'silver' | 'bronze'
  icon: string
  metric: string
  unit: string
  current: number
  target: number
  progress: number
  unlocked: boolean
}

export interface AchievementSummary {
  unlocked: number
  total: number
  completion: number
  gold: number
  silver: number
  bronze: number
  by_category: Record<string, { total: number; unlocked: number }>
  next: AchievementItem | null
}

export interface AchievementData {
  items: AchievementItem[]
  summary: AchievementSummary
  stats: Record<string, number>
}

export function getAchievements() {
  return http.get<any, any>('/achievements')
}
