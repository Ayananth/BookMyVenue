import { useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { CalendarDays, Clock, DollarSign, Tag, X } from "lucide-react"
import { formatVenuePrice } from "../../apis/venues"

function formatBookingDate(dateValue) {
  if (!dateValue) return "—"

  const [year, month, day] = dateValue.split("-").map(Number)
  const date = new Date(year, month - 1, day)

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date)
}

function formatTimeLabel(timeStr) {
  if (!timeStr) return "—"

  const [hours, minutes] = timeStr.split(":").map(Number)
  const period = hours >= 12 ? "PM" : "AM"
  const hour = hours % 12 || 12

  return `${hour}:${String(minutes).padStart(2, "0")} ${period}`
}

function getScheduleName(schedule) {
  if (!schedule) return "—"
  return schedule.name || `${formatTimeLabel(schedule.startTime)} - ${formatTimeLabel(schedule.endTime)}`
}

function DetailRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-border bg-background/60 px-4 py-3">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <Icon size={16} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        <p className="mt-0.5 text-sm font-semibold text-foreground sm:text-base">
          {value}
        </p>
      </div>
    </div>
  )
}

export default function BookingConfirmationDialog({
  venue,
  selectedSchedule,
  bookingDate,
  onCancel,
  onConfirm,
}) {
  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === "Escape") onCancel()
    }

    document.body.style.overflow = "hidden"
    window.addEventListener("keydown", onKeyDown)

    return () => {
      document.body.style.overflow = ""
      window.removeEventListener("keydown", onKeyDown)
    }
  }, [onCancel])

  if (!venue || !selectedSchedule) return null

  const formattedPrice = formatVenuePrice(selectedSchedule.price) ?? "—"

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6">
        <motion.button
          type="button"
          aria-label="Close booking confirmation"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 bg-foreground/45 backdrop-blur-sm"
          onClick={onCancel}
        />

        <motion.div
          role="dialog"
          aria-modal="true"
          aria-labelledby="booking-confirmation-title"
          initial={{ opacity: 0, scale: 0.96, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 16 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
          className="relative flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-[0_24px_60px_rgba(27,36,29,0.2)] sm:max-w-2xl"
        >
          <button
            type="button"
            onClick={onCancel}
            className="absolute right-3 top-3 z-10 flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-background/90 text-muted-foreground shadow-sm transition-colors hover:bg-background hover:text-foreground sm:right-4 sm:top-4"
            aria-label="Close"
          >
            <X size={18} />
          </button>

          <div className="overflow-y-auto">
            <div className="relative h-40 w-full shrink-0 sm:h-48">
              <img
                src={venue.image || "/placeholder.svg"}
                alt={venue.name}
                className="h-full w-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-foreground/80 via-foreground/25 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-5 sm:p-6">
                <p className="text-xs font-semibold uppercase tracking-wider text-primary-foreground/80">
                  Booking confirmation
                </p>
                <h2
                  id="booking-confirmation-title"
                  className="mt-1 font-serif text-2xl font-bold text-primary-foreground sm:text-3xl"
                >
                  {venue.name}
                </h2>
              </div>
            </div>

            <div className="p-5 sm:p-6">
              <p className="text-sm text-muted-foreground">
                Review your booking details before proceeding to payment.
              </p>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <DetailRow
                  icon={CalendarDays}
                  label="Booking date"
                  value={formatBookingDate(bookingDate)}
                />
                <DetailRow
                  icon={Tag}
                  label="Schedule"
                  value={getScheduleName(selectedSchedule)}
                />
                <DetailRow
                  icon={Clock}
                  label="Start time"
                  value={formatTimeLabel(selectedSchedule.startTime)}
                />
                <DetailRow
                  icon={Clock}
                  label="End time"
                  value={formatTimeLabel(selectedSchedule.endTime)}
                />
              </div>

              <div className="mt-4 flex items-center justify-between rounded-xl border border-primary/20 bg-primary/5 px-4 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <DollarSign size={18} />
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Total price
                    </p>
                    <p className="font-serif text-2xl font-bold text-primary">
                      {formattedPrice}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row">
                <button
                  type="button"
                  onClick={onCancel}
                  className="flex-1 rounded-lg border border-border px-5 py-3 text-sm font-semibold text-foreground transition hover:bg-muted sm:text-base"
                >
                  Cancel
                </button>
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={onConfirm}
                  className="flex-1 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition hover:opacity-90 sm:text-base"
                >
                  Proceed to Payment
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
