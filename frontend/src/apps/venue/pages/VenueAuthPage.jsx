import { useEffect, useState } from "react"
import { GoogleLogin } from "@react-oauth/google"
import { motion } from "framer-motion"
import { Mail, Phone } from "lucide-react"
import { useLocation, useNavigate } from "react-router-dom"

import {
  loginVenue,
  loginWithGoogleVenue,
  parseAuthError,
  registerVenue,
} from "../../../apis/auth"
import { useAuth } from "../../../contexts/AuthContext"

const methods = [
  { id: "email", label: "Email", icon: Mail },
  { id: "phone", label: "Phone", icon: Phone },
]

export default function VenueAuthPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [mode, setMode] = useState("login")
  const [method, setMethod] = useState("email")
  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [googleError, setGoogleError] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)

  useEffect(() => {
    if (location.state?.wrongRole) {
      setError("This account is not registered as a venue partner.")
    }
  }, [location.state])

  const redirectAfterAuth = () => {
    const from = location.state?.from?.pathname
    navigate(from && from.startsWith("/venue") ? from : "/venue", {
      replace: true,
    })
  }

  const handleEmailSubmit = async (event) => {
    event.preventDefault()
    setError("")
    setSubmitting(true)

    try {
      const payload =
        mode === "register"
          ? { email, password, full_name: fullName || undefined }
          : { email, password }

      const data =
        mode === "register"
          ? await registerVenue(payload)
          : await loginVenue(payload)

      login(data.access_token, data.user)
      redirectAfterAuth()
    } catch (err) {
      setError(parseAuthError(err))
    } finally {
      setSubmitting(false)
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
      redirectAfterAuth()
    } catch {
      setGoogleError("Google sign-in failed. Please try again.")
    } finally {
      setGoogleLoading(false)
    }
  }

  const toggleMode = () => {
    setMode((current) => (current === "login" ? "register" : "login"))
    setError("")
    setPassword("")
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
              {mode === "login" ? "Sign in to BookMyVenue" : "Create your account"}
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

            {method === "phone" ? (
              <div className="mt-5 rounded-xl border border-dashed border-border bg-muted/30 px-4 py-6 text-center text-sm text-muted-foreground">
                Phone sign-in is coming soon. Please use email for now.
              </div>
            ) : (
              <form onSubmit={handleEmailSubmit} className="mt-5 space-y-4">
                {mode === "register" && (
                  <div>
                    <label
                      htmlFor="fullName"
                      className="text-sm font-medium text-foreground"
                    >
                      Full name
                    </label>
                    <input
                      id="fullName"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Your name"
                      className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                    />
                  </div>
                )}

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
                    required
                    autoComplete="email"
                    className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                </div>

                <div>
                  <label
                    htmlFor="password"
                    className="text-sm font-medium text-foreground"
                  >
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                    minLength={8}
                    autoComplete={
                      mode === "login" ? "current-password" : "new-password"
                    }
                    className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                </div>

                {error && (
                  <p className="text-sm text-red-600" role="alert">
                    {error}
                  </p>
                )}

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full rounded-full bg-primary px-5 py-3.5 text-sm font-semibold text-primary-foreground transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting
                    ? mode === "login"
                      ? "Signing in..."
                      : "Creating account..."
                    : mode === "login"
                      ? "Sign in"
                      : "Create account"}
                </button>
              </form>
            )}

            <p className="mt-6 text-center text-sm text-muted-foreground">
              {mode === "login" ? "New venue partner?" : "Already have an account?"}
              <button
                type="button"
                onClick={toggleMode}
                className="ml-1 font-semibold text-primary hover:underline"
              >
                {mode === "login" ? "Create account" : "Sign in"}
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
