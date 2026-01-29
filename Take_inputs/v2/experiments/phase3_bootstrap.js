import "/Take_inputs/supabase.js";

let __cachedSession = null;

async function getSessionCached() {
  if (__cachedSession) return __cachedSession;

  const { data, error } = await window.supabase.auth.getSession();
  if (error || !data.session) {
    alert("Session expired. Please sign in again.");
    window.location.href = "/index.html";
    throw new Error("No session");
  }

  __cachedSession = data.session;
  return __cachedSession;
}

window.authFetch = async function authFetch(url, options = {}) {
  const session = await getSessionCached();

  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${session.access_token}`
    }
  });
};
