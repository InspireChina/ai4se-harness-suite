import http, { unwrap } from '@/utils/request'
import type { FavoriteItem } from '@/types'

/** 收藏相关接口（ACC）。 */
export const favoriteService = {
  list: () => unwrap(http.get<FavoriteItem[]>('/me/favorites')),

  /** 收藏咨询师（幂等） */
  add: (consultantId: string) => unwrap(http.post<FavoriteItem>('/me/favorites', { consultantId })),

  /** 取消收藏（幂等） */
  remove: (consultantId: string) => unwrap(http.delete<void>(`/me/favorites/${consultantId}`)),
}
