
/* Detectability / Power pillar */

function renderVerdict(result) {
  const verdict = result.computed.feasibility_verdict;

let statusClass;
if (verdict === "feasible") {
    statusClass = "status-feasible";
  } else if (verdict === "borderline") {
    statusClass = "status-borderline";
  } else if (verdict === "not_feasible") {
    statusClass = "status-not_feasible";
  } else {
    statusClass = "";
  }


  const root = document.getElementById("verdict-section");
  root.innerHTML = `
    <div class="verdict-card">
      <h2>Detectability Verdict</h2>
      <div class="verdict-status ${statusClass}">
        ${verdict === "feasible"
          ? "FEASIBLE"
          : verdict === "borderline"
          ? "BORDERLINE FEASIBLE"
          : "NOT FEASIBLE"}
      </div>
      <p class="metric-help" style="margin-top:12px;">
        ${verdict === "feasible"
          ? "This design is capable of reliably detecting the minimum effect that matters to your business."
          : verdict === "borderline"
          ? "This design may detect meaningful effects, but there is a non-trivial risk of inconclusive results."
          : "This design is unlikely to reliably detect the minimum effect that matters to your business."}

      </p>
    </div>
  `;


}


function renderMetrics(result, mwe) {
  const root = document.getElementById("metrics-section");

  const mdePct = (result.computed.statistical_mde * 100).toFixed(2);
  const powerPct = (
    result.computed.power_at_minimum_worthwhile_effect * 100
  ).toFixed(1);
  const mwePct = mwe ? (mwe * 100).toFixed(2) : "–";

  root.innerHTML = `
    <h2>Key Detectability Metrics</h2>
    <div class="metric-grid">

      <div class="metric-card">
        <div class="metric-label">Minimum Detectable Effect</div>
        <div class="metric-value">${mdePct}%</div>
        <div class="metric-help">
          Smallest effect this design can detect with the specified confidence and power.
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Minimum Worthwhile Effect</div>
        <div class="metric-value">${mwePct}%</div>
        <div class="metric-help">
          Effect size you indicated is meaningful for business or design decisions.
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Power at Business Threshold</div>
        <div class="metric-value">${powerPct}%</div>
        <div class="metric-help">
          Probability of detecting the minimum worthwhile effect if it truly exists.
        </div>
      </div>

    </div>
  `;
}

function renderExplanations(result) {
  const root = document.getElementById("explanations-section");

  let items = result.explanations
  .map(e => `<li>${e}</li>`)
  .join("");



  const baselineNote = `
    <li>
      The Baseline sensitivity table shows how detectability would change if the true conversion rate
      were roughly <strong>20% higher or lower</strong> than the value you entered.
      This helps assess how dependent the experiment outcome is on the accuracy of
      your baseline estimate. Large changes across these scenarios indicate a fragile design.
    </li>
  `;

  root.innerHTML = `
    <h2>What this means for your experiment</h2>
    <ul class="explanation-list">
      ${items}
      ${baselineNote}
    </ul>
  `;
}

function renderBaselineSensitivity(result) {
  const data = result.computed.baseline_sensitivity;
  if (!data || data.length === 0) return;

  const rows = data.map(d => `
    <tr>
      <td>${d.scenario.replace(/_/g, " ")}</td>
      <td>${(d.assumed_baseline * 100).toFixed(2)}%</td>
      <td>${(d.power_at_mwe * 100).toFixed(1)}%</td>
      <td>${d.verdict.replace("_", " ")}</td>
    </tr>
  `).join("");

  const root = document.getElementById("baseline-sensitivity-section");

  root.innerHTML = `
    <h2>Baseline Sensitivity</h2>
    <p class="metric-help">
      How detectability changes if the true baseline is moderately higher or lower
      than expected.
    </p>

    <table>
      <thead>
        <tr>
          <th>Scenario</th>
          <th>Assumed baseline</th>
          <th>Power at business effect</th>
          <th>Verdict</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>

    <div class="disclaimer">
      Sensitivity is evaluated assuming the true baseline could be
      ~20% higher or lower than estimated.
    </div>
  `;
}


