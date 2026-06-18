import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { createTask, deleteTask, getTasks, updateTask } from '../api/lifeplanner'

export function TasksPage() {
  const queryClient = useQueryClient()
  const [title, setTitle] = useState('')

  const tasks = useQuery({ queryKey: ['tasks'], queryFn: () => getTasks() })

  const createMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      setTitle('')
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Record<string, unknown> }) => updateTask(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  })

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Tasks</h2>
        <p className="text-sm text-slate-500">Track to-dos with priority, status, and duration estimates.</p>
      </div>

      <div className="flex gap-2">
        <input
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          placeholder="New task title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <button
          type="button"
          className="rounded-lg bg-sky-500 px-3 py-2 text-sm text-white"
          onClick={() => title.trim() && createMutation.mutate({ title: title.trim(), status: 'todo', priority: 3 })}
        >
          Add Task
        </button>
      </div>

      <div className="space-y-2">
        {(tasks.data ?? []).map((task) => (
          <div key={task.id} className="flex items-center gap-2 rounded-xl border border-slate-200 p-3 dark:border-slate-800">
            <select
              value={task.status}
              onChange={(event) => updateMutation.mutate({ id: task.id, payload: { status: event.target.value } })}
              className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-800"
            >
              <option value="todo">todo</option>
              <option value="in_progress">in progress</option>
              <option value="done">done</option>
            </select>

            <div className="flex-1">
              <div className="font-medium">{task.title}</div>
              <div className="text-xs text-slate-500">Priority {task.priority} {task.estimated_minutes ? `• ${task.estimated_minutes} min` : ''}</div>
            </div>

            <button
              type="button"
              className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700"
              onClick={() => deleteMutation.mutate(task.id)}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

