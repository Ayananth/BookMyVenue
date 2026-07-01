import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { fetchBookings } from "../../../apis/bookings"

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value)
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value))
}

function formatTimeRange(startTime, endTime) {
  if (!startTime || !endTime) return "—"

  const formatTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(":").map(Number)
    const period = hours >= 12 ? "PM" : "AM"
    const hour = hours % 12 || 12
    return `${hour}:${String(minutes).padStart(2, "0")} ${period}`
  }

  return `${formatTime(startTime)} - ${formatTime(endTime)}`
}

function statusLabel(status) {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

export default function VenueBookingsPage() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    let active = true

    fetchBookings()
      .then((data) => {
        if (active) setBookings(data)
      })
      .catch((fetchError) => {
        console.error("Failed to load venue bookings:", fetchError)
        if (active) setError("Could not load bookings.")
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const sortedBookings = useMemo(
    () =>
      [...bookings].sort(
        (a, b) => new Date(b.eventDate) - new Date(a.eventDate),
      ),
    [bookings],
  )

  return (
    <div>
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Bookings</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Reservations made for your venues.
          </p>
        </div>
        <Link
          className="rounded-xl bg-muted px-4 py-2 text-sm font-medium hover:opacity-90"
          to=".."
        >
          Back to dashboard
        </Link>
      </div>

      {loading && (
        <div className="mt-6 rounded-2xl border border-border/60 bg-card p-8 text-center text-sm text-muted-foreground">
          Loading bookings...
        </div>
      )}

      {!loading && error && (
        <div className="mt-6 rounded-2xl border border-destructive/30 bg-destructive/5 p-8 text-center text-sm text-destructive">
          {error}
        </div>
      )}

      {!loading && !error && sortedBookings.length === 0 && (
        <div className="mt-6 rounded-2xl border border-border/60 bg-card p-8 text-center text-sm text-muted-foreground">
          No bookings yet.
        </div>
      )}

      {!loading && !error && sortedBookings.length > 0 && (
        <div className="mt-6 space-y-3">
          {sortedBookings.map((booking) => (
            <div
              key={booking.id}
              className="rounded-2xl border border-border/60 bg-card p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-sm font-medium">
                    {booking.venueName} • {formatDate(booking.eventDate)}
                  </div>
                  <div className="mt-1 text-sm text-muted-foreground">
                    {formatTimeRange(booking.startTime, booking.endTime)}
                  </div>
                </div>
                <div className="text-xs font-semibold capitalize text-muted-foreground">
                  {statusLabel(booking.status)}
                </div>
              </div>
              <div className="mt-2 text-sm text-muted-foreground">
                Booking #{booking.id} • Amount: {formatCurrency(booking.amount)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
