import { Link } from "react-router-dom"

export default function VenueBookingsPage() {
  return (
    <div>
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Bookings</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sample nested route at <code className="font-mono">/venue/bookings</code>.
          </p>
        </div>
        <Link
          className="rounded-xl bg-muted px-4 py-2 text-sm font-medium hover:opacity-90"
          to=".."
        >
          Back to dashboard
        </Link>
      </div>

      <div className="mt-6 space-y-3">
        <div className="rounded-2xl border border-border/60 bg-card p-5">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium">Wedding • June 28</div>
            <div className="text-xs text-muted-foreground">Confirmed</div>
          </div>
          <div className="mt-2 text-sm text-muted-foreground">Guests: 240 • Amount: ₹52,000</div>
        </div>
        <div className="rounded-2xl border border-border/60 bg-card p-5">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium">Conference • July 05</div>
            <div className="text-xs text-muted-foreground">Pending</div>
          </div>
          <div className="mt-2 text-sm text-muted-foreground">Guests: 90 • Amount: ₹18,000</div>
        </div>
      </div>
    </div>
  )
}

