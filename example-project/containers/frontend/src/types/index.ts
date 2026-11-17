/** 共享前端类型 —— 对齐 docs/facts/api.yaml（ACC 账号与个人中心）。 */

export interface HealthResponse {
  status: string
}

export interface AccountInfo {
  id: string
  roles: string[]
  status: string
  phone: string | null
  phoneVerifiedAt: string | null
  lastLoginAt: string | null
  disabledReason: string | null
  createdAt: string
  updatedAt: string
}

export interface UserProfile {
  accountId: string
  nickname: string
  avatarUrl: string | null
  email: string | null
  cityCode: string | null
  locale: string
  updatedAt: string
}

export interface MeResponse {
  account: AccountInfo
  profile: UserProfile | null
}

export interface LoginResponse {
  token: string
  account: AccountInfo
  profile: UserProfile | null
}

export interface FavoriteItem {
  id: string
  consultantId: string
  createdAt: string
}

export interface AgreementConsent {
  id: string
  agreementType: string
  agreementVersion: string
  consentedAt: string
  sourceIp: string
}

export interface ApiError {
  errorCode: string
  errorMessage: string
  data: unknown
}
