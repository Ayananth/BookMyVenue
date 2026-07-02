import { motion } from "framer-motion"
import { CalendarDays, Clock, DollarSign, Tag } from "lucide-react"
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
  return (
    schedule.name ||
    `${formatTimeLabel(schedule.startTime)} - ${formatTimeLabel(schedule.endTime)}`
  )
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

export default function BookingConfirmationContent({
  venue,
  selectedSchedule,
  bookingDate,
  onCancel,
  onConfirm,
}) {
  if (!venue || !selectedSchedule) return null

  const formattedPrice = formatVenuePrice(selectedSchedule.price) ?? "—"

  return (
    <div className="flex min-h-[420px] flex-col">
      <div className="mb-6 pr-8">
        <p className="text-sm font-semibold text-primary">Booking confirmation</p>
        <h3 className="mt-1 font-serif text-2xl font-bold">Review your booking</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Check the details below before proceeding to payment.
        </p>
      </div>

      <div className="grid flex-1 gap-3 sm:grid-cols-2">
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
            <p className="font-serif text-2xl font-bold text-primary">{formattedPrice}</p>
          </div>
        </div>
      </div>

      <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 rounded-lg border border-border px-5 py-3 font-semibold text-foreground transition hover:bg-muted"
        >
          Back
        </button>
        <motion.button
          type="button"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onConfirm}
          className="flex-1 rounded-lg bg-primary px-5 py-3 font-semibold text-primary-foreground transition hover:opacity-90"
        >
          Proceed to Payment
        </motion.button>
      </div>
    </div>
  )
}
