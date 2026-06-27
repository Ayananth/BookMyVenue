export const WEEKDAYS = [
  { value: 0, label: "Monday", short: "Mon" },
  { value: 1, label: "Tuesday", short: "Tue" },
  { value: 2, label: "Wednesday", short: "Wed" },
  { value: 3, label: "Thursday", short: "Thu" },
  { value: 4, label: "Friday", short: "Fri" },
  { value: 5, label: "Saturday", short: "Sat" },
  { value: 6, label: "Sunday", short: "Sun" },
]

let nextId = 1

export function createClientId(prefix = "id") {
  nextId += 1
  return `${prefix}-${nextId}-${Date.now()}`
}

function parseTimeToMinutes(timeStr) {
  const [hours, minutes] = timeStr.split(":").map(Number)
  return hours * 60 + minutes
}

function minutesToTimeString(totalMinutes) {
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`
}

export function formatCompactSlotRange(startTime, endTime) {
  return `${startTime.slice(0, 2)}-${endTime.slice(0, 2)}`
}

export function formatSlotName(startTime, endTime) {
  return `${startTime.slice(0, 5)} - ${endTime.slice(0, 5)}`
}

export function formatIndianPrice(amount) {
  const numeric = Number(amount)
  if (Number.isNaN(numeric)) return "—"
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(numeric)
}

export function formatDaySelection(days) {
  if (!days.length) return "No days selected"
  const sorted = [...days].sort((a, b) => a - b)
  const labels = sorted.map((day) => WEEKDAYS.find((item) => item.value === day)?.short ?? day)

  if (sorted.length === 7) return "Every day"
  if (
    sorted.length === 5 &&
    sorted.every((day, index) => day === index)
  ) {
    return "Mon – Fri"
  }
  if (sorted.length === 2 && sorted[0] === 5 && sorted[1] === 6) {
    return "Sat – Sun"
  }

  return labels.join(", ")
}

export function generateHourlySlots({
  openTime,
  closeTime,
  durationMinutes,
  defaultPrice,
}) {
  const openMinutes = parseTimeToMinutes(openTime)
  const closeMinutes = parseTimeToMinutes(closeTime)
  const duration = Number(durationMinutes)
  const price = Number(defaultPrice)

  if (closeMinutes <= openMinutes) {
    throw new Error("Close time must be after open time.")
  }
  if (!duration || duration <= 0) {
    throw new Error("Duration must be greater than zero.")
  }
  if (Number.isNaN(price) || price < 0) {
    throw new Error("Default price must be zero or greater.")
  }

  const slots = []
  let cursor = openMinutes

  while (cursor + duration <= closeMinutes) {
    const startTime = minutesToTimeString(cursor)
    const endTime = minutesToTimeString(cursor + duration)

    slots.push({
      id: createClientId("slot"),
      name: formatSlotName(startTime, endTime),
      start_time: startTime,
      end_time: endTime,
      price,
      is_available: true,
    })

    cursor += duration
  }

  if (slots.length === 0) {
    throw new Error("No slots fit within the selected time range.")
  }

  return slots
}

export function buildScheduleGroupPayload(group) {
  return {
    name: group.name.trim(),
    days: [...group.days].sort((a, b) => a - b),
    schedules: group.slots.map((slot) => ({
      name: slot.name,
      start_time: `${slot.start_time}:00`,
      end_time: `${slot.end_time}:00`,
      price: Number(slot.price),
      is_available: slot.is_available,
    })),
  }
}
