import { fetchWithAuth } from "/Take_inputs/v2/lib/authFetch.js";
import { renderReadableResult } from "./phase5_inference_results_renderer.js";
const API_BASE = window.API_BASE;

const experimentId =
  new URLSearchParams(window.location.search).get("id") ||
  sessionStorage.getItem("experiment_id");

if (!experimentId) {
  alert("Experiment ID not found. Please reopen from dashboard.");
  throw new Error("experiment_id missing");
}

sessionStorage.setItem("experiment_id", experimentId);


function normalizeInferenceResponse(raw) {
  // Snapshot hydration shape
  if (raw.results) {
    return raw;
  }

  // Fresh inference API shape
  if (raw.result) {
    return {
      results: raw.result,
      warnings: raw.warnings || [],
    };
  }

  throw new Error("Unknown inference response shape");
}


/**
 * Phase 5 — Inference Inputs Controller
 *
 * Responsibilities:
 * - Load committed experiment configuration
 * - Render inference calculator input UI
 * - Lock committed fields
 * - Collect post-experiment observed data
 * - Call inference engine
 *
 * NON-GOALS:
 * - No insight logic
 * - No modal logic
 * - No Supabase writes
 */



/* --------------------------------------------------
   State
-------------------------------------------------- */

let experimentSnapshot = null;
let inferenceResult = null;

/* --------------------------------------------------
   Init
-------------------------------------------------- */