function renderPowerCurve(data) {
  const root = document.getElementById("power-curve-section");

  // Transform data
 const grid = data?.computed?.grid ?? data?.grid;
  if (!grid || grid.length === 0) return;

  const points = grid.map(d => ({
    x: d.effect * 100,
    y: d.power * 100
  }));

  const width = 700;
  const height = 320;
  const padding = 50;

  const maxX = Math.max(...points.map(p => p.x));
  const maxY = 100;

  const xScale = x => padding + (x / maxX) * (width - padding * 2);
  const yScale = y => height - padding - (y / maxY) * (height - padding * 2);

  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${xScale(p.x)} ${yScale(p.y)}`)
    .join(" ");

  root.innerHTML = `
    <h2>Power vs Effect Size</h2>

    <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;">
      <!-- Axes -->
      <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="#94a3b8" />
      <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="#94a3b8" />

      <!-- Y-axis labels -->
      ${[0, 20, 40, 60, 80, 100].map(v => `
        <text x="${padding - 10}" y="${yScale(v) + 4}" text-anchor="end" font-size="12" fill="#475569">${v}%</text>
        <line x1="${padding}" y1="${yScale(v)}" x2="${width - padding}" y2="${yScale(v)}" stroke="#e2e8f0" />
      `).join("")}

      <!-- X-axis labels -->
      ${points.map(p => `
        <text x="${xScale(p.x)}" y="${height - padding + 18}" text-anchor="middle" font-size="12" fill="#475569">${p.x.toFixed(2)}%</text>
      `).join("")}

      <!-- Curve -->
      <path d="${path}" fill="none" stroke="#2563eb" stroke-width="2" />

      <!-- Points -->
      ${points.map(p => `
        <circle cx="${xScale(p.x)}" cy="${yScale(p.y)}" r="4" fill="#2563eb" />
      `).join("")}

      <!-- Axis titles -->
      <text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="13" fill="#475569">Effect size (percentage points)</text>
      <text x="14" y="${height / 2}" transform="rotate(-90 14 ${height / 2})" text-anchor="middle" font-size="13" fill="#475569">Power</text>
    </svg>

    <div class="disclaimer">
      Power values are computed using a normal-approximation around the design MDE and are intended for visualization only.
    </div>
  `;
}



/* Sample & Time pillar */

function renderSampleTimeVerdict(result) {
  const verdict = result.computed.time_feasibility_verdict;

  let statusClass;
  if (verdict === "feasible") {
    statusClass = "status-feasible";
  } else if (verdict === "borderline") {
    statusClass = "status-borderline";
  } else {
    statusClass = "status-not_feasible";
  }

  document.getElementById("sample-time-verdict-section").innerHTML = `
    <div class="verdict-card">
      <h2>Sample & Time Verdict</h2>
      <div class="verdict-status ${statusClass}">
        ${verdict === "feasible"
          ? "FEASIBLE"
          : verdict === "borderline"
          ? "BORDERLINE"
          : "NOT FEASIBLE"}
      </div>
      <p class="metric-help" style="margin-top:12px;">
        ${verdict === "feasible"
          ? "This experiment is expected to reach the required sample size within the planned duration."
          : verdict === "borderline"
          ? "This experiment may complete, but is likely to take longer than planned."
          : "This experiment is unlikely to reach the required sample size in a reasonable timeframe."}
      </p>
    </div>
  `;
  

}


function renderSampleTimeMetrics(result) {
  const c = result.computed;

  const dailyTrafficItems = Object.entries(c.planned_sample_per_variant || {})
  .map(([variant, total]) => {
    const daily = (total / c.duration_days).toFixed(1);
    return `<li><strong>${variant}:</strong> ~${daily} users/day</li>`;
  })
  .join("");


  document.getElementById("sample-time-metrics-section").innerHTML = `
    <h2>Key Sample & Time Metrics</h2>

    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">Required Total Sample</div>
        <div class="metric-value">
          ${Object.values(c.required_sample_per_variant || {}).reduce((a, b) => a + b, 0)}
        </div>
        <div class="metric-help">
          Total number of users required to detect the minimum worthwhile effect.
        </div>
      </div>


      <div class="metric-card">
        <div class="metric-label">Planned Total Sample</div>
        <div class="metric-value">
          ${Object.values(c.planned_sample_per_variant || {}).reduce((a, b) => a + b, 0)}
        </div>
        <div class="metric-help">
          Users expected based on the current traffic plan.
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Estimated Time to Completion</div>
        <div class="metric-value">${c.time_to_completion_days} days</div>
        <div class="metric-help">
          Time required to reach the required sample size.
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Derived Daily Traffic (users per day per variant)</div>
        <ul class="metric-help" style="margin-top:8px;">
          ${dailyTrafficItems}
        </ul>
      </div>

    </div>
  `;
}


function renderSampleTimeTable(result) {
  const planned = result.computed.planned_sample_per_variant;
  const required = result.computed.required_sample_per_variant;
  const time = result.computed.time_per_variant_days;

  const rows = Object.keys(planned).map(v => `
    <tr>
      <td>${v}</td>
      <td>${planned[v]}</td>
      <td>${required[v]}</td>
      <td>${time[v]}</td>
    </tr>
  `).join("");

  document.getElementById("sample-time-table-section").innerHTML = `
    <h2>Time to Sample by Variant</h2>

    <table>
      <thead>
        <tr>
          <th>Variant</th>
          <th>Planned Sample</th>
          <th>Required Sample</th>
          <th>Estimated Days</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>

    <div class="disclaimer">
      Time estimates assume traffic remains stable throughout the experiment.
    </div>
  `;
}


function renderSampleTimeExplanations(result) {
  const items = result.explanations
    .map(e => `<li>${e}</li>`)
    .join("");

  document.getElementById("sample-time-explanations-section").innerHTML = `
    <h2>What this means for sample & timing</h2>
    <ul class="explanation-list">
      ${items}
    </ul>
  `;
}


/* Decision Robustness */

function renderDecisionRobustness(result) {
  const verdict = result.verdict;
  const ratio = result.computed.decision_separation_ratio;
  const powerPct = (result.computed.power_at_minimum_worthwhile_effect * 100).toFixed(1);

  let statusClass;
  let label;
  let description;

  if (verdict === "robust_decision") {
    statusClass = "status-feasible";
    label = "ROBUST DECISION EXPECTED";
    description =
      "This experiment is likely to produce results that clearly support a confident decision.";
  } else if (verdict === "fragile_decision") {
    statusClass = "status-borderline";
    label = "FRAGILE DECISION SIGNAL";
    description =
      "This experiment is likely to produce results close to your decision threshold, making it harder to confidently decide whether to act.";
  } else {
    statusClass = "status-not_feasible";
    label = "WEAK DECISION SIGNAL";
    description =
      "This experiment is unlikely to produce results that clearly support a business decision.";
  }

  // ----------------------------
  // VERDICT CARD
  // ----------------------------
  document.getElementById("decision-robustness-verdict").innerHTML = `
    <div class="verdict-card">
      <h2>Decision Robustness Verdict</h2>
      <div class="verdict-status ${statusClass}">
        ${label}
      </div>
      <p class="metric-help" style="margin-top:12px;">
        ${description}
      </p>
    </div>
  `;

  // ----------------------------
  // WHY THIS IS FRAGILE / ROBUST
  // ----------------------------
  const whyText = `
    <li>
      The smallest effect this experiment can reliably detect is
      <strong>${ratio.toFixed(2)}×</strong> your minimum worthwhile effect.
    </li>
    <li>
      Power at your business threshold is approximately <strong>${powerPct}%</strong>.
    </li>
  `;

  document.getElementById("decision-robustness-risks").innerHTML = `
    <h2>Why this decision may be unclear</h2>
    <ul class="explanation-list">
      ${whyText}
    </ul>
  `;

  // ----------------------------
  // ACTIONABLE GUIDANCE
  // ----------------------------
  const actions =
    result.recommended_actions.length > 0
      ? result.recommended_actions.map(a => `<li>${a}</li>`).join("")
      : `
        <li>Increase sample size or experiment duration to create clearer separation.</li>
        <li>Increase the minimum worthwhile effect if only larger wins matter.</li>
        <li>Consider a one-sided test if only improvement matters.</li>
      `;

  document.getElementById("decision-robustness-guidance").innerHTML = `
    <h2>How to improve decision clarity</h2>
    <ul class="explanation-list">
      ${actions}
    </ul>
  `;
}


/* Risk Disclosure */

function renderRiskDisclosure(result) {

  // ----------------------------
  // Explicit Assumptions
  // ----------------------------
  const assumptions = result.explicit_assumptions.length
    ? result.explicit_assumptions.map(a => `
        <li>
          ${a.statement}
          <span class="disclaimer">(Source: ${a.source})</span>
        </li>
      `).join("")
    : "<li>No explicit assumptions identified.</li>";

  document.getElementById("risk-assumptions").innerHTML = `
    <h2>Explicit Assumptions</h2>
    <ul class="explanation-list">
      ${assumptions}
    </ul>
  `;

  // ----------------------------
  // Approximations
  // ----------------------------
  const approximations = result.approximations.length
    ? result.approximations.map(a => `
        <li>
          <strong>${a.statement}</strong><br />
          <span class="metric-help">${a.impact}</span>
        </li>
      `).join("")
    : "<li>No material approximations disclosed.</li>";

  document.getElementById("risk-approximations").innerHTML = `
    <h2>Statistical Approximations Used</h2>
    <ul class="explanation-list">
      ${approximations}
    </ul>
  `;

  // ----------------------------
  // Known Fragilities
  // ----------------------------
  const fragilities = result.known_fragilities.length
    ? result.known_fragilities.map(f => `
        <li>
          ${f.statement}
          <span class="disclaimer">(Source: ${f.source})</span>
        </li>
      `).join("")
    : "<li>No major fragilities identified for this design.</li>";

  document.getElementById("risk-fragilities").innerHTML = `
    <h2>Known Design Fragilities</h2>
    <ul class="explanation-list">
      ${fragilities}
    </ul>
  `;

  // ----------------------------
  // Invalidation Conditions
  // ----------------------------
  const invalidations = result.invalidation_conditions.length
    ? result.invalidation_conditions.map(i => `
        <li>
          ${i.statement}
          <span class="disclaimer">(Source: ${i.source})</span>
        </li>
      `).join("")
    : "<li>No explicit invalidation conditions defined.</li>";

  document.getElementById("risk-invalidations").innerHTML = `
    <h2>What Would Invalidate These Conclusions</h2>
    <ul class="explanation-list">
      ${invalidations}
    </ul>
  `;
}