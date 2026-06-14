import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { AnimatePresence, motion } from "framer-motion"
import {
  CalendarDays,
  Check,
  Heart,
  LogOut,
  Mail,
  Star,
  TicketCheck,
  User,
  X,
} from "lucide-react"
import MainLayout from "../layouts/MainLayout"
import { useAuth } from "../contexts/AuthContext"
import {
  fetchBookings,
  fetchFavouriteVenues,
  fetchProfile,
  updateProfile,
} from "../services/profileService"

const navItems = [
  { id: "profile", label: "Profile Information", icon: User },
  { id: "bookings", label: "My Bookings", icon: TicketCheck },
  { id: "favourites", label: "Favourites", icon: Heart },
]

const bookingTabs = [
  { id: "upcoming", label: "Upcoming Bookings" },
  { id: "history", label: "Booking History" },
]

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value)
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value))
}

function statusClasses(status) {
  const styles = {
    confirmed: "bg-primary/10 text-primary border-primary/20",
    pending: "bg-accent/15 text-foreground border-accent/30",
    completed: "bg-muted text-muted-foreground border-border",
    cancelled: "bg-red-100 text-red-700 border-red-200",
  }

  return styles[status] || styles.completed
}

function SidebarNav({ activeSection, onSectionChange, onLogout }) {
  return (
    <aside className="hidden lg:block">
      <div className="sticky top-28 rounded-2xl border border-border bg-card p-4 shadow-sm">
        <div className="border-b border-border px-2 pb-5">
          <p className="text-sm font-semibold uppercase tracking-wider text-accent">Account</p>
          <h1 className="mt-2 font-serif text-3xl font-semibold text-foreground">My Profile</h1>
        </div>

        <nav className="mt-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = activeSection === item.id

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSectionChange(item.id)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-semibold transition ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            )
          })}
        </nav>

        <div className="mt-8 border-t border-border pt-4">
          <button
            type="button"
            onClick={onLogout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-semibold text-red-700 transition hover:bg-red-50"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </div>
    </aside>
  )
}

