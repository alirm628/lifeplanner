import FullCalendar from '@fullcalendar/react'
import timeGridPlugin from '@fullcalendar/timegrid'
import dayGridPlugin from '@fullcalendar/daygrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'
import type { DateSelectArg, EventClickArg, EventDropArg } from '@fullcalendar/core/index.js'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'

import {
  applySchedule,
  createCategory,
  deleteCategory,
  createEvent,
  deleteEvent,
  duplicateEvent,
  generateSchedule,
  getCategories,
  getEvents,
  updateCategory,
  updateEvent,
} from '../api/lifeplanner'
import type { CalendarEvent, Category, EventType, LockMode, ScheduleMode, SchedulerRun } from '../types'
import { startOfWeek, toLocalDateTimeString } from '../utils/date'

const lockOrder: LockMode[] = ['unlocked', 'locked', 'pinned_day', 'pinned_time', 'pinned_day_time']
const legacyPreferredTimeMap: Record<string, { start: string; end: string }> = {
  morning: { start: '05:00', end: '12:00' },
  afternoon: { start: '12:00', end: '17:00' },
  evening: { start: '17:00', end: '22:00' },
  night: { start: '22:00', end: '05:00' },
}

function parsePreferredTimeRange(value: string | null | undefined): { start: string; end: string } {
  if (!value) return { start: '', end: '' }
  const first = value.split(',')[0]?.trim().toLowerCase() ?? ''
  if (!first) return { start: '', end: '' }
  if (legacyPreferredTimeMap[first]) return legacyPreferredTimeMap[first]
  const [start, end] = first.split('-', 2).map((part) => part?.trim() ?? '')
  if (/^\d{2}:\d{2}$/.test(start) && /^\d{2}:\d{2}$/.test(end)) {
    return { start, end }
  }
  return { start: '', end: '' }
}

function composePreferredTimeRange(start: string, end: string): { value: string | null; error: string | null } {
  const s = start.trim()
  const e = end.trim()
  if (!s && !e) return { value: null, error: null }
  if (!s || !e) return { value: null, error: 'Set both preferred start and end times, or leave both blank.' }
  if (!/^\d{2}:\d{2}$/.test(s) || !/^\d{2}:\d{2}$/.test(e)) {
    return { value: null, error: 'Preferred time must use HH:MM format.' }
  }
  if (s === e) return { value: null, error: 'Preferred start and end times cannot be the same.' }
  return { value: `${s}-${e}`, error: null }
}

type EventResizeLikeArg = { event: { id: string; start: Date | null; end: Date | null }; revert: () => void }

const initialCategoryForm = {
  name: '',
  color: '#0ea5e9',
  weekly_target_hours: 4,
  max_blocks_per_day: '2',
  session_length_minutes: 60,
  priority: 3,
  preferred_days: '',
  preferred_start_time: '',
  preferred_end_time: '',
}

