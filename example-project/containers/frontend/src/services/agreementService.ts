import http, { unwrap } from '@/utils/request'
import type { AgreementConsent } from '@/types'

/** 协议同意相关接口（ACC）。 */
export const agreementService = {
  list: () => unwrap(http.get<AgreementConsent[]>('/me/agreements')),

  /** 记录协议同意（按类型 + 版本幂等） */
  consent: (agreementType: string, agreementVersion: string) =>
    unwrap(http.post<AgreementConsent>('/me/agreements', { agreementType, agreementVersion })),
}
