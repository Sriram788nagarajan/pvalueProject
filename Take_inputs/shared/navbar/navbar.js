// =========================
// SHARED NAVBAR LOADER
// =========================



(async function loadNavbar() {
  const res = await fetch("/Take_inputs/shared/navbar/navbar.html");
  const html = await res.text();

  const root = document.getElementById("navbar-root");

    if (!root) {
    console.error("Navbar root not found");
    return;
    }

    root.innerHTML = html;

    /* 🔒 FIX: prevent navbar overlap */
    const navbar = root.querySelector(".home-navbar");
    
    /* commented out
    if (navbar) {
    document.body.style.paddingTop = `${navbar.offsetHeight}px`;
    }
    */

    applyNavbarRules();
    wireNavbarActions();

})();

// =========================
// PAGE CONTEXT RULES
// =========================

function applyNavbarRules() {
  const pathname = window.location.pathname;

  const isExperimentPage =
    pathname.includes("/Take_inputs/v2/experiments/");

  const createBtn = document.getElementById("nav-create-exp-btn");

  if (isExperimentPage && createBtn) {
    createBtn.remove();
  }
}

// =========================
// ACTION WIRING
// =========================

function wireNavbarActions() {
  // =========================
  // DASHBOARD
  // =========================
  document
    .querySelectorAll('#nav-dashboard-btn')
    .forEach(el =>
      el.addEventListener("click", () => {
        if (window.handleDashboardClick) {
          window.handleDashboardClick();
        } else {
          // Fallback: always works
          window.location.href = "/Take_inputs/v2/dashboard/dashboard.html";
        }
      })
    );

  // =========================
  // WORKFLOW LANDING
  // =========================
  document
    .querySelectorAll('[data-action="workflow"]')
    .forEach(el =>
      el.addEventListener("click", () => {
        window.location.href = "/ab-test-workflow/";
      })
    );

  // =========================
  // CREATE EXPERIMENT
  // =========================
  document
    .getElementById("nav-create-exp-btn")
    ?.addEventListener("click", () => {
      if (window.handleCreateExperimentClick) {
        window.handleCreateExperimentClick();
      }
    });

  // =========================
  // SCROLL LINKS
  // =========================
  document.querySelectorAll("[data-scroll]").forEach(el => {
    const target = el.dataset.scroll;
    el.addEventListener("click", () => navigateToSection(target));
  });
}

// =========================
// CROSS-PAGE NAVIGATION
// =========================

function navigateToSection(target) {
  const isHome =
    location.pathname === "/" ||
    location.pathname.endsWith("/index.html");

  if (isHome) {
    scrollWithOffset(target);
  } else {
    window.location.href = `/?scroll=${target}`;
  }
}

function scrollWithOffset(target) {
  const NAVBAR_HEIGHT = 90; // safe fixed height

  // 1) Try ID
  let el = document.getElementById(target);

  // 2) Fallback to class
  if (!el) {
    el = document.querySelector(`.${target}`);
  }

  if (!el) {
    console.warn("Scroll target not found:", target);
    return;
  }

  const y =
    el.getBoundingClientRect().top +
    window.pageYOffset -
    NAVBAR_HEIGHT;

  window.scrollTo({
    top: y,
    behavior: "smooth"
  });
}

window.addEventListener("scroll", () => {
  const nav = document.querySelector(".home-navbar");
  if (!nav) return;

  nav.classList.toggle("scrolled", window.scrollY > 4);
});