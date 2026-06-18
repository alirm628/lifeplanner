import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLogin } from '../hooks/useAuth'

export function LoginPage() {
  const [email, setEmail] = useState('admin@local.dev')
  const [password, setPassword] = useState('admin1234')
  const navigate = useNavigate()
  const login = useLogin()

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    try {
      await login.mutateAsync({ email, password })
      navigate('/')
    } catch {
      // handled with inline message
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4 dark:bg-slate-950">
      <form className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 shadow-soft dark:border-slate-800 dark:bg-slate-900" onSubmit={onSubmit}>
        <h1 className="mb-1 text-2xl font-semibold tracking-tight">LifePlanner</h1>
        <p className="mb-6 text-sm text-slate-500">Sign in to manage your week.</p>

        <div className="mb-4 space-y-1">
          <label className="text-sm" htmlFor="email">Email</label>
          <input
            id="email"
            className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-sky-500 focus:ring dark:border-slate-700 dark:bg-slate-800"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="mb-4 space-y-1">
          <label className="text-sm" htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-sky-500 focus:ring dark:border-slate-700 dark:bg-slate-800"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {login.isError ? <p className="mb-4 text-sm text-rose-500">Invalid credentials.</p> : null}

        <button
          type="submit"
          className="w-full rounded-xl bg-sky-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-600 disabled:opacity-60"
          disabled={login.isPending}
        >
          {login.isPending ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}

