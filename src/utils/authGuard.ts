import { ElMessage } from 'element-plus'
import { isLoggedIn } from '@/api'

/**
 * 需要登录才能执行的动作（保存记录、生成 AI 方案、打卡等）统一走这里。
 * 返回 false 时调用方直接 return，避免发出必然 401 的请求。
 */
export function ensureLogin(message = '请先登录后再操作'): boolean {
  if (isLoggedIn()) return true
  ElMessage.warning(message)
  return false
}

/** 跳转登录页，并记录来源页以便登录后返回 */
export function goLogin(redirect?: string) {
  const target = redirect || (window.location.pathname + window.location.search)
  window.location.href = `/login?redirect=${encodeURIComponent(target)}`
}
