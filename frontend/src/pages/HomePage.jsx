import Categories from "../components/sections/Categories"
import Contact from "../components/sections/Contact"
import ExploreVenues from "../components/sections/ExploreVenues"
import Features from "../components/sections/Features"
import ForOwners from "../components/sections/ForOwners"
import Hero from "../components/sections/Hero"
import HowItWorks from "../components/sections/HowItWorks"
import MainLayout from "../layouts/MainLayout"

export default function HomePage() {
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
