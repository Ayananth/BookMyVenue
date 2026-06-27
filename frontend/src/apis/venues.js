import { venues } from "../data/venues"
import api from "../lib/axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

const apiConfig = { baseURL: API_BASE_URL }

export function parseVenueError(error) {
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

export async function fetchMyVenues() {
  const { data } = await api.get("/venues/", {
    ...apiConfig,
    params: { mine: true },
  })
  return data.results ?? data
}

export async function fetchVenueFormCategories() {
  const { data } = await api.get("/venues/categories", apiConfig)
  return data
}

export async function fetchVenueFormLocations() {
  const { data } = await api.get("/venues/locations", apiConfig)
  return data
}

export async function createVenue(payload) {
  const { data } = await api.post("/venues/add", payload, apiConfig)
  return data
}

export async function uploadVenueImage(file) {
  const formData = new FormData()
  formData.append("file", file)
  const { data } = await api.post("/uploads/image", formData, {
    ...apiConfig,
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}

export const VENUE_BOOKING_TYPES = [
  { value: "hourly", label: "Hourly" },
  { value: "session", label: "Session" },
  { value: "full_day", label: "Full Day" },
]

export function buildVenuePayload(formData, amenities, images) {
  return {
    name: formData.name.trim(),
    category_id: Number(formData.category),
    location_id: Number(formData.location),
    address: formData.address.trim(),
    description: formData.description.trim(),
    capacity: Number(formData.capacity),
    booking_type: formData.bookingType,
    contact_name: formData.contactName.trim(),
    contact_phone: formData.contactPhone.trim(),
    contact_email: formData.contactEmail.trim(),
    amenities,
    images: images.map(({ image_url, is_cover, sort_order }) => ({
      image_url,
      is_cover,
      sort_order,
    })),
  }
}

export function formatVenuePrice(price) {
  if (price == null || price === "") {
    return null
  }

  const numeric =
    typeof price === "number"
      ? price
      : Number(String(price).replace(/[^0-9.]/g, ""))

  if (Number.isNaN(numeric)) {
    return String(price)
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(numeric)
}

function toExploreVenue(venue) {
  if (venue.type) {
    return venue
  }

  return {
    slug: venue.slug ?? venue.id?.toString(),
    name: venue.name,
    type: venue.category,
    location: [venue.district, venue.city, venue.state].filter(Boolean).join(", "),
    address: venue.address,
    capacity: venue.capacity,
    price: venue.price,
    image: venue.image || "/placeholder.svg",
    rating: null,
  }
}

export async function fetchExploreVenues({ categoryId } = {}) {
  const { data } = categoryId
    ? await api.get("/venues/explore", {
        baseURL: API_BASE_URL,
        params: { category_id: categoryId, limit: 12 },
      })
    : await api.get("/venues/home", { baseURL: API_BASE_URL })

  return data.map(toExploreVenue)
}

export async function fetchVenueCategories() {
  const { data } = await api.get("/venues/categories", { baseURL: API_BASE_URL })
  return [{ id: null, name: "All venues" }, ...data]
}

export function getVenues() {
  return venues
}

export function getVenueBySlug(slug) {
  return venues.find((venue) => venue.slug === slug)
}

export function getRelatedVenues(venue) {
  if (!venue) {
    return []
  }

  return venues
    .filter((candidate) => candidate.type === venue.type && candidate.slug !== venue.slug)
    .slice(0, 3)
}