document.addEventListener("DOMContentLoaded", () => {
    renderInferenceInputs();   // UI renders instantly

    // ================================
    // PHASE 5 DRAFT AUTOSAVE
    // ================================
    [
      "control_n",
      "control_value",
      "control_sd",
      "test_0_n",
      "test_0_value",
      "test_0_sd"
    ].forEach(id => {
      document.addEventListener("input", e => {
        if (e.target.id !== id) return;

        localStorage.setItem(
          `phase5_draft_${experimentId}`,
          JSON.stringify({
            control_n: document.getElementById("control_n").value,
            control_value: document.getElementById("control_value").value,
            control_sd: document.getElementById("control_sd").value,
            test_0_n: document.getElementById("test_0_n").value,
            test_0_value: document.getElementById("test_0_value").value,
            test_0_sd: document.getElementById("test_0_sd").value
          })
        );
      });
    });

    hydratePhase5();           // async hydration

    const backBtn = document.getElementById("phase5-back-btn");
    if (backBtn) {
      backBtn.onclick = () => {
        sessionStorage.setItem("workflow_active", "1");
        window.location.href =
          `/Take_inputs/v2/experiments/phase4_implementation.html?id=${experimentId}`;
      };
    }
    });

    /* --------------------------------------------------
    Phase 5 — Final Decision Modal State
    -------------------------------------------------- */

    let selectedPhase5Decision = null;

    document.addEventListener("change", e => {
    if (e.target.name === "phase5Decision") {
        selectedPhase5Decision = e.target.value;

        const confirmBtn =
        document.getElementById("confirmPhase5DecisionBtn");

        if (confirmBtn) {
        confirmBtn.disabled = false;
        }
    }
    });

    document.addEventListener("click", e => {
    if (e.target.id === "confirmPhase5DecisionBtn") {
        closeDecisionModal();
        handleFinalDecisionConfirmed();
    }
    });

    async function hydratePhase5() {
      await loadExperimentSnapshot();

      //  Phase 4 decision enforcement
      if (experimentSnapshot.phase4_path !== "yes_analyze") {
        window.location.replace(
          `/Take_inputs/v2/experiments/phase4_implementation.html?id=${experimentId}`
        );
        return;
      }
      lockCommittedFields();

      //  If inference already ran, hydrate from snapshot
      if (experimentSnapshot.phase5_results) {

        console.log("=== PHASE 5 HYDRATION DIAGNOSTIC ===");
        console.log("Full snapshot:", experimentSnapshot);
        console.log("phase5_results:", experimentSnapshot.phase5_results);
        console.log("observed_data exists?", experimentSnapshot.phase5_results.observed_data);
        console.log("phase5_results KEYS:", Object.keys(experimentSnapshot.phase5_results));
        console.log("phase5_results FULL:", JSON.stringify(experimentSnapshot.phase5_results, null, 2));
        console.log("=== END DIAGNOSTIC ===");

        //  HYDRATE OBSERVED INPUT DATA (the user's entered values)
        const observedData = experimentSnapshot.phase5_results.observed_data;
        if (observedData) {
          document.getElementById("control_n").value = observedData.control.n || "";
          document.getElementById("control_value").value = observedData.control.value || "";
          document.getElementById("control_sd").value = observedData.control.sd || "";
          document.getElementById("test_0_n").value = observedData.tests[0].n || "";
          document.getElementById("test_0_value").value = observedData.tests[0].value || "";
          document.getElementById("test_0_sd").value = observedData.tests[0].sd || "";
        }

        //  FINAL DECISION ALREADY SUBMITTED — HARD LOCK
        if (experimentSnapshot.final_decision) {
            document.getElementById("results-section").style.display = "block";
            document.getElementById("completion-banner").style.display = "block";
            document.getElementById("completion-message").style.display = "block";
            document.getElementById("next-steps-section").style.display = "block";

            disableInferenceInputs();
            
            // ✅ RENDER RESULTS FOR COMPLETED EXPERIMENTS
            inferenceResult = {
              results: experimentSnapshot.phase5_results.results,
              warnings: experimentSnapshot.phase5_results.warnings || [],
              metadata: {
                alpha: experimentSnapshot.design_inputs.alpha,
                confidence: 1 - experimentSnapshot.design_inputs.alpha,
                comparisons: 1,
              },
              summary: {
                metric_type: experimentSnapshot.metric_type,
                control_value: experimentSnapshot.design_inputs?.baseline?.value ?? null,
              },
            };

            renderReadableResult(inferenceResult);
            return;
          }

          //  Results exist but experiment NOT yet finished
          inferenceResult = {
            results: experimentSnapshot.phase5_results.results,
            warnings: experimentSnapshot.phase5_results.warnings || [],
            metadata: {
              alpha: experimentSnapshot.design_inputs.alpha,
              confidence: 1 - experimentSnapshot.design_inputs.alpha,
              comparisons: 1,
            },
            summary: {
              metric_type: experimentSnapshot.metric_type,
              control_value: experimentSnapshot.design_inputs?.baseline?.value ?? null,
            },
          };

          renderReadableResult(inferenceResult);

          document.getElementById("results-section").style.display = "block";
          document.getElementById("completion-banner").style.display = "block";
          document.getElementById("finish-section").style.display = "block";

          disableInferenceInputs();
          wireFinishExperiment();
          return;
        }

      const draft = localStorage.getItem(`phase5_draft_${experimentId}`);
      if (draft && !experimentSnapshot.phase5_results) {
        const d = JSON.parse(draft);
        Object.entries(d).forEach(([k, v]) => {
          const el = document.getElementById(k);
          if (el) el.value = v;
        });
      }

      // Otherwise allow inference
      wireRunAnalysis();
    }

/* --------------------------------------------------
   Load committed experiment data
-------------------------------------------------- */

async function loadExperimentSnapshot() {
  /**
   * This must already exist from previous phases.
   * Phase 3/4 have persisted a snapshot.
   *
   * Expected shape (example):
   * {
   *   metric_type,
   *   data_relationship,
   *   tail,
   *   confidence_level,
   *   minimum_effect,
   *   variants: [{ id, is_control }]
   * }
   */
    const experimentId =
    new URLSearchParams(window.location.search).get("id") ||
    sessionStorage.getItem("experiment_id");

    if (!experimentId) {
    alert("Experiment ID not found. Please reopen this experiment from the dashboard.");
    throw new Error("experiment_id missing");
    }

    const res = await fetchWithAuth(
    `/v2/experiments/${experimentId}/snapshot/full`
    );

    experimentSnapshot = await res.json();

    if (!experimentSnapshot || !experimentSnapshot.design_inputs) {
    throw new Error("Experiment snapshot incomplete or malformed");
    }

}

