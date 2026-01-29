
(function () {
  if (window.authFetch) return; // idempotent safety

  let __cachedSession = null;

  async function getSessionFast() {
    if (__cachedSession) return __cachedSession;

    const { data } = await window.supabase.auth.getSession();
    __cachedSession = data.session;
    return __cachedSession;
  }

  window.authFetch = async function authFetch(url, options = {}) {
    const session = await getSessionFast();

    if (!session) {
      alert("Session expired. Please sign in again.");
      throw new Error("No active Supabase session");
    }

    const resolvedUrl =
      url.startsWith("http")
        ? url
        : `${window.API_BASE}${url}`;

return fetch(resolvedUrl, {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${session.access_token}`,
      },
    });
  };
})();

