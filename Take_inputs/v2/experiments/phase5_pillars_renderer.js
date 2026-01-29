/**
 * Phase 5 — Insight Pillars Renderer
 * Rules:
 * - Render only if content exists
 * - Max 4 pillars
 * - Read-only
 */

export function renderPillars({ inferenceResult, snapshot }) {
  const container = document.getElementById("pillars-container");
  if (!container) return;

  container.innerHTML = "";

  const pillars = [];

  const p1 = buildCommitmentAlignment(inferenceResult, snapshot);
  if (p1) pillars.push(p1);

  const p2 = buildDecisionConfidence(inferenceResult);
  if (p2) pillars.push(p2);

  const p3 = buildRiskCallout(inferenceResult, snapshot);
  if (p3) pillars.push(p3);

  const p4 = buildLearningSummary(inferenceResult);
  if (p4) pillars.push(p4);

  pillars.slice(0, 4).forEach(p => container.appendChild(p));
}

/* -----------------------------
   Pillar builders (EMPTY for now)
----------------------------- */

function buildCommitmentAlignment(inferenceResult, snapshot) {
  if (!inferenceResult || !inferenceResult.results || inferenceResult.results.length === 0) {
    return null;
  }

  const r = inferenceResult.results[0];

  // Phase 3 commitment decision
  const commitment = snapshot?.decision; // "accepted", "blocked", or null

  if (!commitment) return null;

  let message;

  if (commitment === "accepted" && r.significant && r.lift_absolute > 0) {
    message = "Final results support the original decision to proceed.";
  } else if (commitment === "accepted" && !r.significant) {
    message = "Final results did not provide strong evidence for the original decision.";
  } else if (commitment === "blocked" && r.significant && r.lift_absolute > 0) {
    message = "Final results contradict the original decision to block.";
  } else if (commitment === "blocked" && !r.significant) {
    message = "Final results reinforce the decision to block.";
  } else {
    message = "Final results are directionally inconsistent with the original decision.";
  }

  return createPillar(
    "Commitment Alignment",
    `<p>${message}</p>`
  );
}

function buildDecisionConfidence(inferenceResult) {
  if (!inferenceResult || !inferenceResult.results || inferenceResult.results.length === 0) {
    return null;
  }

  const r = inferenceResult.results[0];

  if (typeof r.p_value !== "number" || !r.confidence_interval) {
    return null;
  }

  const alpha = 0.05; // canonical alpha (confidence already committed earlier)

  const distanceFromAlpha = Math.abs(alpha - r.p_value);
  const ciWidth = Math.abs(r.confidence_interval[1] - r.confidence_interval[0]);

  let message;

  if (r.significant && distanceFromAlpha > 0.03) {
    message = "The result is decisively significant with strong separation from the decision threshold.";
  } else if (r.significant && distanceFromAlpha <= 0.03) {
    message = "The result is statistically significant but close to the decision boundary.";
  } else if (!r.significant && distanceFromAlpha <= 0.03) {
    message = "The result is inconclusive and close to the decision threshold.";
  } else {
    message = "The result is clearly non-significant with low decision confidence.";
  }

  return createPillar(
    "Decision Confidence",
    `<p>${message}</p>`
  );
}

function buildRiskCallout(inferenceResult, snapshot) {
  if (!inferenceResult || !inferenceResult.results || inferenceResult.results.length === 0) {
    return null;
  }

  const r = inferenceResult.results[0];

  // Require Phase 3 feasibility context
  const phase3 = snapshot?.phase3_results;
  if (!phase3) return null;

  const detectability = phase3.detectability?.result;
  const sampleTime = phase3.sample_time?.result;

  let message = null;

  // Case 1: Statistically significant, but Phase 3 said "not feasible"
  if (
    r.significant &&
    detectability?.computed?.feasibility_verdict === "not_feasible"
  ) {
    message =
      "Although statistically significant, this result comes from a design previously flagged as underpowered, increasing false-positive risk.";
  }

  // Case 2: Non-significant AND Phase 3 warned about excessive duration / power
  if (
    !r.significant &&
    sampleTime?.computed?.time_feasibility_verdict === "not_feasible"
  ) {
    message =
      "The inconclusive result is consistent with earlier feasibility risks around insufficient sample size or duration.";
  }

  // Case 3: Effect barely clears MWE
  if (
    r.significant &&
    Math.abs(r.lift_absolute) <
      (snapshot?.design_inputs?.target_mde || 0)
  ) {
    message =
      "The detected effect is statistically significant but close to the minimum worthwhile threshold, making it sensitive to noise.";
  }

  if (!message) return null;

  return createPillar(
    "Risk Callout",
    `<p>${message}</p>`
  );
}

function buildLearningSummary(inferenceResult) {
  if (!inferenceResult || !inferenceResult.results || inferenceResult.results.length === 0) {
    return null;
  }

  const r = inferenceResult.results[0];

  let message = null;

  // Case 1: Clear positive signal
  if (r.significant && r.lift_absolute > 0) {
    message =
      "This experiment demonstrates that the tested change can produce measurable positive impact under real conditions.";
  }

  // Case 2: Clear negative signal
  if (r.significant && r.lift_absolute < 0) {
    message =
      "This experiment reveals that the tested change negatively affects the primary metric, warranting avoidance or redesign.";
  }

  // Case 3: Inconclusive outcome
  if (!r.significant) {
    message =
      "This experiment suggests that the tested change does not produce a reliably measurable impact at the current scale.";
  }

  if (!message) return null;

  return createPillar(
    "Learning Summary",
    `<p>${message}</p>`
  );
}

/* -----------------------------
   UI helper
----------------------------- */

function createPillar(title, bodyHTML) {
  const div = document.createElement("div");
  div.className = "pillar-card";
  div.innerHTML = `<h4>${title}</h4>${bodyHTML}`;
  return div;
}