export type EventType = 'fixed' | 'flexible'
export type LockMode = 'unlocked' | 'locked' | 'pinned_day' | 'pinned_time' | 'pinned_day_time'
export type ScheduleMode = 'full_auto' | 'respect_locks' | 'fill_gaps' | 'rebalance'
export type TaskStatus = 'todo' | 'in_progress' | 'done'
export type GoalStatus = 'active' | 'completed'

export interface User {
  id: number
  email: string
  is_active: boolean
  created_at: string
}

export interface Category {
  id: number
  user_id: number
  name: string
  color: string
  description: string | null
  priority: number
  weekly_target_hours: number
  max_blocks_per_day: number | null
  session_length_minutes: number
  min_session_minutes: number
  max_session_minutes: number
  preferred_days: string | null
  preferred_times: string | null
  default_location: string | null
  created_at: string
  updated_at: string
}

export interface CalendarEvent {
  id: number
  user_id: number
  category_id: number | null
  title: string
  description: string | null
  notes: string | null
  start_time: string
  end_time: string
  event_type: EventType
  lock_mode: LockMode
  recurrence_rule: string | null
  location: string | null
  estimated_minutes: number | null
  actual_minutes: number | null
  created_at: string
  updated_at: string
}

export interface Task {
  id: number
  user_id: number
  category_id: number | null
  title: string
  description: string | null
  notes: string | null
  priority: number
  status: TaskStatus
  due_date: string | null
  estimated_minutes: number | null
  actual_minutes: number | null
  tags: string[] | null
  created_at: string
  updated_at: string
}

export interface Goal {
  id: number
  user_id: number
  title: string
  description: string | null
  category_id: number | null
  target_hours: number | null
  target_sessions: number | null
  target_date: string | null
  status: GoalStatus
  created_at: string
  updated_at: string
}

export interface GoalProgress {
  goal_id: number
  title: string
  status: GoalStatus
  progress_hours: number
  progress_sessions: number
  target_hours: number | null
  target_sessions: number | null
}

export interface ScheduleTemplate {
  id: number
  user_id: number
  name: string
  description: string | null
  template_data: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface DashboardSummary {
  today_events: Array<Record<string, unknown>>
  upcoming_events: Array<Record<string, unknown>>
  weekly_planned_hours: Record<string, number>
  weekly_completed_hours: Record<string, number>
  remaining_free_hours: number
  total_planned_hours: number
  total_completed_hours: number
  generated_at: string
}

export interface ScheduleDiagnostics {
  per_category: Array<{
    category_id: number
    category_name: string
    target_hours: number
    scheduled_hours: number
    deficit_hours: number
    excess_hours: number
    blocks_scheduled: number
  }>
  total_target_hours: number
  total_scheduled_hours: number
  average_daily_flexible_hours: number
}

export interface SchedulerRun {
  run_id: number
  mode: ScheduleMode
  proposed_events: Array<{
    title: string
    description: string | null
    notes: string | null
    start_time: string
    end_time: string
    event_type: EventType
    lock_mode: LockMode
    recurrence_rule: string | null
    location: string | null
    category_id: number | null
  }>
  diagnostics: ScheduleDiagnostics
}

export interface AnalyticsSummary {
  planned_hours: number
  completed_hours: number
  missed_hours: number
  consistency_score: number
  productivity_score: number
}

export interface AnalyticsBreakdown {
  category: string
  planned_hours: number
  completed_hours: number
}

export interface AnalyticsTrendPoint {
  label: string
  planned_hours: number
  completed_hours: number
}

export interface AnalyticsHeatmapPoint {
  weekday: number
  hour: number
  count: number
}

export interface SearchResultItem {
  id: number
  type: string
  title: string
  subtitle: string | null
}

