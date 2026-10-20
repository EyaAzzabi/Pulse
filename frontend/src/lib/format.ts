export function formatMoney(value: string | number, currency = 'EUR'): string {
  const num = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(num)) return `${currency} 0.00`
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)
}

export function formatDate(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export function riskColor(level: string): string {
  if (level === 'high') return 'text-risk'
  if (level === 'medium') return 'text-amber'
  return 'text-success'
}
