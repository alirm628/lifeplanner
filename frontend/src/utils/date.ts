export function startOfWeek(input: Date): Date {
  const d = new Date(input)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  const out = new Date(d)
  out.setDate(diff)
  out.setHours(0, 0, 0, 0)
  return out
}

export function addDays(input: Date, days: number): Date {
  const d = new Date(input)
  d.setDate(d.getDate() + days)
  return d
}

export function formatHours(value: number): string {
  return `${value.toFixed(1)}h`
}

export function toIsoLocal(date: Date): string {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}

export function toLocalDateTimeString(date: Date): string {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 19)
}

