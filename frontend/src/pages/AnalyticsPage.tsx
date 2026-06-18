import { useQuery } from '@tanstack/react-query'

import { getAnalyticsBreakdown, getAnalyticsHeatmap, getAnalyticsSummary, getAnalyticsTrends } from '../api/lifeplanner'

const weekdayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export function AnalyticsPage() {
  const summary = useQuery({ queryKey: ['analytics', 'summary'], queryFn: getAnalyticsSummary })
  const breakdown = useQuery({ queryKey: ['analytics', 'breakdown'], queryFn: getAnalyticsBreakdown })
  const trends = useQuery({ queryKey: ['analytics', 'trends'], queryFn: getAnalyticsTrends })
  const heatmap = useQuery({ queryKey: ['analytics', 'heatmap'], queryFn: getAnalyticsHeatmap })

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Analytics</h2>
        <p className="text-sm text-slate-500">Planned vs completed hours, trends, and productive windows.</p>
      </div>

      <div className="grid gap-3 md:grid-cols-5">
        <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <div className="text-xs text-slate-500">Planned</div>
          <div className="text-xl font-semibold">{summary.data?.planned_hours ?? 0}h</div>
        </div>
        <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <div className="text-xs text-slate-500">Completed</div>
          <div className="text-xl font-semibold">{summary.data?.completed_hours ?? 0}h</div>
        </div>
        <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <div className="text-xs text-slate-500">Missed</div>
          <div className="text-xl font-semibold">{summary.data?.missed_hours ?? 0}h</div>
        </div>
        <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <div className="text-xs text-slate-500">Consistency</div>
          <div className="text-xl font-semibold">{summary.data?.consistency_score ?? 0}%</div>
        </div>
        <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <div className="text-xs text-slate-500">Productivity</div>
          <div className="text-xl font-semibold">{summary.data?.productivity_score ?? 0}%</div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <h3 className="mb-2 font-medium">Category Breakdown</h3>
          <div className="space-y-2 text-sm">
            {(breakdown.data ?? []).map((item) => (
              <div key={item.category} className="flex justify-between rounded-lg bg-slate-100 px-3 py-2 dark:bg-slate-800">
                <span>{item.category}</span>
                <span>{item.completed_hours}h / {item.planned_hours}h</span>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <h3 className="mb-2 font-medium">Weekly Trend</h3>
          <div className="space-y-2 text-xs">
            {(trends.data ?? []).map((point) => (
              <div key={point.label} className="rounded-lg bg-slate-100 px-3 py-2 dark:bg-slate-800">
                {point.label}: {point.completed_hours}h completed / {point.planned_hours}h planned
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
        <h3 className="mb-2 font-medium">Productive Time Heatmap (basic)</h3>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {(heatmap.data ?? []).map((point) => (
            <div key={`${point.weekday}-${point.hour}`} className="rounded-lg bg-slate-100 px-2 py-1 text-xs dark:bg-slate-800">
              {weekdayLabels[point.weekday] ?? point.weekday} {String(point.hour).padStart(2, '0')}:00 — {point.count}
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

