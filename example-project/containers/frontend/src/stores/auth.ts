import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AccountInfo, UserProfile } from '@/types'

/** 登录态：token + 当前账号 + 资料。 */
export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<AccountInfo | null>(readJson<AccountInfo>('user'))
  const profile = ref<UserProfile | null>(readJson<UserProfile>('profile'))
  const isLoggedIn = computed(() => !!token.value)
  const roles = computed(() => user.value?.roles ?? [])

  function setLogin(payload: { token: string; account: AccountInfo; profile: UserProfile | null }) {
    token.value = payload.token
    user.value = payload.account
    profile.value = payload.profile
    localStorage.setItem('token', payload.token)
    localStorage.setItem('user', JSON.stringify(payload.account))
    if (payload.profile) localStorage.setItem('profile', JSON.stringify(payload.profile))
    else localStorage.removeItem('profile')
  }

  function setProfile(value: UserProfile | null) {
    profile.value = value
    if (value) localStorage.setItem('profile', JSON.stringify(value))
    else localStorage.removeItem('profile')
  }

  function logout() {
    token.value = ''
    user.value = null
    profile.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('profile')
  }

  function hasRole(role: string) {
    return roles.value.includes(role)
  }

  return { token, user, profile, isLoggedIn, roles, setLogin, setProfile, logout, hasRole }
})

function readJson<T>(key: string): T | null {
  const raw = localStorage.getItem(key)
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}
