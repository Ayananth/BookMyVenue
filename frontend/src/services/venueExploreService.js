import api from "../lib/axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
const EXPLORE_VENUE_MAX_LIMIT = 50

function toExplorePageVenue(venue) {
  const category =
    typeof venue.category === "object" && venue.category
      ? venue.category
      : { id: venue.category_id, name: venue.category }

  const location =
    typeof venue.location === "object" && venue.location
      ? venue.location
      : { state: venue.state, district: venue.district, city: venue.city }

  const price = venue.min_price ?? venue.price

  return {
    slug: venue.slug ?? venue.id?.toString(),
    name: venue.name,
    category,
    location,
    capacity: venue.capacity,
    price: price != null ? Number(price) : 0,
    rating: venue.rating ?? 0,
    image: venue.cover_image ?? venue.image ?? "/placeholder.svg",
  }
}

export function priceRangeToParams(price) {
  switch (price) {
    case "Below INR 10,000":
      return { max_price: 9999 }
    case "INR 10,000 - INR 25,000":
      return { min_price: 10000, max_price: 25000 }
    case "INR 25,000 - INR 50,000":
      return { min_price: 25001, max_price: 50000 }
    case "Above INR 50,000":
      return { min_price: 50001 }
    default:
      return {}
  }
}

export function sortToOrdering(sort) {
  switch (sort) {
    case "price-low":
      return "min_price"
    case "price-high":
      return "-min_price"
    case "recommended":
    default:
      return "-created_at"
  }
}

export const fetchVenues = async ({ min_price, max_price, ordering, category_id } = {}) => {
  const params = { limit: EXPLORE_VENUE_MAX_LIMIT }

  if (category_id != null) params.category_id = category_id
  if (min_price != null) params.min_price = min_price
  if (max_price != null) params.max_price = max_price
  if (ordering) params.ordering = ordering

  const { data } = await api.get("/venues/", {
    baseURL: API_BASE_URL,
    params,
  })

  const venues = data.results ?? data
  return venues.map(toExplorePageVenue)
}
