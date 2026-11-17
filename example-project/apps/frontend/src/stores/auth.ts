import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/** Auth store shell — wire login/register when ACC is implemented. */
export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const isLoggedIn = computed(() => !!token.value)

  function logout() {
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, isLoggedIn, logout }
})
