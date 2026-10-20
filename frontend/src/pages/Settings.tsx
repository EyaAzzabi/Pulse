import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'

export function Settings() {
  const { me, currentOrg, setCurrentOrgId } = useAuth()

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-8">
      <h1 className="text-2xl font-semibold text-ink">Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <Row label="Name" value={me?.user.full_name ?? ''} />
          <Row label="Email" value={me?.user.email ?? ''} />
          <Row label="Default currency" value={me?.user.default_currency ?? ''} />
          <Row label="Timezone" value={me?.user.timezone ?? ''} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Organizations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {me?.memberships.map((m) => (
            <button
              key={m.organization_id}
              onClick={() => setCurrentOrgId(m.organization_id)}
              className={`flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-sm ${
                currentOrg?.organization_id === m.organization_id
                  ? 'border-brand/40 bg-brand/5 text-ink'
                  : 'border-slate-200 text-slate hover:text-ink'
              }`}
            >
              <span>{m.organization_name}</span>
              <span className="text-xs text-slate">{m.role}</span>
            </button>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-slate-100 py-1.5">
      <span className="text-slate">{label}</span>
      <span className="text-ink">{value}</span>
    </div>
  )
}
