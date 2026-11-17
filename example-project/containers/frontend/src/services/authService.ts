import http, { unwrap } from '@/utils/request'
import type { LoginResponse } from '@/types'

/** 鉴权相关接口（ACC）。 */
export const authService = {
  /** 发送登录 / 注册验证码 */
  sendSmsCode: (phone: string) => unwrap(http.post<void>('/auth/sms/send', { phone })),

  /** 验证码登录或注册 */
  smsLogin: (payload: { phone: string; code: string; nickname?: string }) =>
    unwrap(http.post<LoginResponse>('/auth/sms/login', payload)),

  /** 管理员密码登录 */
  adminLogin: (payload: { phone: string; password: string }) =>
    unwrap(http.post<LoginResponse>('/auth/admin/login', payload)),
}
