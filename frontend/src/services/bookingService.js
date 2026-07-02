import {
  getStartBookingErrorMessage,
  startBooking as startBookingFromApi,
} from "../apis/bookings"

export function bookingStartFromApi(data) {
  return {
    bookingSession: {
      id: data.booking_session_id,
      expiresAt: data.expires_at ?? null,
    },
    payment: {
      id: data.payment_id ?? null,
    },
    order: {
      id: data.razorpay_order_id,
    },
    amount: data.amount ?? data.amount_paise,
    currency: data.currency,
    key: data.key,
  }
}

export async function startBooking({ venueScheduleId, bookingDate }) {
  const data = await startBookingFromApi({ venueScheduleId, bookingDate })
  return bookingStartFromApi(data)
}

export { getStartBookingErrorMessage }
