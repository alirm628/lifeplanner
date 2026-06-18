import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? ''

export const api = axios.create({
  baseURL: apiBaseUrl,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('lifeplanner_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('lifeplanner_token')
    }
    return Promise.reject(error)
  },
)

