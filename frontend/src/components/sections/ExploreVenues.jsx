import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import { Star, Users, MapPin, ArrowRight, Heart, Search, X } from "lucide-react"
import { fetchExploreVenues, fetchVenueCategories, fetchVenueLocationGroups, formatVenuePrice } from "../../apis/venues"
import LocationPicker from "../venues/LocationPicker"
import Reveal from "../common/Reveal"

const ALL_VENUES_CATEGORY = { id: null, name: "All venues" }
const SEARCH_DEBOUNCE_MS = 400

export default function ExploreVenues() {
  const navigate = useNavigate()
  const debounceTimerRef = useRef(null)
  const [activeCategory, setActiveCategory] = useState(ALL_VENUES_CATEGORY)
  const [selectedCityId, setSelectedCityId] = useState(null)
  const [searchInput, setSearchInput] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const [locationGroups, setLocationGroups] = useState([])
  const [loadingLocations, setLoadingLocations] = useState(true)
  const [venues, setVenues] = useState([])
  const [categories, setCategories] = useState([ALL_VENUES_CATEGORY])
  const [loading, setLoading] = useState(true)
  const [liked, setLiked] = useState({})

  useEffect(() => {
    fetchVenueCategories()
      .then((categoryData) => setCategories(categoryData))
      .catch((error) => console.error("Failed to fetch categories:", error))
  }, [])

  useEffect(() => {
    setLoadingLocations(true)
    fetchVenueLocationGroups()
      .then((groupData) => setLocationGroups(groupData))
      .catch((error) => console.error("Failed to fetch locations:", error))
      .finally(() => setLoadingLocations(false))
  }, [])

  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [])

  useEffect(() => {
    let active = true
    setLoading(true)

    fetchExploreVenues({
      categoryId: activeCategory.id,
      cityId: selectedCityId,
      search: searchQuery || undefined,
    })
      .then((venueData) => {
        if (active) setVenues(venueData)
      })
      .catch((error) => console.error("Failed to fetch venues:", error))
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [activeCategory, selectedCityId, searchQuery])

  const applySearchQuery = (value) => {
    const trimmed = value.trim()
    setSearchQuery((current) => (current === trimmed ? current : trimmed))
  }

  const handleSearchInputChange = (value) => {
    setSearchInput(value)

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    if (value.trim() === "") {
      applySearchQuery("")
      return
    }

    debounceTimerRef.current = setTimeout(() => {
      applySearchQuery(value)
    }, SEARCH_DEBOUNCE_MS)
  }

  const handleSearchKeyDown = (event) => {
    if (event.key !== "Enter") return

    event.preventDefault()
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }
    applySearchQuery(searchInput)
  }

  const handleSearchClear = () => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }
    setSearchInput("")
    applySearchQuery("")
  }

  const handleLocationSelect = (city) => {
    setSelectedCityId(city?.id ?? null)
  }

  const handleLocationClear = () => {
    setSelectedCityId(null)
  }

  return (
    <section id="explore" className="px-4 py-24">
      <div className="mx-auto max-w-6xl">
        <Reveal className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
          <div className="max-w-xl">
            <span className="text-sm font-semibold uppercase tracking-wider text-accent">
              Explore venues
            </span>
            <h2 className="mt-3 font-serif text-4xl font-semibold tracking-tight text-foreground text-balance sm:text-5xl">
              Spaces worth celebrating in
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
              Hand-picked venues for weddings, parties, conferences, and
              everything in between.
            </p>
          </div>
          <a
            href="/venues"
            className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-5 py-2.5 text-sm font-semibold text-foreground transition-colors hover:border-primary hover:text-primary"
          >
            View all venues
            <ArrowRight className="h-4 w-4" />
          </a>
        </Reveal>

        <Reveal delay={0.1} className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-end">
          <label className="relative min-w-0 w-full sm:max-w-xs">
            <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Search
            </span>
            <div className="relative">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                value={searchInput}
                placeholder="Search by venue name..."
                autoComplete="off"
                onChange={(event) => handleSearchInputChange(event.target.value)}
                onKeyDown={handleSearchKeyDown}
                className="h-11 w-full rounded-full border border-border bg-card py-2 pl-10 pr-10 text-sm font-semibold text-foreground outline-none transition hover:border-primary/50 focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
              {searchInput && (
                <button
                  type="button"
                  onClick={handleSearchClear}
                  aria-label="Clear search"
                  className="absolute right-3 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-muted-foreground transition hover:bg-muted hover:text-foreground"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          </label>
          <LocationPicker
            locationGroups={locationGroups}
            selectedCityId={selectedCityId}
            onSelect={handleLocationSelect}
            onClear={handleLocationClear}
            loading={loadingLocations}
            className="w-full sm:max-w-xs"
          />
        </Reveal>

        <Reveal delay={0.12} className="mt-4 flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.id ?? "all"}
              onClick={() => setActiveCategory(category)}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition-all ${
                activeCategory.id === category.id
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground"
              }`}
            >
              {category.name}
            </button>
          ))}
        </Reveal>

        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {loading && (
            <p className="col-span-full text-center text-muted-foreground">
              Loading venues...
            </p>
          )}

          {!loading && venues.length === 0 && (
            <p className="col-span-full text-center text-muted-foreground">
              No venues found
              {searchQuery ? ` matching "${searchQuery}"` : ""}
              {activeCategory.id ? " in this category" : ""}
              {selectedCityId ? " for this location" : ""}.
            </p>
          )}

          <AnimatePresence>
            {!loading &&
              venues.map((v, i) => {
                const formattedPrice = formatVenuePrice(v.price)

                return (
                  <motion.article
                    key={v.slug}
                    layout
                    initial={{ opacity: 0, y: 24 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-60px" }}
                    transition={{ duration: 0.5, delay: (i % 3) * 0.08 }}
                    onClick={() => navigate(`/venues/${v.slug}`)}
                    className="group cursor-pointer overflow-hidden rounded-2xl border border-border bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_18px_44px_rgba(27,36,29,0.12)]"
                  >
                    <div className="relative overflow-hidden">
                      <img
                        src={v.image || "/placeholder.svg"}
                        alt={v.name}
                        className="h-52 w-full object-cover transition-transform duration-500 group-hover:scale-105"
                      />
                      <span className="absolute left-3 top-3 rounded-full bg-card/90 px-3 py-1 text-xs font-semibold text-foreground backdrop-blur-sm">
                        {v.type}
                      </span>
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation()
                          setLiked((state) => ({ ...state, [v.slug]: !state[v.slug] }))
                        }}
                        aria-label="Save venue"
                        className="absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-full bg-card/90 text-foreground backdrop-blur-sm transition-colors hover:text-accent"
                      >
                        <Heart
                          className={`h-4 w-4 ${
                            liked[v.slug] ? "fill-accent text-accent" : ""
                          }`}
                        />
                      </button>
                    </div>

                    <div className="p-5">
                      <div className="flex items-start justify-between gap-3">
                        <h3 className="text-lg font-semibold text-foreground">
                          {v.name}
                        </h3>
                        {v.rating != null && (
                          <span className="flex shrink-0 items-center gap-1 text-sm font-semibold text-foreground">
                            <Star className="h-4 w-4 fill-accent text-accent" />
                            {v.rating}
                          </span>
                        )}
                      </div>

                      <p className="mt-1 flex items-center gap-1.5 text-sm text-muted-foreground">
                        <MapPin className="h-4 w-4" /> {v.location}
                      </p>

                      <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
                        <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
                          <Users className="h-4 w-4" /> Up to {v.capacity}
                        </span>
                        {formattedPrice && (
                          <span className="text-sm text-muted-foreground">
                            <span className="font-serif text-lg font-semibold text-foreground">
                              {formattedPrice}
                            </span>{" "}
                            /slot
                          </span>
                        )}
                      </div>
                    </div>
                  </motion.article>
                )
              })}
          </AnimatePresence>
        </div>
      </div>
    </section>
  )
}
