import { supabase } from "./supabaseClient.js";

const API_BASE =
  window.API_BASE ||
  (window.location.hostname === "localhost" ||
   window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://pvalueproject-new.onrender.com");

/**
 * Centralized authenticated fetch
 * - Attaches Supabase access token
 * - Throws if user is not logged in
 */
export async function fetchWithAuth(url, options = {}) {
  const {
    data: { session },
    error
  } = await supabase.auth.getSession();

  if (error || !session) {
    throw new Error("Not authenticated");
  }

  return fetch(`${API_BASE}${url}`, {
  ...options,
  headers: {
    ...(options.headers || {}),
    Authorization: `Bearer ${session.access_token}`,
  },
});
}

