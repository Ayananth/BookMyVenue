import { useState } from "react"
import { motion } from "framer-motion"
import { Mail, Phone, MapPin, Send, CheckCircle2 } from "lucide-react"
import Reveal from "../common/Reveal"

const info = [
  { icon: Mail, label: "Email us", value: "hello@bookmyvenue.com" },
  { icon: Phone, label: "Call us", value: "+1 (415) 555-0192" },
  { icon: MapPin, label: "Visit us", value: "500 Market St, San Francisco, CA" },
]

export default function Contact() {
  const [role, setRole] = useState("guest")
  const [sent, setSent] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    setSent(true)
    setTimeout(() => setSent(false), 4000)
  }

  return (
    <section id="contact" className="px-4 py-24">
      <div className="mx-auto grid max-w-6xl gap-12 lg:grid-cols-[0.85fr_1.15fr]">
        <Reveal>
          <span className="text-sm font-semibold uppercase tracking-wider text-accent">
            Get in touch
          </span>
          <h2 className="mt-3 font-serif text-4xl font-semibold tracking-tight text-foreground text-balance sm:text-5xl">
            Let&apos;s plan something memorable
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            Questions about booking a space or listing your venue? Our team
            replies within one business day.
          </p>

          <div className="mt-10 space-y-4">
            {info.map((c) => (
              <div
                key={c.label}
                className="flex items-center gap-4 rounded-2xl border border-border bg-card p-5"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <c.icon className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-sm text-muted-foreground">{c.label}</p>
                  <p className="font-semibold text-foreground">{c.value}</p>
                </div>
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <form
            onSubmit={handleSubmit}
            className="rounded-[2rem] border border-border bg-card p-7 shadow-[0_18px_50px_rgba(27,36,29,0.08)] sm:p-9"
          >
            <p className="text-sm font-medium text-foreground">I am a…</p>
            <div className="mt-3 grid grid-cols-2 gap-3">
              {[
                { id: "guest", label: "Looking for a venue" },
                { id: "owner", label: "Venue owner" },
              ].map((r) => (
                <button
                  type="button"
                  key={r.id}
                  onClick={() => setRole(r.id)}
                  className={`rounded-xl border px-4 py-3 text-sm font-semibold transition-all ${
                    role === r.id
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-border text-muted-foreground hover:border-primary/40"
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <Field label="Full name" placeholder="Jordan Rivera" />
              <Field label="Email" type="email" placeholder="you@email.com" />
            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label="Phone" placeholder="+1 (___) ___-____" />
              <Field
                label={role === "owner" ? "Venue name" : "City"}
                placeholder={role === "owner" ? "Aurora Banquet Hall" : "San Francisco"}
              />
            </div>

            <div className="mt-4">
              <label className="text-sm font-medium text-foreground">
                Message
              </label>
              <textarea
                rows={4}
                placeholder={
                  role === "owner"
                    ? "Tell us about your space, capacity, and location…"
                    : "Tell us about your event, date, and guest count…"
                }
                className="mt-1.5 w-full resize-none rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/20"
              />
            </div>

            <motion.button
              type="submit"
              whileTap={{ scale: 0.98 }}
              className="mt-6 flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
            >
              {sent ? (
                <>
                  <CheckCircle2 className="h-4 w-4" /> Message sent!
                </>
              ) : (
                <>
                  {role === "owner" ? "Register my venue" : "Send message"}
                  <Send className="h-4 w-4" />
                </>
              )}
            </motion.button>
          </form>
        </Reveal>
      </div>
    </section>
  )
}

function Field({ label, type = "text", placeholder }) {
  return (
    <div>
      <label className="text-sm font-medium text-foreground">{label}</label>
      <input
        type={type}
        placeholder={placeholder}
        className="mt-1.5 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/20"
      />
    </div>
  )
}
