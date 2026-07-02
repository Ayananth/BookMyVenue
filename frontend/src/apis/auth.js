import api from "../lib/axios"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

const authConfig = { baseURL: API_BASE_URL }

export function parseAuthError(error) {
  const data = error.response?.data
  if (!data) return "Something went wrong. Please try again."
  if (typeof data.detail === "string") return data.detail
  if (data.email) {
    return Array.isArray(data.email) ? data.email[0] : data.email
  }
  if (data.password) {
    return Array.isArray(data.password) ? data.password[0] : data.password
  }
  return "Something went wrong. Please try again."
}

export async function loginWithGoogle(idToken) {
  const { data } = await api.post(
    "/users/google",
    { token: idToken },
    authConfig,
  )
  return data
}

export async function loginWithGoogleVenue(idToken) {
  const { data } = await api.post(
    "/users/venue/google",
    { token: idToken },
    authConfig,
  )
  return data
}

export async function loginUser(credentials) {
  const { data } = await api.post("/users/login", credentials, authConfig)
  return data
}

export async function registerUser(payload) {
  const { data } = await api.post("/users/register", payload, authConfig)
  return data
}

export async function loginVenue(credentials) {
  const { data } = await api.post("/users/venue/login", credentials, authConfig)
  return data
}

export async function registerVenue(payload) {
  const { data } = await api.post("/users/venue/register", payload, authConfig)
  return data
}

export async function fetchCurrentUser() {
  const { data } = await api.get("/users/me", authConfig)
  return data
}

export async function updateCurrentUser(payload) {
  const { data } = await api.patch("/users/me", payload, authConfig)
  return data
}
