import { Link, Outlet } from "react-router-dom"
import {
  LayoutDashboard,
  Building2,
  CalendarDays,
  Users,
  Settings,
} from "lucide-react"

export default function PortalLayout({ title = "Venue Owner Portal" }) {
  const menuItems = [
    {
      label: "Dashboard",
      icon: LayoutDashboard,
      path: "/venue",
    },
    {
      label: "Venues",
      icon: Building2,
      path: "/venue/venues",
    },
    {
      label: "Bookings",
      icon: CalendarDays,
      path: "/venue/bookings",
    },
    {
      label: "Customers",
      icon: Users,
      path: "/venue/customers",
    },
    {
      label: "Settings",
      icon: Settings,
      path: "/venue/settings",
    },
  ]

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-white">
        <div className="border-b p-5">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-white font-bold">
              BM
            </div>

            <div>
              <h2 className="font-semibold">BookMyVenue</h2>
              <p className="text-sm text-muted-foreground">
                Venue Owner
              </p>
            </div>
          </div>
        </div>

        <nav className="p-3">
          <div className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition hover:bg-muted"
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              )
            })}
          </div>
        </nav>
      </aside>

      {/* Right Section */}
      <div className="flex flex-1 flex-col">
        {/* Navbar */}
        <header className="sticky top-0 z-10 border-b bg-white">
          <div className="flex h-16 items-center justify-between px-6">
            <h1 className="text-lg font-semibold">{title}</h1>

            <div className="flex items-center gap-4">
              <Link
                to="/"
                className="rounded-lg border px-3 py-2 text-sm hover:bg-muted"
              >
                View Website
              </Link>

              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-white">
                A
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>

        {/* Footer */}
        <footer className="border-t bg-white px-6 py-3 text-sm text-muted-foreground">
          © 2026 BookMyVenue. All rights reserved.
        </footer>
      </div>
    </div>
  )
}