import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { applyTemplate, createTemplate, createTemplateFromWeek, deleteTemplate, getTemplates } from '../api/lifeplanner'

export function TemplatesPage() {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')

  const templates = useQuery({ queryKey: ['templates'], queryFn: () => getTemplates() })

  const createMutation = useMutation({
    mutationFn: createTemplate,
    onSuccess: () => {
      setName('')
      queryClient.invalidateQueries({ queryKey: ['templates'] })
    },
  })

  const createFromWeekMutation = useMutation({
    mutationFn: ({ templateName }: { templateName: string }) => createTemplateFromWeek(templateName, new Date()),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['templates'] }),
  })

  const applyMutation = useMutation({
    mutationFn: (id: number) => applyTemplate(id, new Date()),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteTemplate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['templates'] }),
  })

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Templates</h2>
        <p className="text-sm text-slate-500">Save and re-apply weekly schedule structures.</p>
      </div>

      <div className="flex gap-2">
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Template name"
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
        />
        <button
          className="rounded-lg bg-sky-500 px-3 py-2 text-sm text-white"
          type="button"
          onClick={() => name.trim() && createMutation.mutate({ name: name.trim(), template_data: { events: [] } })}
        >
          Create
        </button>
        <button
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          type="button"
          onClick={() => name.trim() && createFromWeekMutation.mutate({ templateName: name.trim() })}
        >
          Save Current Week
        </button>
      </div>

      <div className="space-y-2">
        {(templates.data ?? []).map((template) => (
          <div key={template.id} className="flex items-center justify-between rounded-xl border border-slate-200 p-3 dark:border-slate-800">
            <div>
              <div className="font-medium">{template.name}</div>
              <div className="text-xs text-slate-500">{template.description ?? 'No description'}</div>
            </div>
            <div className="flex gap-2">
              <button className="rounded-lg border border-slate-300 px-2 py-1 text-xs" type="button" onClick={() => applyMutation.mutate(template.id)}>
                Apply
              </button>
              <button className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700" type="button" onClick={() => deleteMutation.mutate(template.id)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

