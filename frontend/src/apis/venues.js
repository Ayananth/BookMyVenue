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

export async function fetchVenueBySlug(slug) {
  const { data } = await api.get(`/venues/${slug}/`, apiConfig)
  return data
}

export async function updateVenue(slug, payload) {
  const { data } = await api.patch(`/venues/${slug}/`, payload, apiConfig)
  return data
}

export function venueToFormState(venue) {
  return {
    name: venue.name ?? "",
    category: venue.category?.id ? String(venue.category.id) : "",
    location: venue.location?.id ? String(venue.location.id) : "",
    address: venue.address ?? "",
    description: venue.description ?? "",
    capacity: venue.capacity != null ? String(venue.capacity) : "",
    bookingType: venue.booking_type ?? "",
    contactName: venue.contact_name ?? "",
    contactPhone: venue.contact_phone ?? "",
    contactEmail: venue.contact_email ?? "",
  }
}

export function venueImagesToFormState(images = []) {
  return images.map((image, index) => ({
    public_id: image.id ?? `image-${index}`,
    image_url: image.image_url,
    is_cover: image.is_cover,
    sort_order: image.sort_order ?? index + 1,
  }))
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

export const VENUE_STATUS_STYLES = {
  approved: "bg-emerald-50 text-emerald-700 border-emerald-200",
  pending_approval: "bg-amber-50 text-amber-700 border-amber-200",
  rejected: "bg-red-50 text-red-700 border-red-200",
  suspended: "bg-slate-100 text-slate-600 border-slate-200",
}

export const VENUE_STATUS_LABELS = {
  approved: "Approved",
  pending_approval: "Pending approval",
  rejected: "Rejected",
  suspended: "Suspended",
}

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

export const buildVenueUpdatePayload = buildVenuePayload

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

export function formatVenueLocation(location) {
  if (!location) return ""
  if (typeof location === "string") return location
  return [location.district, location.city, location.state].filter(Boolean).join(", ")
}

const BOOKING_TYPE_LABELS = {
  hourly: "Hourly slots",
  session: "Session slots",
  full_day: "Full day rental",
}

function getVenueGallery(images = []) {
  const sorted = [...images].sort(
    (a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0),
  )
  const urls = sorted.map((image) => image.image_url).filter(Boolean)
  return urls.length > 0 ? urls : ["/placeholder.svg"]
}

function getCoverImage(images = []) {
  if (!images.length) return "/placeholder.svg"
  const cover = images.find((image) => image.is_cover)
  if (cover?.image_url) return cover.image_url
  const sorted = [...images].sort(
    (a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0),
  )
  return sorted[0]?.image_url ?? "/placeholder.svg"
}

export function toVenueDetailPage(venue) {
  const gallery = getVenueGallery(venue.images)
  const image = getCoverImage(venue.images)
  const location = formatVenueLocation(venue.location)
  const type = venue.category?.name ?? venue.type ?? ""
  const amenities = Array.isArray(venue.amenities) ? venue.amenities : []
  const priceValue = venue.min_price != null ? Number(venue.min_price) : null
  const formattedPrice = formatVenuePrice(priceValue)
  const pricePerPerson =
    priceValue != null && venue.capacity
      ? Math.max(1, Math.round(priceValue / venue.capacity))
      : null

  return {
    slug: venue.slug,
    name: venue.name,
    location,
    address: venue.address ?? "",
    type,
    capacity: venue.capacity,
    price: formattedPrice,
    priceValue,
    pricePerPerson,
    rating: venue.rating ?? null,
    reviews: venue.reviews ?? 0,
    image,
    gallery,
    description: venue.description ?? "",
    amenities,
    parking: venue.parking ?? null,
    hours: BOOKING_TYPE_LABELS[venue.booking_type] ?? venue.hours ?? null,
    phone: venue.contact_phone ?? venue.phone ?? "",
    email: venue.contact_email ?? venue.email ?? "",
    owner: venue.contact_name ?? venue.owner ?? "Venue manager",
    ownerImage: image,
    reviews_list: venue.reviews_list ?? [],
    highlights: venue.highlights ?? amenities.slice(0, 4),
    minEventSize: venue.minEventSize ?? null,
    maxEventSize: venue.maxEventSize ?? venue.capacity ?? null,
    eventTypes: venue.eventTypes ?? (type ? [type] : []),
    categoryId: venue.category?.id ?? null,
    bookingType: venue.booking_type,
  }
}

export async function fetchVenueDetail(slug) {
  const data = await fetchVenueBySlug(slug)
  return toVenueDetailPage(data)
}

export async function fetchRelatedVenues({ categoryId, slug, limit = 3 } = {}) {
  if (!categoryId) return []

  const { data } = await api.get("/venues/", {
    baseURL: API_BASE_URL,
    params: { category_id: categoryId, limit: limit + 1 },
  })

  const venues = data.results ?? data
  return venues
    .filter((candidate) => candidate.slug !== slug)
    .slice(0, limit)
    .map(toExploreVenue)
}

function toExploreVenue(venue) {
  if (venue.type && typeof venue.location === "string") {
    return venue
  }

  const location =
    typeof venue.location === "object" && venue.location
      ? [venue.location.district, venue.location.city, venue.location.state]
          .filter(Boolean)
          .join(", ")
      : [venue.district, venue.city, venue.state].filter(Boolean).join(", ")

  const categoryName =
    typeof venue.category === "object" && venue.category
      ? venue.category.name
      : venue.category ?? venue.type

  return {
    slug: venue.slug ?? venue.id?.toString(),
    name: venue.name,
    type: categoryName,
    location,
    address: venue.address,
    capacity: venue.capacity,
    price: venue.min_price ?? venue.price,
    image: venue.cover_image ?? venue.image ?? "/placeholder.svg",
    rating: venue.rating ?? null,
  }
}

export async function fetchExploreVenues({ categoryId } = {}) {
  const params = { limit: 12 }
  if (categoryId != null) {
    params.category_id = categoryId
  }

  const { data } = await api.get("/venues/", {
    baseURL: API_BASE_URL,
    params,
  })

  const venues = data.results ?? data
  return venues.map(toExploreVenue)
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