function MobileNav({ activeSection, onSectionChange }) {
  return (
    <div className="lg:hidden">
      <div className="flex gap-2 overflow-x-auto rounded-2xl border border-border bg-card p-2 shadow-sm">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeSection === item.id

          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onSectionChange(item.id)}
              className={`flex shrink-0 items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}

function ProfileInformation({ profile, onSave }) {
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState(profile)
  const [errors, setErrors] = useState({})
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setForm(profile)
  }, [profile])

  const validate = () => {
    const nextErrors = {}

    if (!form.name.trim()) {
      nextErrors.name = "Full name is required."
    }

    if (!form.phone.trim()) {
      nextErrors.phone = "Phone number is required."
    } else if (!/^\+?[0-9\s-]{8,}$/.test(form.phone.trim())) {
      nextErrors.phone = "Enter a valid phone number."
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSave = async () => {
    if (!validate()) {
      return
    }

    setSaving(true)
    const updatedProfile = await updateProfile(form)
    onSave(updatedProfile)
    setSaving(false)
    setEditing(false)
  }

  const handleCancel = () => {
    setForm(profile)
    setErrors({})
    setEditing(false)
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-border bg-card p-6 shadow-sm"
    >
      <div className="flex flex-col justify-between gap-4 border-b border-border pb-5 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-accent">Profile Information</p>
          <h2 className="mt-2 font-serif text-3xl font-semibold text-foreground">Personal details</h2>
        </div>
        {!editing && (
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-transform hover:-translate-y-0.5"
          >
            Edit Profile
          </button>
        )}
      </div>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-foreground">Full Name</span>
          <input
            type="text"
            value={form.name}
            disabled={!editing}
            onChange={(event) => setForm((state) => ({ ...state, name: event.target.value }))}
            className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm font-semibold text-foreground outline-none transition disabled:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-primary/20"
          />
          {errors.name && <p className="mt-2 text-sm text-red-700">{errors.name}</p>}
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-foreground">Phone Number</span>
          <input
            type="tel"
            value={form.phone}
            disabled={!editing}
            onChange={(event) => setForm((state) => ({ ...state, phone: event.target.value }))}
            className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm font-semibold text-foreground outline-none transition disabled:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-primary/20"
          />
          {errors.phone && <p className="mt-2 text-sm text-red-700">{errors.phone}</p>}
        </label>

        <label className="block md:col-span-2">
          <span className="mb-2 block text-sm font-semibold text-foreground">Email Address</span>
          <div className="flex items-center gap-3 rounded-xl border border-border bg-muted px-4 py-3 text-sm font-semibold text-muted-foreground">
            <Mail className="h-4 w-4 text-primary" />
            {profile.email}
          </div>
        </label>
      </div>

      {editing && (
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition hover:opacity-90 disabled:opacity-60"
          >
            <Check className="h-4 w-4" />
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <button
            type="button"
            onClick={handleCancel}
            className="inline-flex items-center justify-center gap-2 rounded-full border border-border px-5 py-3 text-sm font-semibold text-foreground transition hover:border-primary hover:text-primary"
          >
            <X className="h-4 w-4" />
            Cancel Changes
          </button>
        </div>
      )}
    </motion.section>
  )
}

function BookingCard({ booking }) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 12 }}
      className="rounded-2xl border border-border bg-card p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-[0_18px_44px_rgba(27,36,29,0.10)]"
    >
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div>
          <h3 className="font-serif text-2xl font-semibold text-foreground">{booking.venueName}</h3>
          <p className="mt-1 text-sm font-semibold text-muted-foreground">Booking ID: {booking.id}</p>
        </div>
        <span className={`w-fit rounded-full border px-3 py-1 text-xs font-bold capitalize ${statusClasses(booking.status)}`}>
          {booking.status}
        </span>
      </div>

      <div className="mt-5 grid gap-4 border-t border-border pt-5 sm:grid-cols-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Event Date</p>
          <p className="mt-1 font-semibold text-foreground">{formatDate(booking.eventDate)}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Booking Date</p>
          <p className="mt-1 font-semibold text-foreground">{formatDate(booking.bookingDate)}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Amount</p>
          <p className="mt-1 font-serif text-xl font-semibold text-foreground">{formatCurrency(booking.amount)}</p>
        </div>
      </div>

      <button
        type="button"
        className="mt-5 rounded-full border border-border px-5 py-2.5 text-sm font-semibold text-foreground transition hover:border-primary hover:text-primary"
      >
        View Details
      </button>
    </motion.article>
  )
}

function BookingsSection({ bookings }) {
  const [activeTab, setActiveTab] = useState("upcoming")

  const visibleBookings = useMemo(() => {
    const upcomingStatuses = ["confirmed", "pending"]
    return bookings.filter((booking) =>
      activeTab === "upcoming"
        ? upcomingStatuses.includes(booking.status)
        : !upcomingStatuses.includes(booking.status)
    )
  }, [activeTab, bookings])

  return (
    <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
      <div className="rounded-2xl border border-border bg-card p-4 shadow-sm">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-accent">My Bookings</p>
            <h2 className="mt-2 font-serif text-3xl font-semibold text-foreground">Venue reservations</h2>
          </div>
          <div className="flex rounded-full border border-border bg-background p-1">
            {bookingTabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-5 space-y-4">
        <AnimatePresence mode="popLayout">
          {visibleBookings.map((booking) => (
            <BookingCard key={booking.id} booking={booking} />
          ))}
        </AnimatePresence>

        {visibleBookings.length === 0 && (
          <div className="rounded-2xl border border-border bg-card px-6 py-14 text-center">
            <CalendarDays className="mx-auto h-8 w-8 text-primary" />
            <h3 className="mt-3 font-serif text-2xl font-semibold text-foreground">
              {activeTab === "upcoming" ? "No upcoming bookings found." : "No booking history found."}
            </h3>
          </div>
        )}
      </div>
    </motion.section>
  )
}

function FavouriteVenueCard({ venue, onRemove }) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 14 }}
      className="group overflow-hidden rounded-2xl border border-border bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_18px_44px_rgba(27,36,29,0.12)]"
    >
      <div className="relative overflow-hidden">
        <img
          src={venue.image || "/placeholder.svg"}
          alt={venue.name}
          className="h-52 w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <span className="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-card/90 px-3 py-1 text-sm font-semibold text-foreground backdrop-blur-sm">
          <Star className="h-4 w-4 fill-accent text-accent" />
          {venue.rating}
        </span>
      </div>

      <div className="p-5">
        <h3 className="text-lg font-semibold text-foreground">{venue.name}</h3>
        <p className="mt-2 flex items-center gap-1.5 text-sm text-muted-foreground">
          <MapPin className="h-4 w-4" />
          {venue.location}
        </p>
        <p className="mt-4 text-sm text-muted-foreground">
          From <span className="font-serif text-xl font-semibold text-foreground">{formatCurrency(venue.price)}</span> /slot
        </p>

        <div className="mt-5 flex flex-col gap-2 border-t border-border pt-4 sm:flex-row">
          <button
            type="button"
            className="flex-1 rounded-full bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition hover:opacity-90"
          >
            View Venue
          </button>
          <button
            type="button"
            onClick={onRemove}
            className="flex-1 rounded-full border border-border px-4 py-2.5 text-sm font-semibold text-foreground transition hover:border-primary hover:text-primary"
          >
            Remove Favourite
          </button>
        </div>
      </div>
    </motion.article>
  )
}

function FavouritesSection({ venues, onRemove }) {
  return (
    <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
      <div className="mb-5 rounded-2xl border border-border bg-card p-5 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wider text-accent">Favourites</p>
        <h2 className="mt-2 font-serif text-3xl font-semibold text-foreground">Saved venues</h2>
      </div>

      {venues.length === 0 ? (
        <div className="rounded-2xl border border-border bg-card px-6 py-14 text-center">
          <Heart className="mx-auto h-8 w-8 text-primary" />
          <h3 className="mt-3 font-serif text-2xl font-semibold text-foreground">No favourite venues found.</h3>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          <AnimatePresence mode="popLayout">
            {venues.map((venue) => (
              <FavouriteVenueCard key={venue.id} venue={venue} onRemove={() => onRemove(venue.id)} />
            ))}
          </AnimatePresence>
        </div>
      )}
    </motion.section>
  )
}

function LogoutModal({ open, onCancel, onLogout }) {
  if (!open) {
    return null
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-foreground/50 p-4 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, y: 18, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl"
      >
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-700">
          <LogOut className="h-5 w-5" />
        </div>
        <h2 className="mt-4 font-serif text-3xl font-semibold text-foreground">Are you sure you want to logout?</h2>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
          You will need to sign in again to access your profile and bookings.
        </p>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-full border border-border px-5 py-3 text-sm font-semibold text-foreground transition hover:border-primary hover:text-primary"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onLogout}
            className="flex-1 rounded-full bg-red-700 px-5 py-3 text-sm font-semibold text-white transition hover:opacity-90"
          >
            Logout
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default function ProfilePage() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [activeSection, setActiveSection] = useState("profile")
  const [profile, setProfile] = useState(null)
  const [bookings, setBookings] = useState([])
  const [favouriteVenues, setFavouriteVenues] = useState([])
  const [loading, setLoading] = useState(true)
  const [logoutOpen, setLogoutOpen] = useState(false)

  useEffect(() => {
    let active = true

    setLoading(true)

    Promise.all([fetchProfile(), fetchBookings(), fetchFavouriteVenues()])
      .then(([profileData, bookingData, favouriteVenueData]) => {
        if (active) {
          setProfile(profileData)
          setBookings(bookingData)
          setFavouriteVenues(favouriteVenueData)
        }
      })
      .catch((error) => console.error("Failed to load profile page:", error))
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [])

  const removeFavourite = (venueId) => {
    setFavouriteVenues((venues) => venues.filter((venue) => venue.id !== venueId))
  }

  const handleLogout = () => {
    logout()
    setLogoutOpen(false)
    navigate("/")
  }

  const renderContent = () => {
    if (loading || !profile) {
      return (
        <div className="rounded-2xl border border-border bg-card py-16 text-center text-muted-foreground">
          Loading profile...
        </div>
      )
    }

    if (activeSection === "bookings") {
      return <BookingsSection bookings={bookings} />
    }

    if (activeSection === "favourites") {
      return <FavouritesSection venues={favouriteVenues} onRemove={removeFavourite} />
    }

    return <ProfileInformation profile={profile} onSave={setProfile} />
  }

  return (
    <MainLayout>
      <main className="px-4 pt-32 pb-20 sm:pt-36">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8 lg:hidden">
            <p className="text-sm font-semibold uppercase tracking-wider text-accent">Account</p>
            <h1 className="mt-2 font-serif text-4xl font-semibold text-foreground">My Profile</h1>
          </div>

          <div className="grid gap-8 lg:grid-cols-[280px_1fr]">
            <SidebarNav
              activeSection={activeSection}
              onSectionChange={setActiveSection}
              onLogout={() => setLogoutOpen(true)}
            />

            <div>
              <MobileNav activeSection={activeSection} onSectionChange={setActiveSection} />
              <div className="mt-5 lg:mt-0">{renderContent()}</div>
              <button
                type="button"
                onClick={() => setLogoutOpen(true)}
                className="mt-6 flex w-full items-center justify-center gap-2 rounded-2xl border border-border bg-card px-5 py-3 text-sm font-semibold text-red-700 transition hover:bg-red-50 lg:hidden"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </main>

      <LogoutModal
        open={logoutOpen}
        onCancel={() => setLogoutOpen(false)}
        onLogout={handleLogout}
      />
    </MainLayout>
  )
}
