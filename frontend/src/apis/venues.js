import { categories, venues } from "../data/venues"
import api from "../lib/axios"

export async function fetchAllVenuesHome() {
  const { data } = await api.get("http://127.0.0.1:8000/venues/all")
  return data
}

export function getVenueCategories() {
  return categories
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
