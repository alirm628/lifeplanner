interface PlaceholderPageProps {
  title: string
  description: string
}

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center dark:border-slate-700">
      <h2 className="mb-2 text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="mx-auto max-w-xl text-sm text-slate-500">{description}</p>
    </div>
  )
}

