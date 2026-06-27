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
    rating: 0,
    image: venue.cover_image ?? venue.image ?? "/placeholder.svg",
  }
}

export const fetchVenues = async () => {
  const { data } = await api.get("/venues/", {
    baseURL: API_BASE_URL,
    params: { limit: EXPLORE_VENUE_MAX_LIMIT },
  })

  const venues = data.results ?? data
  return venues.map(toExplorePageVenue)
}
