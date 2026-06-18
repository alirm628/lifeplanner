import { addDays, startOfWeek, toLocalDateTimeString } from '../utils/date'
import type {
  AnalyticsBreakdown,
  AnalyticsHeatmapPoint,
  AnalyticsSummary,
  AnalyticsTrendPoint,
  CalendarEvent,
  Category,
  DashboardSummary,
  Goal,
  GoalProgress,
  ScheduleMode,
  ScheduleTemplate,
  SchedulerRun,
  SearchResultItem,
  Task,
  User,
} from '../types'
import { api } from './client'

export async function login(email: string, password: string) {
  const { data } = await api.post<{ access_token: string; token_type: string }>('/api/v1/auth/login', { email, password })
  return data
}

export async function me() {
  const { data } = await api.get<User>('/api/v1/auth/me')
  return data
}

export async function getCategories(query?: string) {
  const { data } = await api.get<Category[]>('/api/v1/categories', { params: query ? { q: query } : undefined })
  return data
}

export async function createCategory(payload: Partial<Category> & { name: string }) {
  const { data } = await api.post<Category>('/api/v1/categories', payload)
  return data
}

export async function updateCategory(categoryId: number, payload: Partial<Category>) {
  const { data } = await api.patch<Category>(`/api/v1/categories/${categoryId}`, payload)
  return data
}

export async function deleteCategory(categoryId: number) {
  await api.delete(`/api/v1/categories/${categoryId}`)
}

export async function getEvents(weekStart?: Date, categoryId?: number, query?: string) {
  const params: Record<string, string | number> = {}
  if (weekStart) {
    params.week_start = toLocalDateTimeString(startOfWeek(weekStart)).slice(0, 10)
    params.week_end = toLocalDateTimeString(addDays(startOfWeek(weekStart), 7)).slice(0, 10)
  }
  if (categoryId) {
    params.category_id = categoryId
  }
  if (query) {
    params.q = query
  }

  const { data } = await api.get<CalendarEvent[]>('/api/v1/events', { params })
  return data
}

export async function createEvent(payload: Partial<CalendarEvent> & { title: string; start_time: string; end_time: string }) {
  const { data } = await api.post<CalendarEvent>('/api/v1/events', payload)
  return data
}

export async function updateEvent(eventId: number, payload: Partial<CalendarEvent>) {
  const { data } = await api.patch<CalendarEvent>(`/api/v1/events/${eventId}`, payload)
  return data
}

export async function deleteEvent(eventId: number) {
  await api.delete(`/api/v1/events/${eventId}`)
}

export async function duplicateEvent(eventId: number, dayOffset = 1) {
  const { data } = await api.post<CalendarEvent>(`/api/v1/events/${eventId}/duplicate`, { day_offset: dayOffset })
  return data
}

export async function generateSchedule(weekStart: Date, mode: ScheduleMode) {
  const { data } = await api.post<SchedulerRun>('/api/v1/scheduler/generate', {
    week_start: toLocalDateTimeString(startOfWeek(weekStart)).slice(0, 10),
    mode,
  })
  return data
}

export async function applySchedule(runId: number) {
  const { data } = await api.post<{ status: string }>('/api/v1/scheduler/apply', { run_id: runId })
  return data
}

export async function getDashboardSummary() {
  const { data } = await api.get<DashboardSummary>('/api/v1/dashboard/summary')
  return data
}

export async function getSettings() {
  const { data } = await api.get('/api/v1/settings')
  return data
}

export async function updateSettings(payload: Record<string, unknown>) {
  const { data } = await api.patch('/api/v1/settings', payload)
  return data
}

export async function exportBackup() {
  const { data } = await api.get('/api/v1/backup/export')
  return data
}

export async function importBackup(payload: Record<string, unknown>) {
  const { data } = await api.post('/api/v1/backup/import', payload)
  return data
}

export async function getTasks(query?: string) {
  const { data } = await api.get<Task[]>('/api/v1/tasks', { params: query ? { q: query } : undefined })
  return data
}

export async function createTask(payload: Partial<Task> & { title: string }) {
  const { data } = await api.post<Task>('/api/v1/tasks', payload)
  return data
}

export async function updateTask(taskId: number, payload: Partial<Task>) {
  const { data } = await api.patch<Task>(`/api/v1/tasks/${taskId}`, payload)
  return data
}

export async function deleteTask(taskId: number) {
  await api.delete(`/api/v1/tasks/${taskId}`)
}

export async function getGoals(query?: string) {
  const { data } = await api.get<Goal[]>('/api/v1/goals', { params: query ? { q: query } : undefined })
  return data
}

export async function getGoalProgress() {
  const { data } = await api.get<GoalProgress[]>('/api/v1/goals/progress')
  return data
}

export async function createGoal(payload: Partial<Goal> & { title: string }) {
  const { data } = await api.post<Goal>('/api/v1/goals', payload)
  return data
}

export async function updateGoal(goalId: number, payload: Partial<Goal>) {
  const { data } = await api.patch<Goal>(`/api/v1/goals/${goalId}`, payload)
  return data
}

export async function deleteGoal(goalId: number) {
  await api.delete(`/api/v1/goals/${goalId}`)
}

export async function getTemplates(query?: string) {
  const { data } = await api.get<ScheduleTemplate[]>('/api/v1/templates', { params: query ? { q: query } : undefined })
  return data
}

export async function createTemplate(payload: Partial<ScheduleTemplate> & { name: string; template_data: Record<string, unknown> }) {
  const { data } = await api.post<ScheduleTemplate>('/api/v1/templates', payload)
  return data
}

export async function applyTemplate(templateId: number, weekStart: Date) {
  const { data } = await api.post(`/api/v1/templates/${templateId}/apply`, null, {
    params: { week_start: toLocalDateTimeString(startOfWeek(weekStart)) },
  })
  return data
}

export async function deleteTemplate(templateId: number) {
  await api.delete(`/api/v1/templates/${templateId}`)
}

export async function createTemplateFromWeek(name: string, weekStart: Date, description?: string) {
  const { data } = await api.post<ScheduleTemplate>('/api/v1/templates/from-week', null, {
    params: { name, week_start: toLocalDateTimeString(startOfWeek(weekStart)), description },
  })
  return data
}

export async function getAnalyticsSummary() {
  const { data } = await api.get<AnalyticsSummary>('/api/v1/analytics/summary')
  return data
}

export async function getAnalyticsBreakdown() {
  const { data } = await api.get<AnalyticsBreakdown[]>('/api/v1/analytics/breakdown')
  return data
}

export async function getAnalyticsTrends() {
  const { data } = await api.get<AnalyticsTrendPoint[]>('/api/v1/analytics/trends')
  return data
}

export async function getAnalyticsHeatmap() {
  const { data } = await api.get<AnalyticsHeatmapPoint[]>('/api/v1/analytics/heatmap')
  return data
}

export async function searchAll(q: string) {
  const { data } = await api.get<{ results: SearchResultItem[] }>('/api/v1/search', { params: { q } })
  return data.results
}


