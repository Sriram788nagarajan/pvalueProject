
  console.time("PHASE3_VISIBLE");

  let __designWaitAttempts = 0;

  function hidePhase3Loading() {
    const overlay = document.getElementById("phase3-loading");
    if (overlay) {
      overlay.classList.add("hidden");
    }
  }

  const API_BASE =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://pvalueproject.onrender.com";

  let detectabilityVerdict = null;
  let sampleTimeVerdict = null;

  // IMMEDIATE SHELL RENDER (before DOMContentLoaded)
  renderShell();

  document.addEventListener("DOMContentLoaded", () => {
    bootstrapPhase3();
  });

  function bootstrapPhase3() {
    resolveSessionAsync();  // background
  }

  function renderShell() {
    const overall = document.getElementById("overall-feasibility-section");
    if (overall) {
      overall.innerHTML = `
        <div class="overall-card">
          <div class="overall-title">Overall Design Feasibility</div>
          <div class="verdict-status" style="margin-top:8px;background:#e5e7eb;color:#374151;">
            Loading…
          </div>
          <div class="overall-sub">
            Preparing experiment analysis…
          </div>
        </div>
      `;
    }

    const verdict = document.getElementById("verdict-section");
    if (verdict) {
      verdict.innerHTML =
        "<p class='metric-help'>Loading detectability analysis…</p>";
    }

    console.timeEnd("PHASE3_VISIBLE");
  }

  let __cachedSession = null;

  async function getSessionCached() {
    if (__cachedSession) return __cachedSession;

    const { data, error } = await window.supabase.auth.getSession();
    if (error || !data.session) {
      throw new Error("No session");
    }

    __cachedSession = data.session;
    return __cachedSession;
  }

  async function resolveSessionAsync() {
    try {
      //  HARD GUARD — wait until auth bootstrap is ready
      if (typeof window.authFetch !== "function" || !window.supabase) {
        setTimeout(resolveSessionAsync, 25);
        return;
      }

      await getSessionCached();

      //  defer heavy work
      (window.requestIdleCallback || function (cb) { setTimeout(cb, 0); })(() => {
        hydrateFromSnapshot();
      });

    } catch {
      window.location.href = "/index.html";
    }
  }



  // ================================
  // Phase 3 SAFE FETCH (NO SILENT FAILURES)
  // ================================
  async function phase3Fetch(url, options = {}) {
    const res = await authFetch(url, options);

    if (!res.ok) {
      let detail = "";
      try {
        const err = await res.json();
        detail = err.detail || JSON.stringify(err);
      } catch {
        detail = res.status;
      }

      console.warn("Phase 3 skipped:", url, detail);
      return null;
    }

    return res.json();
  }



  async function hydrateFromSnapshot() {
    const snapshot = await getSnapshotCached(experimentId);

    if (snapshot.locked_version !== null) {
      window.location.replace(`phase3_decision.html?id=${experimentId}`);
      return;
    }

    //  HARD GUARD — Phase 3 cannot run without design

      // ================================
      // FAST PATH — Phase 3 already computed
      // ================================
      if (
        snapshot.phase3_results &&
        snapshot.phase3_results.detectability &&
        snapshot.phase3_results.sample_time &&
        snapshot.phase3_results.decision_robustness &&
        snapshot.phase3_results.risk_disclosure
      ) {
        __snapshotCache = snapshot;
        hydratePhase3(snapshot);
        return;
      }
    
    const MAX_DESIGN_WAIT = 40; // ~2 seconds total

    if (!snapshot.design_inputs) {
      __designWaitAttempts++;

      if (__designWaitAttempts > MAX_DESIGN_WAIT) {
        throw new Error("Design commit did not materialize in time");
      }

      setTimeout(hydrateFromSnapshot, 50);
      return;
    }

    markPhase3ViewOnce(experimentId);
    hydratePhase3(snapshot);
  }





  // ================================
  // SNAPSHOT CACHE (CRITICAL FOR SPEED)
  // ================================
  let __snapshotCache = null;

  async function getSnapshotCached(experimentId) {
    //  Only cache READY snapshots
    if (__snapshotCache && __snapshotCache.design_inputs) {
      return __snapshotCache;
    }

    const res = await authFetch(
      `${API_BASE}/v2/experiments/${experimentId}/snapshot/full`
    );

    if (!res.ok) {
      throw new Error("Failed to load experiment snapshot");
    }

    const snapshot = await res.json();

    // Cache ONLY after design exists
    if (snapshot.design_inputs) {
      __snapshotCache = snapshot;
    }

    return snapshot;
  }



  // ===== Experiment context =====
  const urlParams = new URLSearchParams(window.location.search);
  const experimentId = urlParams.get("id");

  if (!experimentId) {
    alert("Experiment ID missing in URL.");
    throw new Error("experimentId not found");
  }

  // ================================
  // Back button navigation
  // ================================
  document.addEventListener("DOMContentLoaded", () => {
    const backBtn = document.getElementById("back-btn");
    if (!backBtn) return;

    backBtn.addEventListener("click", () => {
      // Go back to Design Parameters (Phase 2)
      window.location.href = `design_parameters.html?id=${experimentId}`;
    });
  });


  let phase3ViewMarked = false;

  async function markPhase3ViewOnce(experimentId) {
    if (phase3ViewMarked) return;
    phase3ViewMarked = true;

    const snapRes = await authFetch(
      `${API_BASE}/v2/experiments/${experimentId}/snapshot`
    );
    if (!snapRes.ok) return;

    const snapshot = await snapRes.json();

    // Do not overwrite after commit
    if (snapshot.locked_version !== null) return;

    await authFetch(
      `${API_BASE}/v2/experiments/${experimentId}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_view: "phase3_feasibility"
        })
      }
    );
  }


  async function hydratePhase3(snapshot) {
    const phase3Results = snapshot.phase3_results || {};
    const lockedVersion = snapshot.locked_version;
    const mwe = snapshot.design_inputs?.target_mde;

     // ==============================
    // FAST PATH — render only
    // ==============================
    if (
      snapshot.phase3_results &&
      snapshot.phase3_results.detectability &&
      snapshot.phase3_results.sample_time &&
      snapshot.phase3_results.decision_robustness &&
      snapshot.phase3_results.risk_disclosure
    ) {
      const results = snapshot.phase3_results;

      // Detectability
      if (results.detectability?.result) {
        const result = results.detectability.result;
        renderVerdict(result);
        if (mwe != null) renderMetrics(result, mwe);
        renderBaselineSensitivity(result);
        renderExplanations(result);
        detectabilityVerdict = result.computed.feasibility_verdict;
      }

      // Sample time
      if (results.sample_time?.result) {
        const result = results.sample_time.result;
        renderSampleTimeVerdict(result);
        renderSampleTimeMetrics(result);
        renderSampleTimeTable(result);
        renderSampleTimeExplanations(result);
        sampleTimeVerdict = result.computed.time_feasibility_verdict;
      }

      // Power grid
      if (results.power_grid?.result) {
        renderPowerCurve(results.power_grid.result);
      }

      // Decision robustness
      if (results.decision_robustness?.result) {
        renderDecisionRobustness(results.decision_robustness.result);
      }

      // Risk disclosure
      if (results.risk_disclosure?.result) {
        renderRiskDisclosure(results.risk_disclosure.result);
      }

      renderOverallFeasibility();
      hidePhase3Loading();
      return;
    }

    // -----------------------------
    // Phase 3 – Stage 1 (independent)
    // -----------------------------
    const stage1 = [];

    // Detectability
    stage1.push(
      (async () => {
        if (!phase3Results.detectability) {
          await phase3Fetch(
            `${API_BASE}/v2/experiments/${experimentId}/phase3/feasibility/detectability`,
            { method: "POST" }
          );
        }
      })()
    );

    // Sample time
    stage1.push(
      (async () => {
        if (!phase3Results.sample_time) {
          await phase3Fetch(
            `${API_BASE}/v2/experiments/${experimentId}/phase3/feasibility/sample-time`,
            { method: "POST" }
          );
        }
      })()
    );

    // Power grid (pure visualization)
    stage1.push(
      (async () => {
        if (!phase3Results.power_grid) {
          await phase3Fetch(
            `${API_BASE}/v2/experiments/${experimentId}/phase3/feasibility/power-grid`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                effect_values: [0.00125, 0.0025, 0.00375, 0.005, 0.00625, 0.0075, 0.01]
              })
            }
          );
        }
      })()
    );

    // Wait for detectability + sample_time to exist
    await Promise.all(stage1);

    // -----------------------------
// Phase 3 – Stage 2 (dependent)
// -----------------------------

// Decision robustness (depends on detectability)
if (!phase3Results.decision_robustness) {
  await phase3Fetch(
    `${API_BASE}/v2/experiments/${experimentId}/phase3/feasibility/decision-robustness`,
    { method: "POST" }
  );
}

// Risk disclosure (depends on detectability + sample_time)
if (!phase3Results.risk_disclosure) {
  await phase3Fetch(
    `${API_BASE}/v2/experiments/${experimentId}/phase3/feasibility/risk-disclosure`,
    { method: "POST" }
  );
}



    //  VERIFY SNAPSHOT COMPLETENESS BEFORE UNLOCKING UI
    const res = await authFetch(
      `${API_BASE}/v2/experiments/${experimentId}/snapshot/full`
    );

    if (!res.ok) {
      console.error("Failed to refetch final snapshot");
      return;
    }

    const finalSnapshot = await res.json();

    __snapshotCache = finalSnapshot;

    const requiredPillars = [
      "detectability",
      "sample_time",
      "decision_robustness",
      "risk_disclosure"
    ];

    const missing = requiredPillars.filter(
      p => !finalSnapshot.phase3_results?.[p]
    );

    if (missing.length > 0) {
      console.warn("Phase 3 incomplete, retrying in 300ms:", missing);
      setTimeout(() => hydrateFromSnapshot(), 300);
      return;
    }

// -----------------------------
// Phase 3 – Stage 3 (RENDER)
// -----------------------------
const results = finalSnapshot.phase3_results;

// Detectability
if (results.detectability?.result) {
  const result = results.detectability.result;

  renderVerdict(result);

  if (mwe != null) {
    renderMetrics(result, mwe);
  }

  renderBaselineSensitivity(result);
  renderExplanations(result);

  detectabilityVerdict = result.computed.feasibility_verdict;
}

// Sample time
if (results.sample_time?.result) {
  const result = results.sample_time.result;

  renderSampleTimeVerdict(result);
  renderSampleTimeMetrics(result);
  renderSampleTimeTable(result);
  renderSampleTimeExplanations(result);

  sampleTimeVerdict = result.computed.time_feasibility_verdict;
}

// Power grid (visual only)
if (results.power_grid?.result) {
  renderPowerCurve(results.power_grid.result);
}

// Decision robustness
if (results.decision_robustness?.result) {
  renderDecisionRobustness(results.decision_robustness.result);
}

// Risk disclosure
if (results.risk_disclosure?.result) {
  renderRiskDisclosure(results.risk_disclosure.result);
}
// -----------------------------
// Now safe to finalize UI
// -----------------------------
renderOverallFeasibility();
hidePhase3Loading();

if (lockedVersion !== null) {
  disableCommitButtons();
}

  




  }





  function renderOverallFeasibility() {
    const root = document.getElementById("overall-feasibility-section");

    // ----------------------------------
    // INCOMPLETE STATE
    // ----------------------------------
    if (detectabilityVerdict == null || sampleTimeVerdict == null) {
      root.innerHTML = `
        <div class="overall-card">
          <div class="overall-title">Overall Design Feasibility</div>
          <div class="verdict-status" style="margin-top:8px;background:#e5e7eb;color:#374151;">
            ⏳ INCOMPLETE
          </div>
          <div class="overall-sub">
            This assessment will be finalized once all feasibility checks are completed.
          </div>
        </div>
      `;
      return;
    }

    // ----------------------------------
    // COMPLETE STATES
    // ----------------------------------
    const verdicts = [detectabilityVerdict, sampleTimeVerdict];

    let statusClass;
    let label;
    let subtitle;

    if (verdicts.includes("not_feasible")) {
      statusClass = "status-not_feasible";
      label = "❌ HIGH RISK";
      subtitle =
        "One or more feasibility checks indicate that this experiment is unlikely to succeed as designed.";
    } else if (verdicts.includes("borderline")) {
      statusClass = "status-borderline";
      label = "⚠️ MODERATE RISK";
      subtitle =
        "This experiment may succeed, but some aspects of the design pose elevated risk.";
    } else {
      statusClass = "status-feasible";
      label = "✅ FEASIBLE";
      subtitle =
        "All evaluated feasibility checks indicate the experiment is well designed.";
    }

    root.innerHTML = `
    <div class="overall-card overall-${statusClass}">
      <div class="overall-title">Overall Design Feasibility</div>
      <div class="verdict-status ${statusClass}" style="margin-top:12px;">
        ${label}
      </div>
      <div class="overall-sub">
        ${subtitle}
      </div>
    </div>
    `;

      // ----------------------------------
    // SHOW DECISION BAR ONCE READY
    // ----------------------------------
    document.getElementById("phase3-decision-bar").style.display = "block";

    temporarilyDisableCommitButtons(5);
  }


  function togglePillar(pillarId, btn) {
    const el = document.getElementById(`pillar-${pillarId}`);

    if (el.style.display === "none") {
      el.style.display = "block";
      btn.innerText = "Collapse ▾";
    } else {
      el.style.display = "none";
      btn.innerText = "Expand ▸";
    }
  }







  function getExperimentId() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
  }

  async function handleAccept() {
  showModal({
    title: "Accept & Lock Experiment Design",
    message:
      "Once accepted, this experiment design will be permanently locked and cannot be edited. " +
      "You will proceed to final analysis and decision-making. Do you want to continue?",
    confirmLabel: "Accept & Lock",
    onConfirm: async () => {
      const id = getExperimentId();

      const res = await authFetch(
      `${API_BASE}/v2/experiments/${id}/phase3/commit/accept`,
      { method: "POST" }
    );

  if (!res.ok) {
    alert("Phase 3 analysis is not complete yet. Please wait.");
    return;
  }

  window.location.replace(`phase3_decision.html?id=${id}`);


    }
  });
}


async function handleBlock() {
  showModal({
    title: "Block Experiment",
    message:
      "Blocking this experiment will permanently close and archive it. " +
      "This action cannot be undone. Are you sure you want to proceed?",
    confirmLabel: "Block Experiment",
    onConfirm: async () => {
      const id = getExperimentId();

      const res = await authFetch(
        `${API_BASE}/v2/experiments/${id}/phase3/commit/block`,
        { method: "POST" }
      );

      if (!res.ok) {
        alert("Failed to block experiment. Please try again.");
        return;
      }

      window.location.replace(`phase3_decision.html?id=${id}`);
    }
  });
}


  async function handleRedesign() {
  showModal({
    title: "Redesign Experiment",
    message:
      "This will reopen the experiment in redesign mode and invalidate the current feasibility analysis. " +
      "You will be taken back to the setup flow. Continue?",
    confirmLabel: "Redesign Experiment",
    onConfirm: async () => {
      const id = getExperimentId();

      const res = await authFetch(
        `${API_BASE}/v2/experiments/${id}/phase3/commit/redesign`,
        { method: "POST" }
      );

      if (!res.ok) {
        const err = await res.json();
        showModal({
          title: "Action Not Allowed",
          message:
            err.detail ||
            "This experiment has already been finalized and cannot be modified."
        });
        disableCommitButtons();
        return;
      }

      window.location.href =
        `create_experiment.html?id=${id}&mode=redesign`;
    }
  });
}




  // ===============================
  // Minimal modal + button handling
  // ===============================

  

  function disableCommitButtons() {
    const accept = document.getElementById("btn-accept");
    const block = document.getElementById("btn-block");
    const redesign = document.getElementById("btn-redesign");

    if (accept) accept.disabled = true;
    if (block) block.disabled = true;
    if (redesign) redesign.disabled = true;
  }

  function temporarilyDisableCommitButtons(seconds = 5) {
  const accept = document.getElementById("btn-accept");
  const block = document.getElementById("btn-block");
  const redesign = document.getElementById("btn-redesign");
  const msg = document.getElementById("commit-delay-message");

  if (!accept || !block || !redesign || !msg) return;

  accept.disabled = true;
  block.disabled = true;
  redesign.disabled = true;

  let remaining = seconds;
  msg.style.display = "block";
  msg.innerText =
    `Commitment buttons will be available in ${remaining} seconds…`;

  const timer = setInterval(() => {
    remaining--;

    if (remaining === 0) {
      clearInterval(timer);
      msg.style.display = "none";
      accept.disabled = false;
      block.disabled = false;
      redesign.disabled = false;
      return;
    }

    msg.innerText =
      `Commitment buttons will be available in ${remaining} seconds…`;
  }, 1000);
}



  // ===============================
// Phase 3 Modal Controller
// ===============================

let modalConfirmCallback = null;

function showModal({ title, message, confirmLabel = "Confirm", onConfirm }) {
  const overlay = document.getElementById("modal-overlay");
  const titleEl = document.getElementById("modal-title");
  const messageEl = document.getElementById("modal-message");
  const confirmBtn = document.getElementById("modal-confirm");
  const cancelBtn = document.getElementById("modal-cancel");

  titleEl.innerText = title;
  messageEl.innerText = message;
  confirmBtn.innerText = confirmLabel;

  modalConfirmCallback = onConfirm || null;

  overlay.classList.remove("hidden");

  cancelBtn.onclick = closeModal;
  confirmBtn.onclick = () => {
  const cb = modalConfirmCallback; // capture BEFORE close
  closeModal();
  if (typeof cb === "function") {
    cb();
  }
};

}

function closeModal() {
  const overlay = document.getElementById("modal-overlay");
  overlay.classList.add("hidden");
  modalConfirmCallback = null;
}
