import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MapPin, Menu, User, X } from "lucide-react"

const links = [
  { label: "Explore", href: "/venues" },
  { label: "Features", href: "/#features" },
  { label: "List your venue", href: "/#owners" },
  { label: "How it works", href: "/#how" },
  { label: "Contact", href: "/#contact" },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener("scroll", onScroll)
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  return (
    <header className="fixed inset-x-0 top-0 z-50 px-4 pt-4">
      <nav
        className={`mx-auto flex max-w-6xl items-center justify-between rounded-2xl border px-4 py-3 transition-all duration-300 sm:px-6 ${
          scrolled
            ? "border-border bg-card/85 shadow-[0_8px_30px_rgba(27,36,29,0.08)] backdrop-blur-md"
            : "border-transparent bg-transparent"
        }`}
      >
        <a href="/#top" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <MapPin className="h-5 w-5" />
          </span>
          <span className="font-serif text-xl font-semibold tracking-tight text-foreground">
            BookMyVenue
          </span>
        </a>

        <ul className="hidden items-center gap-8 md:flex">
          {links.map((l) => (
            <li key={l.href}>
              <a
                href={l.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                {l.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-3 md:flex">
          <a
            href="/profile"
            className="inline-flex items-center gap-2 text-sm font-semibold text-foreground transition-colors hover:text-primary"
          >
            <User className="h-4 w-4" />
            Profile
          </a>
          <a
            href="/#owners"
            className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-transform hover:-translate-y-0.5"
          >
            Get started
          </a>
        </div>

        <button
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-border text-foreground md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mx-auto mt-2 max-w-6xl overflow-hidden rounded-2xl border border-border bg-card p-4 shadow-lg md:hidden"
          >
            <ul className="flex flex-col gap-1">
              {links.map((l) => (
                <li key={l.href}>
                  <a
                    href={l.href}
                    onClick={() => setOpen(false)}
                    className="block rounded-xl px-3 py-2.5 text-sm font-medium text-foreground hover:bg-muted"
                  >
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
            <a
              href="/profile"
              onClick={() => setOpen(false)}
              className="mt-3 block w-full rounded-xl border border-border px-5 py-3 text-center text-sm font-semibold text-foreground hover:bg-muted"
            >
              Profile
            </a>
            <a
              href="/#owners"
              onClick={() => setOpen(false)}
              className="mt-3 block rounded-full bg-primary px-5 py-3 text-center text-sm font-semibold text-primary-foreground"
            >
              Get started
            </a>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
