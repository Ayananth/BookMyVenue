import { useState } from "react"
import { GoogleLogin } from "@react-oauth/google"
import { motion } from "framer-motion"
import { Mail, Phone } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { loginWithGoogleVenue } from "../../../apis/auth"
import { useAuth } from "../../../contexts/AuthContext"

const methods = [
  { id: "phone", label: "Phone", icon: Phone },
  { id: "email", label: "Email", icon: Mail },
]

export default function VenueAuthPage() {
  const { login } = useAuth()
  const navigate = useNavigate();

  const [method, setMethod] = useState("phone")
  const [phone, setPhone] = useState("")
  const [email, setEmail] = useState("")
  const [googleError, setGoogleError] = useState("")
  const [googleLoading, setGoogleLoading] = useState(false)

  const handleSubmit = (event) => {
    event.preventDefault()

    if (method === "phone") {
      console.log(phone)
    } else {
      console.log(email)
    }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    const idToken = credentialResponse?.credential

    if (!idToken) {
      setGoogleError("Google sign-in did not return a token.")
      return
    }

    setGoogleLoading(true)
    setGoogleError("")

    try {
      const data = await loginWithGoogleVenue(idToken)

      login(data.access_token, data.user)

      navigate("/venue")
    } catch {
      setGoogleError("Google sign-in failed. Please try again.")
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto flex min-h-screen items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="w-full max-w-md overflow-hidden rounded-[2rem] border border-border bg-card shadow-[0_24px_60px_rgba(27,36,29,0.18)]"
        >
          <div className="p-7 sm:p-8">
            <span className="text-sm font-semibold uppercase tracking-wider text-accent">
              Venue Partner Portal
            </span>

            <h1 className="mt-2 font-serif text-3xl font-semibold tracking-tight text-foreground">
              Sign in to BookMyVenue
            </h1>

            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              Manage venues, bookings and customers from one place.
            </p>

            <div className="mt-6 flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() =>
                  setGoogleError("Google sign-in was cancelled or failed.")
                }
                theme="outline"
                size="large"
                text="continue_with"
                shape="rectangular"
                width="360"
                useOneTap={false}
              />
            </div>

            {googleLoading && (
              <p className="mt-2 text-center text-sm text-muted-foreground">
                Signing you in...
              </p>
            )}

            {googleError && (
              <p className="mt-2 text-center text-sm text-red-600">
                {googleError}
              </p>
            )}

            <div className="my-6 flex items-center gap-3">
              <span className="h-px flex-1 bg-border" />
              <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                or
              </span>
              <span className="h-px flex-1 bg-border" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {methods.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setMethod(item.id)}
                  className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-semibold transition-all ${
                    method === item.id
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-border text-muted-foreground hover:border-primary/40"
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </button>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="mt-5 space-y-4">
              {method === "phone" ? (
                <div>
                  <label
                    htmlFor="phone"
                    className="text-sm font-medium text-foreground"
                  >
                    Phone number
                  </label>

                  <input
                    id="phone"
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 9876543210"
                    className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                </div>
              ) : (
                <div>
                  <label
                    htmlFor="email"
                    className="text-sm font-medium text-foreground"
                  >
                    Email address
                  </label>

                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="owner@example.com"
                    className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                </div>
              )}

              <button
                type="submit"
                className="w-full rounded-full bg-primary px-5 py-3.5 text-sm font-semibold text-primary-foreground transition-transform hover:-translate-y-0.5"
              >
                {method === "phone"
                  ? "Continue with phone"
                  : "Continue with email"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-muted-foreground">
              New venue partner?
              <button
                type="button"
                className="ml-1 font-semibold text-primary hover:underline"
              >
                Create account
              </button>
            </p>

            <p className="mt-5 text-center text-xs leading-relaxed text-muted-foreground">
              By continuing, you agree to our Terms of Service and Privacy
              Policy.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}