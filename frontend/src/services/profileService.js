const mockProfile = {
  id: 1,
  name: "Ayananth",
  email: "user@example.com",
  phone: "+91 9876543210",
}

const mockBookings = [
  {
    id: "BMV-001",
    venueName: "Royal Convention Center",
    bookingDate: "2026-08-10",
    eventDate: "2026-12-15",
    amount: 25000,
    status: "confirmed",
  },
  {
    id: "BMV-002",
    venueName: "Willow Wedding Hall",
    bookingDate: "2026-06-02",
    eventDate: "2026-09-18",
    amount: 42000,
    status: "pending",
  },
  {
    id: "BMV-003",
    venueName: "Summit Conference Room",
    bookingDate: "2026-02-20",
    eventDate: "2026-04-12",
    amount: 9000,
    status: "completed",
  },
  {
    id: "BMV-004",
    venueName: "Emerald Party Hall",
    bookingDate: "2026-01-08",
    eventDate: "2026-03-22",
    amount: 18000,
    status: "cancelled",
  },
]

const mockFavouriteVenues = [
  {
    id: 1,
    name: "Royal Convention Center",
    location: "Thrissur, Kerala",
    rating: 4.8,
    price: 25000,
    image: "/venues/hero-banquet.png",
  },
  {
    id: 2,
    name: "Willow Wedding Hall",
    location: "Kochi, Kerala",
    rating: 4.9,
    price: 42000,
    image: "/venues/garden.png",
  },
  {
    id: 3,
    name: "Summit Conference Room",
    location: "Kochi, Karnataka",
    rating: 4.6,
    price: 9000,
    image: "/venues/conference.png",
  },
]

export const fetchProfile = async () => {
  // Future API integration: replace with GET /profile.
  return mockProfile
}

export const fetchBookings = async () => {
  // Future API integration: replace with GET /bookings.
  return mockBookings
}

export const fetchFavouriteVenues = async () => {
  // Future API integration: replace with GET /favourite-venues.
  return mockFavouriteVenues
}

export const updateProfile = async (profile) => {
  // Future API integration: replace with PATCH /profile.
  return profile
}
