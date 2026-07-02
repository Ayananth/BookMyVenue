import api from "../lib/axios"

const apiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
}

export function parsePaymentError(error) {
  const data = error.response?.data
  if (!data) return "Payment verification failed."
  if (typeof data.message === "string") return data.message
  if (typeof data.detail === "string") return data.detail
  if (typeof data === "object") {
    const firstKey = Object.keys(data)[0]
    const value = data[firstKey]
    if (Array.isArray(value)) return value[0]
    if (typeof value === "string") return value
  }
  return "Payment verification failed."
}

export async function verifyPayment({
  bookingSessionId,
  razorpayOrderId,
  razorpayPaymentId,
  razorpaySignature,
}) {
  const { data } = await api.post(
    "/payments/verify/",
    {
      booking_session_id: bookingSessionId,
      razorpay_order_id: razorpayOrderId,
      razorpay_payment_id: razorpayPaymentId,
      razorpay_signature: razorpaySignature,
    },
    apiConfig,
  )
  return data
}
