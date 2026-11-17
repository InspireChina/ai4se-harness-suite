import axios from 'axios'
import type { AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiError } from '@/types'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

http.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

http.interceptors.response.use(
  r => r,
  e => {
    const status = e.response?.status
    const data = e.response?.data as ApiError | undefined
    if (status === 401) {
      // Token 过期 / 无效 / 账号被禁用 → 清除登录态并回到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('profile')
      if (!location.pathname.startsWith('/user/login')) {
        location.href = '/user/login'
      }
      return Promise.reject(e)
    }
    if (status === 403) {
      ElMessage.error(data?.errorMessage || '无权访问该资源')
      return Promise.reject(e)
    }
    if (status === 409) {
      ElMessage.warning(data?.errorMessage || '操作冲突')
      return Promise.reject(e)
    }
    if (status === 400) {
      // 具体提示交由调用方展示
      return Promise.reject(e)
    }
    if (status && status >= 500) {
      ElMessage.error('系统繁忙，请稍后重试')
      return Promise.reject(e)
    }
    return Promise.reject(e)
  }
)

export default http

/** 取出响应体（约定：成功响应直接返回 data）。 */
export async function unwrap<T>(promise: Promise<AxiosResponse<T>>): Promise<T> {
  const response = await promise
  return response.data
}
