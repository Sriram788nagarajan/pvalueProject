const API_BASE =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://pvalueproject-new.onrender.com";

let DASHBOARD_CACHE = null;
window.activeTab = "all";

const DEFAULT_VISIBLE_COUNT = 5;
const expandedSections = new Set();



// Map backend status_badge to frontend category for CSS classes

function label(value) {
  if (!value) return "TBD";
  return value.replace(/_/g, " ").toUpperCase();
}

function cls(value) {
  return value.replace(/_/g, "-");
}


function renderExperimentCard(exp) {
  return `
    <div class="experiment-card ${cls(exp.overall_status)}"
         onclick="openExperiment('${exp.experiment_id}')">

      <div class="card-body">

        <div class="card-header">
          <div class="experiment-title">
            ${exp.name || "Untitled Experiment"}
          </div>

          <div class="experiment-status status-pill ${cls(exp.overall_status)}">
            ${label(exp.overall_status)}
          </div>
        </div>

        <div class="card-divider"></div>

          <div class="experiment-id">
            ID : ${exp.experiment_id}
          </div>

        <div class="experiment-details">
          <div class="detail-item">
            <span class="detail-label">Design</span>
            <span class="detail-value ${cls(exp.design_status)}">
              ${label(exp.design_status)}
            </span>
          </div>

          <div class="detail-item">
            <span class="detail-label">Measurement</span>
            <span class="detail-value ${cls(exp.measurement_status)}">
              ${label(exp.measurement_status)}
            </span>
          </div>

          <div class="detail-item">
            <span class="detail-label">Final Decision</span>
            <span class="detail-value">
              ${label(exp.final_decision)}
            </span>
          </div>
        </div>

      </div>
    </div>
  `;
}



async function loadDashboard() {
  /* const res = await fetch("http://127.0.0.1:8000/v2/experiments"); */
  /* changed this above line to below for auth*/ 
  if (!DASHBOARD_CACHE) {
  const res = await authFetch(
      `${API_BASE}/v2/dashboard`
    );

    if (!res.ok) {
      console.error("Failed to load experiments");
      return;
    }

    DASHBOARD_CACHE = await res.json();
  }

  const data = DASHBOARD_CACHE;
  const emptyCard = document.getElementById("dashboard-empty-card");

  const list = document.getElementById("experiments-list");
  list.innerHTML = "";

  if (data.experiments.length === 0) {
    
    emptyCard.classList.remove("hidden");
    return;
    }

    
    emptyCard.classList.add("hidden");

  const experiments = data.experiments;

  // =========================
  // SIDEBAR DATA
  // =========================

  const total = experiments.length;

  const blockedCount = experiments.filter(
    e => e.overall_status === "blocked"
  ).length;

  const completedCount = experiments.filter(
    e => e.overall_status === "completed"
  ).length;

  const inProgressCount = experiments.filter(
    e => e.overall_status === "in_progress"
  ).length;

  // Counts
  document.getElementById("count-total").textContent = total;
  document.getElementById("count-in-progress").textContent = inProgressCount;
  document.getElementById("count-completed").textContent = completedCount;
  document.getElementById("count-blocked").textContent = blockedCount;

  
 


    const processedExperiments = experiments.map(e => ({
    ...e,
    created_at_fmt: new Date(e.created_at).toLocaleDateString()
  }));



  // ---------- TAB FILTER ----------
  let visible;

  if (window.activeTab === "all") {
    visible = processedExperiments;
  }

  if (window.activeTab === "in_progress") {
    visible = processedExperiments.filter(
      e => e.overall_status === "in_progress"
    );
  }

  if (window.activeTab === "completed") {
    visible = processedExperiments.filter(
      e => e.overall_status === "completed"
    );
  }

  if (window.activeTab === "blocked") {
    visible = processedExperiments.filter(
      e => e.overall_status === "blocked"
    );
  }
  // ---------- RENDER ----------
  

  const BATCH_SIZE = 6;
  let index = 0;

  function renderBatch() {
    const slice = visible.slice(index, index + BATCH_SIZE);
    if (slice.length === 0) return;

    

    const html = slice.map(renderExperimentCard).join("");
    list.insertAdjacentHTML("beforeend", html);

    index += BATCH_SIZE;
    requestAnimationFrame(renderBatch);
  }

  renderBatch();
}

document.addEventListener("DOMContentLoaded", loadDashboard);

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    

    document.querySelectorAll(".tab-btn").forEach(b =>
      b.classList.remove("active")
    );

    btn.classList.add("active");
    window.activeTab = btn.dataset.tab;
    loadDashboard();
  }); 
});


window.openExperiment = async function (experimentId) {
  try {
    document.body.style.cursor = 'wait';
    
    const res = await authFetch(
        `${API_BASE}/v2/orchestration/enter/${experimentId}`
      );

    if (!res.ok) {
      document.body.style.cursor = 'default';
      console.error("Failed to enter experiment via orchestration");
      return;
    }

    const data = await res.json();
    const { resolved_view } = data;

    sessionStorage.setItem("workflow_active", "1");

    window.location.replace(
      `/Take_inputs/v2/experiments/${resolved_view}.html?id=${experimentId}`
    );
  } catch (err) {
    document.body.style.cursor = 'default';
    console.error("Orchestration entry failed:", err);
  }
};
