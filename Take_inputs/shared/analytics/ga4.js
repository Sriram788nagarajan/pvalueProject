// ==================================================
// GA4 SHARED INITIALIZATION
// ==================================================

(function () {
  if (window.__GA4_INITIALIZED__) return;
  window.__GA4_INITIALIZED__ = true;

  // Create dataLayer if missing
  window.dataLayer = window.dataLayer || [];

  // Define gtag safely
  window.gtag = function () {
    window.dataLayer.push(arguments);
  };

  // Init timestamp
  gtag('js', new Date());

  // Enable debug only on localhost
  const isLocalhost =
    location.hostname === "localhost" ||
    location.hostname === "127.0.0.1";

  gtag('config', 'G-0S008YMM6L', {
    debug_mode: isLocalhost
  });
})();