export function CalendarPage() {
  const queryClient = useQueryClient()
  const [weekAnchor, setWeekAnchor] = useState(new Date())
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<number | undefined>(undefined)
  const [preview, setPreview] = useState<SchedulerRun | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [schedulerMode, setSchedulerMode] = useState<ScheduleMode>('full_auto')

  const [showCategoryForm, setShowCategoryForm] = useState(false)
  const [categoryForm, setCategoryForm] = useState(initialCategoryForm)
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null)
  const [selectedPreferredStart, setSelectedPreferredStart] = useState('')
  const [selectedPreferredEnd, setSelectedPreferredEnd] = useState('')

  const [quickEventTitle, setQuickEventTitle] = useState('')
  const [quickEventDuration, setQuickEventDuration] = useState(60)

  const [selectedEventId, setSelectedEventId] = useState<number | null>(null)

  const categories = useQuery({ queryKey: ['categories', search], queryFn: () => getCategories(search) })
  const events = useQuery({
    queryKey: ['events', toLocalDateTimeString(startOfWeek(weekAnchor)), categoryFilter ?? 'all', search],
    queryFn: () => getEvents(weekAnchor, categoryFilter, search),
  })

  const createEventMutation = useMutation({
    mutationFn: createEvent,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['events'] }),
  })

  const updateEventMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<CalendarEvent> }) => updateEvent(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['events'] }),
  })

  const deleteEventMutation = useMutation({
    mutationFn: deleteEvent,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['events'] }),
  })

  const duplicateMutation = useMutation({
    mutationFn: ({ id, dayOffset }: { id: number; dayOffset: number }) => duplicateEvent(id, dayOffset),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['events'] }),
  })

  const createCategoryMutation = useMutation({
    mutationFn: createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setCategoryForm(initialCategoryForm)
      setShowCategoryForm(false)
    },
  })

  const updateCategoryMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<Category> }) => updateCategory(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] }),
  })

  const deleteCategoryMutation = useMutation({
    mutationFn: deleteCategory,
    onSuccess: () => {
      setSelectedCategoryId(null)
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      queryClient.invalidateQueries({ queryKey: ['events'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
      setErrorMessage(null)
    },
    onError: () => setErrorMessage('Failed to delete category.'),
  })

  const generateMutation = useMutation({
    mutationFn: ({ mode }: { mode: ScheduleMode }) => generateSchedule(weekAnchor, mode),
    onSuccess: (run) => {
      setPreview(run)
      setErrorMessage(null)
    },
    onError: () => setErrorMessage('Failed to generate schedule.'),
  })

  const applyMutation = useMutation({
    mutationFn: (runId: number) => applySchedule(runId),
    onSuccess: () => {
      setPreview(null)
      queryClient.invalidateQueries({ queryKey: ['events'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
      setErrorMessage(null)
    },
    onError: () => setErrorMessage('Failed to apply generated schedule.'),
  })

  const categoryColorMap = useMemo(() => {
    const map = new Map<number, string>()
    categories.data?.forEach((category) => map.set(category.id, category.color))
    return map
  }, [categories.data])

  const selectedEvent = useMemo(
    () => (events.data ?? []).find((event) => event.id === selectedEventId) ?? null,
    [events.data, selectedEventId],
  )

  const selectedCategory = useMemo(
    () => (categories.data ?? []).find((category) => category.id === selectedCategoryId) ?? null,
    [categories.data, selectedCategoryId],
  )

  useEffect(() => {
    if (!selectedCategory) {
      setSelectedPreferredStart('')
      setSelectedPreferredEnd('')
      return
    }
    const parsed = parsePreferredTimeRange(selectedCategory.preferred_times)
    setSelectedPreferredStart(parsed.start)
    setSelectedPreferredEnd(parsed.end)
  }, [selectedCategory])

  function quickCreateEventNow() {
    const title = quickEventTitle.trim()
    if (!title) {
      setErrorMessage('Event title is required.')
      return
    }
    const now = new Date()
    const rounded = new Date(now)
    rounded.setMinutes(Math.ceil(now.getMinutes() / 15) * 15, 0, 0)
    const end = new Date(rounded.getTime() + quickEventDuration * 60 * 1000)

    createEventMutation.mutate(
      {
        title,
        start_time: toLocalDateTimeString(rounded),
        end_time: toLocalDateTimeString(end),
        event_type: 'flexible',
        lock_mode: 'unlocked',
      },
      {
        onSuccess: () => {
          setQuickEventTitle('')
          setErrorMessage(null)
        },
        onError: () => setErrorMessage('Failed to create event.'),
      },
    )
  }

  function handleSelect(selection: DateSelectArg) {
    const title = quickEventTitle.trim() || 'New Block'
    createEventMutation.mutate(
      {
        title,
        start_time: toLocalDateTimeString(selection.start),
        end_time: toLocalDateTimeString(selection.end),
        event_type: 'flexible',
        lock_mode: 'unlocked',
      },
      {
        onError: () => setErrorMessage('Failed to create selected block.'),
      },
    )
  }

  async function persistEventMove(eventId: number, startIso: string, endIso: string, revert: () => void) {
    try {
      await updateEventMutation.mutateAsync({ id: eventId, payload: { start_time: startIso, end_time: endIso } })
      setErrorMessage(null)
    } catch {
      revert()
      setErrorMessage('Move failed. Event was restored to original position.')
    }
  }

  function handleEventDrop(change: EventDropArg) {
    const idRaw = change.event.id
    if (!/^\d+$/.test(idRaw)) {
      change.revert()
      return
    }

    const source = events.data?.find((event) => event.id === Number(idRaw))
    if (!source) {
      change.revert()
      return
    }

    const immovable = source.event_type === 'fixed' || source.lock_mode !== 'unlocked'
    if (immovable) {
      change.revert()
      setErrorMessage('Fixed or locked events cannot be moved.')
      return
    }

    const start = change.event.start
    if (!start) {
      change.revert()
      return
    }

    const originalDuration =
      new Date(source.end_time).getTime() -
      new Date(source.start_time).getTime()
    const end = change.event.end ?? new Date(start.getTime() + originalDuration)

    void persistEventMove(source.id, toLocalDateTimeString(start), toLocalDateTimeString(end), change.revert)
  }

  function handleEventResize(change: EventResizeLikeArg) {
    const idRaw = change.event.id
    if (!/^\d+$/.test(idRaw)) {
      change.revert()
      return
    }

    const source = events.data?.find((event) => event.id === Number(idRaw))
    if (!source) {
      change.revert()
      return
    }

    const immovable = source.event_type === 'fixed' || source.lock_mode !== 'unlocked'
    if (immovable) {
      change.revert()
      setErrorMessage('Fixed or locked events cannot be resized.')
      return
    }

    const start = change.event.start
    const end = change.event.end
    if (!start || !end) {
      change.revert()
      return
    }

    void persistEventMove(source.id, toLocalDateTimeString(start), toLocalDateTimeString(end), change.revert)
  }

  function handleEventClick(click: EventClickArg) {
    if (!/^\d+$/.test(click.event.id)) {
      return
    }
    setSelectedEventId(Number(click.event.id))
  }

  function createCategoryWithValidation() {
    if (!categoryForm.name.trim()) {
      setErrorMessage('Category name is required.')
      return
    }
    if (categoryForm.session_length_minutes < 15) {
      setErrorMessage('Session length must be at least 15 minutes.')
      return
    }
    if (categoryForm.max_blocks_per_day) {
      const maxBlocks = Number(categoryForm.max_blocks_per_day)
      if (Number.isNaN(maxBlocks) || maxBlocks < 1 || maxBlocks > 12) {
        setErrorMessage('Max blocks per day must be between 1 and 12.')
        return
      }
    }
    const preferred = composePreferredTimeRange(categoryForm.preferred_start_time, categoryForm.preferred_end_time)
    if (preferred.error) {
      setErrorMessage(preferred.error)
      return
    }

    createCategoryMutation.mutate({
      name: categoryForm.name.trim(),
      color: categoryForm.color,
      weekly_target_hours: categoryForm.weekly_target_hours,
      max_blocks_per_day: categoryForm.max_blocks_per_day ? Number(categoryForm.max_blocks_per_day) : null,
      session_length_minutes: categoryForm.session_length_minutes,
      min_session_minutes: categoryForm.session_length_minutes,
      max_session_minutes: categoryForm.session_length_minutes,
      priority: categoryForm.priority,
      preferred_days: categoryForm.preferred_days || null,
      preferred_times: preferred.value,
    })
  }

  function saveSelectedCategoryPatch(patch: Partial<Category>) {
    if (!selectedCategoryId) return
    updateCategoryMutation.mutate({ id: selectedCategoryId, payload: patch })
  }

  function deleteSelectedCategory() {
    if (!selectedCategoryId) return
    const confirmed = window.confirm('Delete this category? All calendar blocks in this category will be deleted.')
    if (!confirmed) return
    deleteCategoryMutation.mutate(selectedCategoryId)
  }

  function saveSelectedCategoryPreferredTimeRange() {
    if (!selectedCategoryId) return
    const preferred = composePreferredTimeRange(selectedPreferredStart, selectedPreferredEnd)
    if (preferred.error) {
      setErrorMessage(preferred.error)
      return
    }
    saveSelectedCategoryPatch({ preferred_times: preferred.value })
    setErrorMessage(null)
  }

  function updateSelectedEvent(patch: Partial<CalendarEvent>) {
    if (!selectedEvent) return
    updateEventMutation.mutate(
      { id: selectedEvent.id, payload: patch },
      {
        onSuccess: () => {
          setSelectedEventId(selectedEvent.id)
          setErrorMessage(null)
        },
        onError: () => setErrorMessage('Failed to update event.'),
      },
    )
  }

  const calendarEvents = (events.data ?? []).map((event) => {
    const editable = event.event_type === 'flexible' && event.lock_mode === 'unlocked'
    return {
      id: String(event.id),
      title: event.title,
      start: event.start_time,
      end: event.end_time,
      editable,
      startEditable: editable,
      durationEditable: editable,
      backgroundColor: event.category_id ? categoryColorMap.get(event.category_id) : '#64748b',
      borderColor: event.category_id ? categoryColorMap.get(event.category_id) : '#64748b',
    }
  })

  const previewEvents = (preview?.proposed_events ?? []).map((event, index) => ({
    id: `preview-${index}`,
    title: `${event.title} (Preview)`,
    start: event.start_time,
    end: event.end_time,
    editable: false,
    startEditable: false,
    durationEditable: false,
    className: 'opacity-90',
    backgroundColor: 'rgba(14,165,233,0.18)',
    borderColor: '#0ea5e9',
    textColor: '#0369a1',
  }))

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Calendar</h2>
        <p className="text-sm text-slate-500">Intuitive weekly planning with safer drag-and-drop and smart distribution.</p>
      </div>

      {errorMessage ? <div className="rounded-lg border border-rose-300 bg-rose-50 px-3 py-2 text-sm text-rose-700">{errorMessage}</div> : null}

      <div className="grid gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-800 lg:grid-cols-12">
        <div className="lg:col-span-3">
          <label className="mb-1 block text-xs font-medium">Search</label>
          <input
            placeholder="Search events/categories"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          />
        </div>

        <div className="lg:col-span-2">
          <label className="mb-1 block text-xs font-medium">Category Filter</label>
          <select
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            value={categoryFilter ?? ''}
            onChange={(event) => setCategoryFilter(event.target.value ? Number(event.target.value) : undefined)}
          >
            <option value="">All Categories</option>
            {(categories.data ?? []).map((category) => (
              <option key={category.id} value={category.id}>{category.name}</option>
            ))}
          </select>
        </div>

        <div className="lg:col-span-3">
          <label className="mb-1 block text-xs font-medium">Quick Add Event</label>
          <div className="flex gap-2">
            <input
              value={quickEventTitle}
              onChange={(event) => setQuickEventTitle(event.target.value)}
              placeholder="Event title"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            />
            <input
              type="number"
              min={15}
              step={15}
              value={quickEventDuration}
              onChange={(event) => setQuickEventDuration(Number(event.target.value))}
              className="w-20 rounded-lg border border-slate-300 bg-white px-2 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
              title="Minutes"
            />
            <button className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white dark:bg-slate-100 dark:text-slate-900" type="button" onClick={quickCreateEventNow}>
              Add
            </button>
          </div>
        </div>

        <div className="lg:col-span-2">
          <label className="mb-1 block text-xs font-medium">Scheduler Mode</label>
          <select
            value={schedulerMode}
            onChange={(event) => setSchedulerMode(event.target.value as ScheduleMode)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          >
            <option value="full_auto">Full Auto</option>
            <option value="respect_locks">Respect Locks</option>
            <option value="fill_gaps">Fill Gaps</option>
            <option value="rebalance">Rebalance</option>
          </select>
        </div>

        <div className="flex items-end gap-2 lg:col-span-2">
          <button className="rounded-lg bg-sky-500 px-3 py-2 text-sm text-white" onClick={() => generateMutation.mutate({ mode: schedulerMode })} type="button">
            Generate
          </button>
          <button className="rounded-lg border border-slate-300 px-3 py-2 text-sm" onClick={() => setShowCategoryForm((v) => !v)} type="button">
            {showCategoryForm ? 'Hide Category' : 'New Category'}
          </button>
        </div>
      </div>

      {showCategoryForm ? (
        <div className="grid gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-800 md:grid-cols-10">
          <input
            placeholder="Category name"
            value={categoryForm.name}
            onChange={(event) => setCategoryForm((v) => ({ ...v, name: event.target.value }))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          />
          <input
            type="number"
            min={0}
            step={0.5}
            placeholder="Hours/week"
            value={categoryForm.weekly_target_hours}
            onChange={(event) => setCategoryForm((v) => ({ ...v, weekly_target_hours: Number(event.target.value) }))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          />
          <input
            type="number"
            min={15}
            step={15}
            placeholder="Block min"
            value={categoryForm.session_length_minutes}
            onChange={(event) => setCategoryForm((v) => ({ ...v, session_length_minutes: Number(event.target.value) }))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          />
          <input
            type="number"
            min={1}
            max={12}
            step={1}
            placeholder="Max blocks/day"
            value={categoryForm.max_blocks_per_day}
            onChange={(event) => setCategoryForm((v) => ({ ...v, max_blocks_per_day: event.target.value }))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          />
          <select
            value={categoryForm.priority}
            onChange={(event) => setCategoryForm((v) => ({ ...v, priority: Number(event.target.value) }))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          >
            <option value={1}>Priority 1</option>
            <option value={2}>Priority 2</option>
            <option value={3}>Priority 3</option>
            <option value={4}>Priority 4</option>
            <option value={5}>Priority 5</option>
          </select>
          <input
            type="time"
            value={categoryForm.preferred_start_time}
            onChange={(event) => setCategoryForm((v) => ({ ...v, preferred_start_time: event.target.value }))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            title="Preferred start time"
          />
          <input
            type="time"
            value={categoryForm.preferred_end_time}
            onChange={(event) => setCategoryForm((v) => ({ ...v, preferred_end_time: event.target.value }))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            title="Preferred end time"
          />
          <input
            type="color"
            value={categoryForm.color}
            onChange={(event) => setCategoryForm((v) => ({ ...v, color: event.target.value }))}
            className="h-10 rounded-lg border border-slate-300 bg-white px-1 py-1 dark:border-slate-700 dark:bg-slate-800"
          />
          <button className="rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white" type="button" onClick={createCategoryWithValidation}>
            Save Category
          </button>
        </div>
      ) : null}

      {preview ? (
        <div className="rounded-xl border border-sky-200 bg-sky-50 p-3 text-sm text-sky-800">
          <div className="mb-2 font-medium">Schedule Preview</div>
          <div className="mb-2 grid gap-2 md:grid-cols-3">
            <div>Total target: {preview.diagnostics.total_target_hours.toFixed(1)}h</div>
            <div>Total scheduled: {preview.diagnostics.total_scheduled_hours.toFixed(1)}h</div>
            <div>Avg flexible/day: {preview.diagnostics.average_daily_flexible_hours.toFixed(1)}h</div>
          </div>
          <div className="flex gap-2">
            <button className="rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white" onClick={() => applyMutation.mutate(preview.run_id)} type="button">
              Apply Preview
            </button>
            <button className="rounded-lg border border-slate-300 px-3 py-2 text-sm" onClick={() => setPreview(null)} type="button">
              Cancel Preview
            </button>
          </div>
        </div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
        <div className="overflow-hidden rounded-2xl border border-slate-200 p-2 dark:border-slate-800">
          <FullCalendar
            plugins={[timeGridPlugin, dayGridPlugin, listPlugin, interactionPlugin]}
            initialView="timeGridWeek"
            editable
            selectable
            nowIndicator
            height="auto"
            select={handleSelect}
            eventDrop={handleEventDrop}
            eventResize={handleEventResize}
            eventClick={handleEventClick}
            events={[...calendarEvents, ...previewEvents]}
            datesSet={(arg) => setWeekAnchor(startOfWeek(arg.start))}
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: 'timeGridDay,timeGridWeek,dayGridMonth,listWeek',
            }}
            firstDay={1}
            slotMinTime="05:00:00"
            slotMaxTime="23:30:00"
            slotDuration="00:15:00"
            snapDuration="00:15:00"
            slotLabelInterval="01:00:00"
            allDaySlot={false}
          />
        </div>

        <div className="space-y-3">
          <section className="rounded-2xl border border-slate-200 p-3 dark:border-slate-800">
            <h3 className="mb-2 font-medium">Category Editor</h3>
            <select
              value={selectedCategoryId ?? ''}
              onChange={(event) => setSelectedCategoryId(event.target.value ? Number(event.target.value) : null)}
              className="mb-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            >
              <option value="">Select category...</option>
              {(categories.data ?? []).map((category) => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </select>

            {selectedCategoryId ? (
              <div className="space-y-2 text-sm">
                {(() => {
                  const cat = selectedCategory
                  if (!cat) return null
                  return (
                    <>
                      <label className="block">
                        Name
                        <input
                          type="text"
                          defaultValue={cat.name}
                          onBlur={(event) => {
                            const nextName = event.target.value.trim()
                            if (!nextName) {
                              setErrorMessage('Category name is required.')
                              event.target.value = cat.name
                              return
                            }
                            saveSelectedCategoryPatch({ name: nextName })
                          }}
                          className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                        />
                      </label>
                      <label className="block">
                        Weekly hours
                        <input
                          type="number"
                          step={0.5}
                          defaultValue={cat.weekly_target_hours}
                          onBlur={(event) => saveSelectedCategoryPatch({ weekly_target_hours: Number(event.target.value) })}
                          className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                        />
                      </label>
                      <label className="block">
                        Priority
                        <select
                          defaultValue={cat.priority}
                          onChange={(event) => saveSelectedCategoryPatch({ priority: Number(event.target.value) })}
                          className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                        >
                          <option value={1}>Priority 1</option>
                          <option value={2}>Priority 2</option>
                          <option value={3}>Priority 3</option>
                          <option value={4}>Priority 4</option>
                          <option value={5}>Priority 5</option>
                        </select>
                      </label>
                      <label className="block">
                        Color
                        <input
                          type="color"
                          value={cat.color}
                          onChange={(event) => saveSelectedCategoryPatch({ color: event.target.value })}
                          className="mt-1 h-10 w-full rounded-lg border border-slate-300 bg-white px-1 py-1 dark:border-slate-700 dark:bg-slate-800"
                        />
                      </label>
                      <label className="block">
                        Exact block length (minutes)
                        <input
                          type="number"
                          min={15}
                          step={15}
                          defaultValue={cat.session_length_minutes}
                          onBlur={(event) => {
                            const val = Number(event.target.value)
                            saveSelectedCategoryPatch({ session_length_minutes: val, min_session_minutes: val, max_session_minutes: val })
                          }}
                          className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                        />
                      </label>
                      <label className="block">
                        Max blocks per day
                        <input
                          type="number"
                          min={1}
                          max={12}
                          step={1}
                          defaultValue={cat.max_blocks_per_day ?? ''}
                          onBlur={(event) => {
                            const raw = event.target.value.trim()
                            if (!raw) {
                              saveSelectedCategoryPatch({ max_blocks_per_day: null })
                              return
                            }
                            const val = Number(raw)
                            if (Number.isNaN(val) || val < 1 || val > 12) {
                              setErrorMessage('Max blocks per day must be between 1 and 12.')
                              event.target.value = cat.max_blocks_per_day ? String(cat.max_blocks_per_day) : ''
                              return
                            }
                            saveSelectedCategoryPatch({ max_blocks_per_day: val })
                          }}
                          className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                        />
                      </label>
                      <label className="block">
                        Preferred time range
                        <div className="mt-1 flex gap-2">
                          <input
                            type="time"
                            value={selectedPreferredStart}
                            onChange={(event) => setSelectedPreferredStart(event.target.value)}
                            className="w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                          />
                          <input
                            type="time"
                            value={selectedPreferredEnd}
                            onChange={(event) => setSelectedPreferredEnd(event.target.value)}
                            className="w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                          />
                          <button
                            type="button"
                            onClick={saveSelectedCategoryPreferredTimeRange}
                            className="rounded-lg border border-slate-300 px-2 py-1 text-xs"
                          >
                            Save
                          </button>
                        </div>
                      </label>
                      <button
                        type="button"
                        onClick={deleteSelectedCategory}
                        className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700"
                      >
                        Delete Category
                      </button>
                    </>
                  )
                })()}
              </div>
            ) : (
              <p className="text-xs text-slate-500">Select a category to edit target hours, block length, and preferred time frame.</p>
            )}
          </section>

          <section className="rounded-2xl border border-slate-200 p-3 dark:border-slate-800">
            <h3 className="mb-2 font-medium">Event Quick Edit</h3>
            {!selectedEvent ? (
              <p className="text-xs text-slate-500">Click an event block to edit type, lock, duplicate, or delete.</p>
            ) : (
              <div className="space-y-2 text-sm">
                <div className="font-medium">{selectedEvent.title}</div>
                <label className="block">
                  Type
                  <select
                    value={selectedEvent.event_type}
                    onChange={(event) => updateSelectedEvent({ event_type: event.target.value as EventType })}
                    className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                  >
                    <option value="flexible">Flexible</option>
                    <option value="fixed">Fixed</option>
                  </select>
                </label>
                <label className="block">
                  Lock mode
                  <select
                    value={selectedEvent.lock_mode}
                    onChange={(event) => updateSelectedEvent({ lock_mode: event.target.value as LockMode })}
                    className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                  >
                    {lockOrder.map((mode) => (
                      <option key={mode} value={mode}>{mode}</option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  Category
                  <select
                    value={selectedEvent.category_id ?? ''}
                    onChange={(event) => updateSelectedEvent({ category_id: event.target.value ? Number(event.target.value) : null })}
                    className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 dark:border-slate-700 dark:bg-slate-800"
                  >
                    <option value="">Uncategorized</option>
                    {(categories.data ?? []).map((category) => (
                      <option key={category.id} value={category.id}>{category.name}</option>
                    ))}
                  </select>
                </label>
                <div className="flex gap-2">
                  <button
                    className="rounded-lg border border-slate-300 px-2 py-1 text-xs"
                    type="button"
                    onClick={() => duplicateMutation.mutate({ id: selectedEvent.id, dayOffset: 1 })}
                  >
                    Duplicate +1 day
                  </button>
                  <button
                    className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700"
                    type="button"
                    onClick={() => {
                      deleteEventMutation.mutate(selectedEvent.id)
                      setSelectedEventId(null)
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}


