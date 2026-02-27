import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const INACTIVITY_TIMEOUT = 30 * 60 * 1000 // 30分钟（毫秒）
let inactivityTimer = null

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const permissions = ref(JSON.parse(localStorage.getItem('permissions') || '[]'))

  const isAuthenticated = computed(() => !!token.value)

  // 重置无操作计时器
  function resetInactivityTimer() {
    if (inactivityTimer) {
      clearTimeout(inactivityTimer)
    }
    inactivityTimer = setTimeout(() => {
      // 30分钟无操作，自动登出
      logout()
    }, INACTIVITY_TIMEOUT)
  }

  // 清除无操作计时器
  function clearInactivityTimer() {
    if (inactivityTimer) {
      clearTimeout(inactivityTimer)
      inactivityTimer = null
    }
  }

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
    // 设置token时启动计时器
    resetInactivityTimer()
  }

  function setUser(newUser) {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function setPermissions(newPermissions) {
    permissions.value = newPermissions
    localStorage.setItem('permissions', JSON.stringify(newPermissions))
  }

  function logout() {
    token.value = ''
    user.value = null
    permissions.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('permissions')
    localStorage.removeItem('lastActivityTime')
    clearInactivityTimer()
  }

  return {
    token,
    user,
    permissions,
    isAuthenticated,
    setToken,
    setUser,
    setPermissions,
    logout,
    resetInactivityTimer
  }
})