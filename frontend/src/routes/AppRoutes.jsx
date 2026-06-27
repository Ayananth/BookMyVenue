import { BrowserRouter, Route, Routes } from "react-router-dom"
import ExploreVenuesPage from "../pages/ExploreVenuesPage"
import HomePage from "../pages/HomePage"
import ProfilePage from "../pages/ProfilePage"
import VenueDetailsPage from "../pages/VenueDetailsPage"
import AdminDashboardPage from "../apps/admin/pages/AdminDashboardPage"
import AdminUsersListPage from "../apps/admin/pages/AdminUsersListPage"
import VenueBookingsPage from "../apps/venue/pages/VenueBookingsPage"
import VenueAuthPage from "../apps/venue/pages/VenueAuthPage"
import VenueDashboardPage from "../apps/venue/pages/VenueDashboardPage"
import VenueListPage from "@/apps/venue/pages/VenueListPage"
import AddVenuePage from "@/apps/venue/pages/AddVenuePage"
import AdminLayout from "../layouts/AdminLayout"
import UserLayout from "../layouts/UserLayout"
import VenueLayout from "../layouts/VenueLayout"
import { GuestRoute, ProtectedRoute } from "./ProtectedRoute"

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UserLayout />}>
          <Route index element={<HomePage />} />
          <Route path="venues" element={<ExploreVenuesPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="venue/:slug" element={<VenueDetailsPage />} />
        </Route>

        <Route
          path="/venue/auth"
          element={
            <GuestRoute allowedRole="venue" redirectTo="/venue">
              <VenueAuthPage />
            </GuestRoute>
          }
        />

        <Route
          path="/venue"
          element={
            <ProtectedRoute requiredRole="venue" loginPath="/venue/auth">
              <VenueLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<VenueDashboardPage />} />
          <Route path="bookings" element={<VenueBookingsPage />} />
          <Route path="venues" element={<VenueListPage />} />
          <Route path="venues/add" element={<AddVenuePage />} />
        </Route>

        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="users" element={<AdminUsersListPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
