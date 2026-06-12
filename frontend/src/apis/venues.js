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
    id: venue.id,
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

export async function fetchAllVenuesHome() {
  let { data } = await api.get("/venues/home", { baseURL: API_BASE_URL })
  return data.map(toExploreVenue)
}

export async function fetchVenueCategories() {
  const { data } = await api.get("/venues/categories", { baseURL: API_BASE_URL })
  return ["All venues", ...data.map((category) => category.name)]
}

export function getVenues() {
  return venues
}

export function getVenueById(id) {
  return venues.find((venue) => venue.id === Number(id))
}

export function getRelatedVenues(venue) {
  if (!venue) {
    return []
  }

  return venues
    .filter((candidate) => candidate.type === venue.type && candidate.id !== venue.id)
    .slice(0, 3)
}
