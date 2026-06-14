import api from "../lib/axios"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

export async function loginWithGoogle(idToken) {
  const { data } = await api.post(
    "/users/google",
    { token: idToken },
    { baseURL: API_BASE_URL },
  )
  return data
}

export async function fetchCurrentUser() {
  const { data } = await api.get("/users/me", { baseURL: API_BASE_URL })
  return data
}
