import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { createGoal, deleteGoal, getGoalProgress, getGoals, updateGoal } from '../api/lifeplanner'

export function GoalsPage() {
  const queryClient = useQueryClient()
  const [title, setTitle] = useState('')

  const goals = useQuery({ queryKey: ['goals'], queryFn: () => getGoals() })
  const progress = useQuery({ queryKey: ['goal-progress'], queryFn: getGoalProgress })

  const createMutation = useMutation({
    mutationFn: createGoal,
    onSuccess: () => {
      setTitle('')
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      queryClient.invalidateQueries({ queryKey: ['goal-progress'] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Record<string, unknown> }) => updateGoal(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      queryClient.invalidateQueries({ queryKey: ['goal-progress'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      queryClient.invalidateQueries({ queryKey: ['goal-progress'] })
    },
  })

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Goals</h2>
        <p className="text-sm text-slate-500">Track weekly hour/session objectives and completion progress.</p>
      </div>

      <div className="flex gap-2">
        <input
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
          placeholder="New goal title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <button
          type="button"
          className="rounded-lg bg-sky-500 px-3 py-2 text-sm text-white"
          onClick={() => title.trim() && createMutation.mutate({ title: title.trim(), status: 'active', target_hours: 5 })}
        >
          Add Goal
        </button>
      </div>

      <div className="space-y-2">
        {(goals.data ?? []).map((goal) => {
          const goalProgress = progress.data?.find((item) => item.goal_id === goal.id)
          return (
            <div key={goal.id} className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
              <div className="mb-2 flex items-center justify-between">
                <div>
                  <div className="font-medium">{goal.title}</div>
                  <div className="text-xs text-slate-500">Target: {goal.target_hours ?? 0}h • {goal.target_sessions ?? 0} sessions</div>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={goal.status}
                    onChange={(event) => updateMutation.mutate({ id: goal.id, payload: { status: event.target.value } })}
                    className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-800"
                  >
                    <option value="active">active</option>
                    <option value="completed">completed</option>
                  </select>
                  <button type="button" className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700" onClick={() => deleteMutation.mutate(goal.id)}>
                    Delete
                  </button>
                </div>
              </div>
              <div className="text-xs text-slate-600 dark:text-slate-300">
                Progress: {goalProgress?.progress_hours ?? 0}h • {goalProgress?.progress_sessions ?? 0} sessions
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

