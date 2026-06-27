import { venues } from "../data/venues"
import api from "../lib/axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

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
