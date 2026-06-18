import { useQuery } from '@tanstack/react-query'
import { Calendar, Gauge, Goal, LayoutTemplate, ListChecks, Menu, Search, Settings, Target, X } from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

import { searchAll } from '../api/lifeplanner'
import { logout } from '../hooks/useAuth'
import { ThemeToggle } from './ThemeToggle'

const navItems = [
  { to: '/', label: 'Dashboard', icon: Gauge },
  { to: '/calendar', label: 'Calendar', icon: Calendar },
  { to: '/tasks', label: 'Tasks', icon: ListChecks },
  { to: '/goals', label: 'Goals', icon: Goal },
  { to: '/analytics', label: 'Analytics', icon: Target },
  { to: '/templates', label: 'Templates', icon: LayoutTemplate },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function AppShell() {
  const [searchQuery, setSearchQuery] = useState('')
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const searchResults = useQuery({
    queryKey: ['global-search', searchQuery],
    queryFn: () => searchAll(searchQuery),
    enabled: searchQuery.trim().length > 1,
  })

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto flex max-w-[1600px] gap-4 px-3 py-3 md:px-6">
        <aside className="sticky top-3 hidden h-[calc(100vh-1.5rem)] w-72 shrink-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900 md:block">
          <div className="mb-4 flex items-center justify-between">
            <h1 className="text-xl font-semibold tracking-tight">LifePlanner</h1>
            <ThemeToggle />
          </div>

          <div className="relative mb-4">
            <Search className="pointer-events-none absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
            <input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search tasks, events, goals..."
              className="w-full rounded-xl border border-slate-300 bg-white py-2 pl-8 pr-3 text-sm dark:border-slate-700 dark:bg-slate-800"
            />
            {searchQuery.trim().length > 1 ? (
              <div className="mt-2 max-h-48 overflow-auto rounded-xl border border-slate-200 bg-white p-2 text-xs shadow dark:border-slate-700 dark:bg-slate-900">
                {(searchResults.data ?? []).slice(0, 8).map((item) => (
                  <div key={`${item.type}-${item.id}`} className="rounded-md px-2 py-1 hover:bg-slate-100 dark:hover:bg-slate-800">
                    <div className="font-medium">{item.title}</div>
                    <div className="text-slate-500">{item.type}{item.subtitle ? ` • ${item.subtitle}` : ''}</div>
                  </div>
                ))}
                {searchResults.data?.length === 0 ? <div className="px-2 py-1 text-slate-500">No matches</div> : null}
              </div>
            ) : null}
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition ${
                      isActive
                        ? 'bg-sky-500 text-white shadow'
                        : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </NavLink>
              )
            })}
          </nav>
          <button
            className="mt-6 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            type="button"
            onClick={() => {
              logout()
              window.location.href = '/login'
            }}
          >
            Logout
          </button>
        </aside>

        <main className="min-w-0 flex-1 rounded-2xl border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900 md:p-6">
          <div className="mb-4 flex items-center justify-between md:hidden">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setMobileNavOpen(true)}
                className="rounded-xl border border-slate-300 p-2 text-slate-700 dark:border-slate-700 dark:text-slate-200"
                aria-label="Open navigation menu"
              >
                <Menu className="h-5 w-5" />
              </button>
              <h1 className="text-xl font-semibold tracking-tight">LifePlanner</h1>
            </div>
            <ThemeToggle />
          </div>
          <Outlet />
        </main>
      </div>

      {mobileNavOpen ? (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-slate-950/50"
            aria-label="Close navigation menu"
            onClick={() => setMobileNavOpen(false)}
          />
          <div className="absolute left-0 top-0 h-full w-[88vw] max-w-sm overflow-y-auto border-r border-slate-200 bg-white p-4 shadow-2xl dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold tracking-tight">LifePlanner</h2>
              <button
                type="button"
                onClick={() => setMobileNavOpen(false)}
                className="rounded-xl border border-slate-300 p-2 text-slate-700 dark:border-slate-700 dark:text-slate-200"
                aria-label="Close navigation menu"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="relative mb-4">
              <Search className="pointer-events-none absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
              <input
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search tasks, events, goals..."
                className="w-full rounded-xl border border-slate-300 bg-white py-2 pl-8 pr-3 text-sm dark:border-slate-700 dark:bg-slate-800"
              />
              {searchQuery.trim().length > 1 ? (
                <div className="mt-2 max-h-48 overflow-auto rounded-xl border border-slate-200 bg-white p-2 text-xs shadow dark:border-slate-700 dark:bg-slate-900">
                  {(searchResults.data ?? []).slice(0, 8).map((item) => (
                    <div key={`${item.type}-${item.id}`} className="rounded-md px-2 py-1 hover:bg-slate-100 dark:hover:bg-slate-800">
                      <div className="font-medium">{item.title}</div>
                      <div className="text-slate-500">{item.type}{item.subtitle ? ` • ${item.subtitle}` : ''}</div>
                    </div>
                  ))}
                  {searchResults.data?.length === 0 ? <div className="px-2 py-1 text-slate-500">No matches</div> : null}
                </div>
              ) : null}
            </div>

            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={() => setMobileNavOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${
                        isActive
                          ? 'bg-sky-500 text-white shadow'
                          : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                      }`
                    }
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </NavLink>
                )
              })}
            </nav>

            <button
              className="mt-6 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              type="button"
              onClick={() => {
                setMobileNavOpen(false)
                logout()
                window.location.href = '/login'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      ) : null}
    </div>
  )
}

