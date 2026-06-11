import { BrowserRouter, Route, Routes } from "react-router-dom"
import HomePage from "../pages/HomePage"
import VenueDetailsPage from "../pages/VenueDetailsPage"

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/venue/:id" element={<VenueDetailsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
