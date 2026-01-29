// /Take_inputs/supabase_lazy.js

let _supabasePromise = null;
let _sessionCache = null;

export async function getSupabase() {
  if (!_supabasePromise) {
    _supabasePromise = import("/Take_inputs/supabase.js");
  }
  return _supabasePromise;
}

export async function getSessionLazy() {
  if (_sessionCache) return _sessionCache;

  const { supabase } = await getSupabase();
  const { data, error } = await supabase.auth.getSession();

  if (error || !data.session) {
    alert("Session expired. Please sign in again.");
    window.location.href = "/index.html";
    throw new Error("No active session");
  }

  _sessionCache = data.session;
  return _sessionCache;
}

export async function authFetch(url, options = {}) {
  const session = await getSessionLazy();

  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${session.access_token}`
    }
  });
}
