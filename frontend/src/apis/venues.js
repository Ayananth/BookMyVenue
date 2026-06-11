import { categories, venues } from "../data/venues"

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
