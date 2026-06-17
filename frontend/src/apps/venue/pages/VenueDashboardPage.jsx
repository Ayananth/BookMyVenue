import { Link } from "react-router-dom"

function Stat({ label, value }) {
  return (
    <div className="rounded-2xl border border-border/60 bg-card p-5">
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  )
}

export default function VenueDashboardPage() {
  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Welcome back</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            This is a starter venue dashboard page. Hook it to your real venue APIs next.
          </p>
        </div>
        <div className="flex gap-2">
          <Link className="rounded-xl bg-muted px-4 py-2 text-sm font-medium hover:opacity-90" to="bookings">
            View bookings
          </Link>
          <button className="rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90">
            Add listing
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <Stat label="Upcoming bookings" value="12" />
        <Stat label="Pending requests" value="3" />
        <Stat label="Revenue (30d)" value="₹84,500" />
      </div>

      <section className="mt-6 rounded-2xl border border-border/60 bg-card p-5">
        <h2 className="text-base font-semibold">Quick actions</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <button className="rounded-xl bg-muted px-4 py-3 text-left hover:opacity-90">
            <div className="text-sm font-medium">Update availability</div>
            <div className="mt-1 text-xs text-muted-foreground">Block dates &amp; set pricing</div>
          </button>
          <button className="rounded-xl bg-muted px-4 py-3 text-left hover:opacity-90">
            <div className="text-sm font-medium">Manage photos</div>
            <div className="mt-1 text-xs text-muted-foreground">Upload or reorder gallery</div>
          </button>
          <button className="rounded-xl bg-muted px-4 py-3 text-left hover:opacity-90">
            <div className="text-sm font-medium">View messages</div>
            <div className="mt-1 text-xs text-muted-foreground">Reply to customer queries</div>
          </button>
        </div>
      </section>
    </div>
  )
}

