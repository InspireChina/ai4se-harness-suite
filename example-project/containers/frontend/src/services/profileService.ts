import http, { unwrap } from '@/utils/request'
import type { MeResponse, UserProfile } from '@/types'

/** 个人资料相关接口（ACC）。 */
export const profileService = {
  /** 当前账号与资料 */
  me: () => unwrap(http.get<MeResponse>('/me')),

  /** 更新本人资料 */
  updateProfile: (payload: {
    nickname?: string
    avatarUrl?: string
    email?: string
    cityCode?: string
    locale?: string
  }) => unwrap(http.put<UserProfile>('/me/profile', payload)),
}
