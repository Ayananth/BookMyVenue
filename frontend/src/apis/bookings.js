import api from "../lib/axios"

const apiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
}

export function parseBookingError(error) {
  const data = error.response?.data
  if (!data) return "Something went wrong. Please try again."
  if (typeof data.detail === "string") return data.detail
  if (typeof data === "object") {
    const firstKey = Object.keys(data)[0]
    const value = data[firstKey]
    if (Array.isArray(value)) return value[0]
    if (typeof value === "string") return value
  }
  return "Something went wrong. Please try again."
}

export function bookingFromApi(entry) {
  return {
    id: entry.id,
    venueName: entry.venue_name,
    venueSlug: entry.venue_slug,
    bookingDate: entry.created_at?.slice(0, 10) ?? entry.created_at,
    eventDate: entry.booking_date,
    amount: Number(entry.price),
    status: entry.status,
    startTime: entry.start_time?.slice(0, 5) ?? entry.start_time,
    endTime: entry.end_time?.slice(0, 5) ?? entry.end_time,
  }
}

export async function fetchBookings(params = {}) {
  const { data } = await api.get("/bookings/", {
    ...apiConfig,
    params: { limit: 100, ...params },
  })
  const results = data.results ?? data
  return (Array.isArray(results) ? results : []).map(bookingFromApi)
}

export async function createBookings({ venueSlug, bookingDate, scheduleIds }) {
  const { data } = await api.post(
    "/bookings/",
    {
      venue_slug: venueSlug,
      booking_date: bookingDate,
      schedule_ids: scheduleIds,
    },
    apiConfig,
  )
  return (Array.isArray(data) ? data : []).map(bookingFromApi)
}

export async function cancelBooking(bookingId) {
  const { data } = await api.patch(
    `/bookings/${bookingId}/`,
    { status: "cancelled" },
    apiConfig,
  )
  return bookingFromApi(data)
}
