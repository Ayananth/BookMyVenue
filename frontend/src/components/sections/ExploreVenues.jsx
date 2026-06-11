import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import { Star, Users, MapPin, ArrowRight, Heart } from "lucide-react"
import { fetchAllVenuesHome, getVenueCategories, getVenues } from "../../apis/venues"
import Reveal from "../common/Reveal"

export default function ExploreVenues() {
  const navigate = useNavigate()
  const [active, setActive] = useState("All venues")
  const [liked, setLiked] = useState({})
  const categories = getVenueCategories()
  const venues = getVenues()

  useEffect(() => {
    fetchAllVenuesHome()
      .then((data) => console.log(data))
      .catch((error) => console.error("Failed to fetch venues:", error))
  }, [])

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
            href="#explore"
            className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-5 py-2.5 text-sm font-semibold text-foreground transition-colors hover:border-primary hover:text-primary"
          >
            View all venues
            <ArrowRight className="h-4 w-4" />
          </a>
        </Reveal>

        {/* Category filter */}
        <Reveal delay={0.1} className="mt-10 flex flex-wrap gap-2">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setActive(c)}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition-all ${
                active === c
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground"
              }`}
            >
              {c}
            </button>
          ))}
        </Reveal>

        {/* Grid */}
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence>
            {venues.map((v, i) => (
              <motion.article
                key={v.name}
                layout
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: (i % 3) * 0.08 }}
                onClick={() => navigate(`/venue/${v.id}`)}
                className="group overflow-hidden rounded-2xl border border-border bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_18px_44px_rgba(27,36,29,0.12)] cursor-pointer"
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
                    onClick={() =>
                      setLiked((s) => ({ ...s, [v.name]: !s[v.name] }))
                    }
                    aria-label="Save venue"
                    className="absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-full bg-card/90 text-foreground backdrop-blur-sm transition-colors hover:text-accent"
                  >
                    <Heart
                      className={`h-4 w-4 ${
                        liked[v.name] ? "fill-accent text-accent" : ""
                      }`}
                    />
                  </button>
                </div>

                <div className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-lg font-semibold text-foreground">
                      {v.name}
                    </h3>
                    <span className="flex shrink-0 items-center gap-1 text-sm font-semibold text-foreground">
                      <Star className="h-4 w-4 fill-accent text-accent" />
                      {v.rating}
                    </span>
                  </div>

                  <p className="mt-1 flex items-center gap-1.5 text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4" /> {v.location}
                  </p>

                  <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
                    <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
                      <Users className="h-4 w-4" /> Up to {v.capacity}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      <span className="font-serif text-lg font-semibold text-foreground">
                        {v.price}
                      </span>{" "}
                      /day
                    </span>
                  </div>
                </div>
              </motion.article>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </section>
  )
}
