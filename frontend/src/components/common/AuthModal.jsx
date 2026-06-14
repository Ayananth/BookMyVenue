import { useEffect, useState } from "react"
import { GoogleLogin } from "@react-oauth/google"
import { motion, AnimatePresence } from "framer-motion"
import { Mail, Phone, X } from "lucide-react"
import { loginWithGoogle } from "../../apis/auth"
import { useAuth } from "../../contexts/AuthContext"

const methods = [
  { id: "phone", label: "Phone", icon: Phone },
  { id: "email", label: "Email", icon: Mail },
]

export default function AuthModal({ open, onClose }) {
  const { login } = useAuth()
  const [method, setMethod] = useState("phone")
  const [phone, setPhone] = useState("")
  const [email, setEmail] = useState("")
  const [googleError, setGoogleError] = useState("")
  const [googleLoading, setGoogleLoading] = useState(false)

  useEffect(() => {
    if (!open) return undefined

    const onKeyDown = (event) => {
      if (event.key === "Escape") onClose()
    }

    document.body.style.overflow = "hidden"
    window.addEventListener("keydown", onKeyDown)

    return () => {
      document.body.style.overflow = ""
      window.removeEventListener("keydown", onKeyDown)
    }
  }, [open, onClose])

  useEffect(() => {
    if (!open) {
      setGoogleError("")
      setGoogleLoading(false)
    }
  }, [open])

  const handleSubmit = (event) => {
    event.preventDefault()
    onClose()
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
      const data = await loginWithGoogle(idToken)
      login(data.access_token, data.user)
      onClose()
    } catch {
      setGoogleError("Google sign-in failed. Please try again.")
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <motion.button
            type="button"
            aria-label="Close sign in dialog"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 bg-foreground/40 backdrop-blur-sm"
            onClick={onClose}
          />

          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="auth-modal-title"
            initial={{ opacity: 0, scale: 0.96, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 12 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="relative w-full max-w-md overflow-hidden rounded-[2rem] border border-border bg-card shadow-[0_24px_60px_rgba(27,36,29,0.18)]"
          >
            <button
              type="button"
              onClick={onClose}
              className="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-xl border border-border text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>

            <div className="p-7 sm:p-8">
              <span className="text-sm font-semibold uppercase tracking-wider text-accent">
                Welcome back
              </span>
              <h2
                id="auth-modal-title"
                className="mt-2 font-serif text-3xl font-semibold tracking-tight text-foreground"
              >
                Sign in to BookMyVenue
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                Choose how you&apos;d like to continue.
              </p>

              <div className="mt-6 flex w-full justify-center">
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
                      htmlFor="auth-phone"
                      className="text-sm font-medium text-foreground"
                    >
                      Phone number
                    </label>
                    <input
                      id="auth-phone"
                      type="tel"
                      value={phone}
                      onChange={(event) => setPhone(event.target.value)}
                      placeholder="+1 (555) 000-0000"
                      className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      autoComplete="tel"
                    />
                  </div>
                ) : (
                  <div>
                    <label
                      htmlFor="auth-email"
                      className="text-sm font-medium text-foreground"
                    >
                      Email address
                    </label>
                    <input
                      id="auth-email"
                      type="email"
                      value={email}
                      onChange={(event) => setEmail(event.target.value)}
                      placeholder="you@example.com"
                      className="mt-2 w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      autoComplete="email"
                    />
                  </div>
                )}

                <button
                  type="submit"
                  className="w-full rounded-full bg-primary px-5 py-3.5 text-sm font-semibold text-primary-foreground transition-transform hover:-translate-y-0.5"
                >
                  {method === "phone" ? "Continue with phone" : "Continue with email"}
                </button>
              </form>

              <p className="mt-5 text-center text-xs leading-relaxed text-muted-foreground">
                By continuing, you agree to our Terms of Service and Privacy Policy.
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
