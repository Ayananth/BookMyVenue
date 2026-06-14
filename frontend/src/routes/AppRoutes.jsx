import { BrowserRouter, Route, Routes } from "react-router-dom"
import ExploreVenuesPage from "../pages/ExploreVenuesPage"
import HomePage from "../pages/HomePage"
import ProfilePage from "../pages/ProfilePage"
import VenueDetailsPage from "../pages/VenueDetailsPage"

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/venues" element={<ExploreVenuesPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/venue/:id" element={<VenueDetailsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
