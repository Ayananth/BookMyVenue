import { Link } from "react-router-dom"

export default function PortalLayout({ title, basePath, children }) {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-10 border-b border-border/60 bg-background/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="grid size-9 place-items-center rounded-xl bg-primary text-primary-foreground">
              BM
            </div>
            <div>
              <div className="text-sm text-muted-foreground">BookMyVenue</div>
              <div className="text-base font-semibold">{title}</div>
            </div>
          </div>

          <nav className="flex items-center gap-3 text-sm">
            <Link className="rounded-lg px-3 py-2 hover:bg-muted" to={basePath || "/"}>
              Dashboard
            </Link>
            <Link className="rounded-lg px-3 py-2 hover:bg-muted" to="/user">
              User site
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
    </div>
  )
}

