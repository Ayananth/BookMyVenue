import { Outlet } from "react-router-dom"
import PortalLayout from "../apps/portal/PortalLayout"

export default function VenueLayout() {
  return (
    <div className="app-venue">
      <PortalLayout title="Venue Portal" basePath="/venue">
        <Outlet />
      </PortalLayout>
    </div>
  )
}