/* --------------------------------------------------
   Render inference calculator input UI
-------------------------------------------------- */

function renderInferenceInputs() {
  const root = document.getElementById("phase5-inference-root");
  if (!root) return;

  root.innerHTML = getInferenceInputHTML();
}

/**
 * IMPORTANT:
 * This is a **direct clone** of the inference calculator input UI
 * with no semantic changes.
 */
function getInferenceInputHTML() {
  return `
    <div class="grid-2">

      <!-- Metric Type -->
      <div class="section">
        <h3>Metric Type</h3>

        <label>
          <input type="radio" name="metric_type" value="binary" disabled />
          Binary (conversion rate, success/failure)
        </label>

        <label>
          <input type="radio" name="metric_type" value="continuous" disabled />
          Continuous (revenue, time, score)
        </label>
      </div>

      <!-- Optional Settings -->
      <div class="section">
        <h3>Decision Thresholds</h3>

        <label>Test Direction</label>
        <select id="tail_type" disabled>
          <option value="two_sided">Two-sided (default)</option>
          <option value="one_sided">One-sided</option>
        </select>

        <label>Confidence Level (%)</label>
        <input type="number" id="confidence_level" disabled />

        <label class="optional">Minimum Worthwhile Effect (MWE)</label>
        <input type="number" id="minimum_effect" disabled />
      </div>
    </div>

    <!-- Data Relationship -->
    <div class="section" data-section="data-relationship">
      <h3>
        Data Relationship
        <span class="info-tooltip">
          ⓘ
          <span class="tooltip-card">
            <strong>Independent</strong><br>
            Different users in control and test.<br><br>
            <strong>Paired</strong><br>
            Same users measured twice.
          </span>
        </span>
      </h3>

      <div class="radio-group">
        <label>
          <input type="radio" name="data_relationship" value="independent" disabled />
          Independent
        </label>

        <label>
          <input type="radio" name="data_relationship" value="paired" disabled />
          Paired
        </label>
      </div>
    </div>

    <!-- Control Group -->
    <div class="section">
      <h3>Control Group</h3>

      <label>Sample Size (n)</label>
      <input type="number" id="control_n" />

      <label id="control_value_label">Observed Value</label>
      <input type="number" id="control_value" />

      <label class="optional">Standard Deviation (optional)</label>
      <input type="number" id="control_sd" />
    </div>

    <!-- Test Group -->
    <div class="section">
      <h3>Test Group</h3>

      <label>Sample Size (n)</label>
      <input type="number" id="test_0_n" />

      <label id="test_0_label">Observed Value</label>
      <input type="number" id="test_0_value" />

      <label class="optional">Standard Deviation (optional)</label>
      <input type="number" id="test_0_sd" />
    </div>
  `;
}

/* --------------------------------------------------
   Lock committed fields
-------------------------------------------------- */

function lockCommittedFields() {
  const design = experimentSnapshot.design_inputs;

  // Metric type radios
  document.querySelector(
    `input[name="metric_type"][value="${experimentSnapshot.metric_type}"]`
  ).checked = true;

  // Disable radios
  document
    .querySelectorAll('input[name="metric_type"]')
    .forEach(r => r.disabled = true);

  // Test direction
  const tailSelect = document.getElementById("tail_type");
  tailSelect.value =
    design.test_direction === "two_tailed" ? "two_sided" : "one_sided";
  tailSelect.disabled = true;

  // Confidence
  document.getElementById("confidence_level").value =
    Math.round((1 - design.alpha) * 100);

  // MDE
  document.getElementById("minimum_effect").value = design.target_mde;

  // Data relationship radios
  document.querySelector(
    `input[name="data_relationship"][value="${design.design_type}"]`
  ).checked = true;

  document
    .querySelectorAll('input[name="data_relationship"]')
    .forEach(r => r.disabled = true);
}

/* --------------------------------------------------
   Render test groups (observed data only)
-------------------------------------------------- */



