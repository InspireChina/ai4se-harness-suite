/**
 * 当前生效的协议版本。
 * 协议中心（PLT）上线后改为后端下发。
 */
export const AGREEMENT_VERSIONS: Record<string, string> = {
  service: 'v1',
  privacy: 'v1',
}

export const AGREEMENT_LABELS: Record<string, string> = {
  service: '服务协议',
  privacy: '隐私政策',
}
