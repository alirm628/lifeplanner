import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { exportBackup, getSettings, importBackup, updateSettings } from '../api/lifeplanner'

type SettingsDraft = {
  workday_start_hour: number
  workday_end_hour: number
  min_gap_between_flexible_minutes: number
  max_flexible_minutes_per_day: number
  max_same_category_blocks_per_day: number
}

export function SettingsPage() {
  const queryClient = useQueryClient()
  const settings = useQuery({ queryKey: ['settings'], queryFn: getSettings })

  const [draft, setDraft] = useState<SettingsDraft | null>(null)
  const [isDirty, setIsDirty] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  const effective: SettingsDraft = draft ?? {
    workday_start_hour: settings.data?.workday_start_hour ?? 8,
    workday_end_hour: settings.data?.workday_end_hour ?? 22,
    min_gap_between_flexible_minutes: settings.data?.min_gap_between_flexible_minutes ?? 30,
    max_flexible_minutes_per_day: settings.data?.max_flexible_minutes_per_day ?? 360,
    max_same_category_blocks_per_day: settings.data?.max_same_category_blocks_per_day ?? 2,
  }

  const update = useMutation({
    mutationFn: updateSettings,
    onSuccess: async () => {
      setIsDirty(false)
      setDraft(null)
      setMessage('Settings saved.')
      await queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
    onError: () => {
      setMessage('Failed to save settings.')
    },
  })

  const backup = useMutation({
    mutationFn: exportBackup,
    onSuccess: (data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `lifeplanner-backup-${new Date().toISOString().slice(0, 10)}.json`
      link.click()
      URL.revokeObjectURL(url)
    },
  })

  const restore = useMutation({
    mutationFn: (payload: Record<string, unknown>) => importBackup(payload),
  })

  async function handleImport(file: File | null) {
    if (!file) return
    const text = await file.text()
    const json = JSON.parse(text) as Record<string, unknown>
    restore.mutate(json)
  }

  function saveChanges() {
    update.mutate(effective)
  }

  function setField<K extends keyof SettingsDraft>(key: K, value: SettingsDraft[K]) {
    setDraft((current) => ({
      ...(current ?? effective),
      [key]: value,
    }))
    setIsDirty(true)
    setMessage(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Settings</h2>
          <p className="text-sm text-slate-500">Customize defaults and manage backups.</p>
        </div>

        <button
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          type="button"
          onClick={saveChanges}
          disabled={!isDirty || update.isPending}
        >
          {update.isPending ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {message ? <div className="rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700">{message}</div> : null}

      <section className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
        <h3 className="mb-3 font-medium">Workday Window</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            Start hour
            <input
              type="number"
              min={0}
              max={23}
              value={effective.workday_start_hour}
              onChange={(event) => setField('workday_start_hour', Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-800"
            />
          </label>

          <label className="text-sm">
            End hour
            <input
              type="number"
              min={1}
              max={24}
              value={effective.workday_end_hour}
              onChange={(event) => setField('workday_end_hour', Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-800"
            />
          </label>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
        <h3 className="mb-3 font-medium">Scheduler Distribution</h3>
        <div className="grid gap-3 sm:grid-cols-3">
          <label className="text-sm">
            Min gap (minutes)
            <input
              type="number"
              min={0}
              max={180}
              value={effective.min_gap_between_flexible_minutes}
              onChange={(event) => setField('min_gap_between_flexible_minutes', Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-800"
            />
          </label>

          <label className="text-sm">
            Max flexible/day (minutes)
            <input
              type="number"
              min={60}
              max={900}
              value={effective.max_flexible_minutes_per_day}
              onChange={(event) => setField('max_flexible_minutes_per_day', Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-800"
            />
          </label>

          <label className="text-sm">
            Max same-category blocks/day
            <input
              type="number"
              min={1}
              max={10}
              value={effective.max_same_category_blocks_per_day}
              onChange={(event) => setField('max_same_category_blocks_per_day', Number(event.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-800"
            />
          </label>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
        <h3 className="mb-3 font-medium">Backup & Restore</h3>
        <div className="flex flex-wrap items-center gap-3">
          <button className="rounded-lg bg-sky-500 px-3 py-2 text-sm text-white" type="button" onClick={() => backup.mutate()}>
            One-click Backup
          </button>

          <label className="rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700">
            Import Backup
            <input type="file" className="hidden" accept="application/json" onChange={(event) => handleImport(event.target.files?.[0] ?? null)} />
          </label>
        </div>
      </section>
    </div>
  )
}
