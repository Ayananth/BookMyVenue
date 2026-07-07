import { useEffect } from "react"
import { useLocation } from "react-router-dom"
import Categories from "../components/sections/Categories"
import Contact from "../components/sections/Contact"
import ExploreVenues from "../components/sections/ExploreVenues"
import Features from "../components/sections/Features"
import ForOwners from "../components/sections/ForOwners"
import Hero from "../components/sections/Hero"
import HowItWorks from "../components/sections/HowItWorks"
import MainLayout from "../layouts/MainLayout"

export default function HomePage() {
  const location = useLocation()

  useEffect(() => {
    if (!location.hash) return undefined

    const id = location.hash.slice(1)
    let cancelled = false

    const tryScroll = (attempt) => {
      if (cancelled) return
      const el = document.getElementById(id)
      if (el) {
        el.scrollIntoView({ behavior: "smooth" })
      } else if (attempt < 5) {
        setTimeout(() => tryScroll(attempt + 1), 100)
      }
    }

    const timer = setTimeout(() => tryScroll(0), 50)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [location.hash, location.key])

  return (
    <MainLayout>
      <main>
        <Hero />
        <Categories />
        <ExploreVenues />
        <Features />
        <ForOwners />
        <HowItWorks />
        <Contact />
      </main>
    </MainLayout>
  )
}
