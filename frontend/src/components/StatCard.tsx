import type { ReactNode } from 'react'

interface StatCardProps {
  label: string
  value: string
  icon?: ReactNode
}

export function StatCard({ label, value, icon }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-4 dark:border-slate-800 dark:from-slate-900 dark:to-slate-800">
      <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
        <span>{label}</span>
        {icon}
      </div>
      <div className="text-2xl font-semibold tracking-tight">{value}</div>
    </div>
  )
}

