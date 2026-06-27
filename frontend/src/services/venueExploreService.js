import api from "../lib/axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
const EXPLORE_VENUE_MAX_LIMIT = 50

function toExplorePageVenue(venue) {
  return {
    slug: venue.slug ?? venue.id?.toString(),
    name: venue.name,
    category: {
      id: venue.category_id,
      name: venue.category,
    },
    location: {
      state: venue.state,
      district: venue.district,
      city: venue.city,
    },
    capacity: venue.capacity,
    price: venue.price != null ? Number(venue.price) : 0,
    rating: 0,
    image: venue.image || "/placeholder.svg",
  }
}

export const fetchVenues = async () => {
  const { data } = await api.get("/venues/explore", {
    baseURL: API_BASE_URL,
    params: { limit: EXPLORE_VENUE_MAX_LIMIT },
  })

  return data.map(toExplorePageVenue)
}
