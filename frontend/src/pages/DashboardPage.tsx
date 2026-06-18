import { useQuery } from '@tanstack/react-query'
import { CalendarClock, ChartNoAxesCombined, Clock3, Flame, Target } from 'lucide-react'

import { getDashboardSummary } from '../api/lifeplanner'
import { StatCard } from '../components/StatCard'
import { formatHours } from '../utils/date'

export function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard-summary'], queryFn: getDashboardSummary })

  if (isLoading || !data) {
    return <p className="text-sm text-slate-500">Loading dashboard...</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Dashboard</h2>
        <p className="text-sm text-slate-500">Your balance and momentum for this week.</p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard label="Planned Hours" value={formatHours(data.total_planned_hours)} icon={<CalendarClock className="h-4 w-4" />} />
        <StatCard label="Completed Hours" value={formatHours(data.total_completed_hours)} icon={<ChartNoAxesCombined className="h-4 w-4" />} />
        <StatCard label="Free Hours" value={formatHours(data.remaining_free_hours)} icon={<Clock3 className="h-4 w-4" />} />
        <StatCard label="Completion Rate" value={`${data.total_planned_hours ? Math.round((data.total_completed_hours / data.total_planned_hours) * 100) : 0}%`} icon={<Target className="h-4 w-4" />} />
        <StatCard label="Consistency" value={`${Math.min(100, Math.round((Object.keys(data.weekly_planned_hours).length / 8) * 100))}%`} icon={<Flame className="h-4 w-4" />} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
          <h3 className="mb-3 font-medium">Today&apos;s Schedule</h3>
          <div className="space-y-2">
            {data.today_events.length === 0 ? (
              <p className="text-sm text-slate-500">No events today.</p>
            ) : (
              data.today_events.map((event) => (
                <div key={String(event.id)} className="rounded-xl bg-slate-100 px-3 py-2 text-sm dark:bg-slate-800">
                  <div className="font-medium">{String(event.title)}</div>
                  <div className="text-xs text-slate-500">{String(event.start_time).slice(11, 16)} - {String(event.end_time).slice(11, 16)}</div>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
          <h3 className="mb-3 font-medium">Weekly Category Progress</h3>
          <div className="space-y-2">
            {Object.entries(data.weekly_planned_hours).map(([name, hours]) => (
              <div key={name}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span>{name}</span>
                  <span>{formatHours(hours)}</span>
                </div>
                <div className="h-2 rounded-full bg-slate-200 dark:bg-slate-800">
                  <div className="h-2 rounded-full bg-sky-500" style={{ width: `${Math.min(100, hours * 8)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