/* --------------------------------------------------
   Run inference
-------------------------------------------------- */

function wireRunAnalysis() {
  const btn = document.getElementById("run-analysis-btn");
  if (!btn) return;

  btn.addEventListener("click", async () => {

      if (
      !document.getElementById("control_n").value ||
      !document.getElementById("control_value").value ||
      !document.getElementById("test_0_n").value ||
      !document.getElementById("test_0_value").value
    ) {
      alert("Please fill all required observed data fields before running analysis.");
      return;
    }

  

    const originalBtnText = btn.textContent;
    btn.textContent = "Analyzing…";
    btn.disabled = true;


    const payload =  buildInferencePayload();

    const experimentId =
      new URLSearchParams(window.location.search).get("id") ||
      sessionStorage.getItem("experiment_id");

    if (!experimentId) {
      alert("Experiment ID missing. Please reopen from dashboard.");
      return;
    }

    //  fire-and-forget inference (DO NOT await)
    fetchWithAuth(
      `/v2/experiments/${experimentId}/phase5/inference`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    ).catch(err => {
      console.error("Phase 5 inference failed:", err);
    });

    //  immediate UI response
    btn.textContent = "Analysis running…";
    btn.disabled = true;

    //  show next sections immediately
    document.getElementById("results-section").style.display = "block";
    document.getElementById("completion-banner").style.display = "block";
    document.getElementById("finish-section").style.display = "block";

    //  ensure finish button is wired exactly once
    wireFinishExperiment();

    //  disable inference inputs immediately
    disableInferenceInputs();

    // stop here — results will hydrate from snapshot later
    return;


  });
}

function disableInferenceInputs() {
  document
    .querySelectorAll("#phase5-inference-root input")
    .forEach(i => i.disabled = true);

  const btn = document.getElementById("run-analysis-btn");
  if (btn) btn.disabled = true;
}

/* --------------------------------------------------
   Payload builder (contract-safe)
-------------------------------------------------- */

function buildInferencePayload() {
  const control = {
    n: Number(document.getElementById("control_n").value),
    value: Number(document.getElementById("control_value").value),
    sd: document.getElementById("control_sd").value
      ? Number(document.getElementById("control_sd").value)
      : null,
  };

  const tests = [
    {
        id: "test",
        n: Number(document.getElementById("test_0_n").value),
        value: Number(document.getElementById("test_0_value").value),
        sd: document.getElementById("test_0_sd").value
        ? Number(document.getElementById("test_0_sd").value)
        : null,
    }
    ];

  const design = experimentSnapshot.design_inputs;

    return {
        metric_type: experimentSnapshot.metric_type,

        data_structure:
        design.design_type === "independent"
        ? "independent"
        : "paired",

        control,
        tests,

        settings: {
            confidence_level: 1 - design.alpha,
            minimum_effect: design.target_mde,
        },
    };
}


/* --------------------------------------------------
   Finish Experiment (Final Decision Modal)
-------------------------------------------------- */

function wireFinishExperiment() {
  const btn = document.getElementById("finish-experiment-btn");
  if (!btn) return;

  btn.onclick = () => {
    openDecisionModal();
  };
}

function handleFinalDecisionConfirmed() {
  const experimentId =
    new URLSearchParams(window.location.search).get("id") ||
    sessionStorage.getItem("experiment_id");

  const notes =
    document.getElementById("phase5Notes").value || null;

  // fire-and-forget completion
  fetchWithAuth(
    `/v2/experiments/${experimentId}/phase5/complete`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision: selectedPhase5Decision,
        notes,
      }),
    }
  ).catch(err => {
    console.error("Finish experiment failed:", err);
  });

  // instant UI update
  document.getElementById("finish-section").style.display = "none";
  document.getElementById("completion-message").style.display = "block";
  document.getElementById("next-steps-section").style.display = "block";
}


function openDecisionModal() {
  document.getElementById("phase5DecisionModal").style.display = "flex";
}

function closeDecisionModal() {
  document.getElementById("phase5DecisionModal").style.display = "none";
}