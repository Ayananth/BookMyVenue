import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import ExploreVenuesPage from "../pages/ExploreVenuesPage"
import HomePage from "../pages/HomePage"
import ProfilePage from "../pages/ProfilePage"
import VenueDetailsPage from "../pages/VenueDetailsPage"
import AdminDashboardPage from "../apps/admin/pages/AdminDashboardPage"
import AdminUsersListPage from "../apps/admin/pages/AdminUsersListPage"
import VenueBookingsPage from "../apps/venue/pages/VenueBookingsPage"
import VenueAuthPage from "../apps/venue/pages/VenueAuthPage"
import VenueDashboardPage from "../apps/venue/pages/VenueDashboardPage"
import AdminLayout from "../layouts/AdminLayout"
import UserLayout from "../layouts/UserLayout"
import VenueLayout from "../layouts/VenueLayout"

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* <Route path="/" element={<Navigate to="/user" replace />} /> */}

        <Route path="/" element={<UserLayout />}>
          <Route index element={<HomePage />} />
          <Route path="venues" element={<ExploreVenuesPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="venue/:id" element={<VenueDetailsPage />} />
        </Route>

        <Route path="/venue" element={<VenueLayout />}>
          <Route index element={<VenueDashboardPage />} />
          <Route path="auth" element={<VenueAuthPage />} />
          <Route path="bookings" element={<VenueBookingsPage />} />
        </Route>

        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="users" element={<AdminUsersListPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
