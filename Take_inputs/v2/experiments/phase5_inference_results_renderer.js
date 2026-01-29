// inference_results_renderer.js
// Extracted verbatim from inference.html
// DO NOT MODIFY LOGIC unless statistical behavior is intentionally changed

export function renderReadableResult(apiResult) {
  if (!apiResult || !apiResult.results || apiResult.results.length === 0) {
    document.getElementById("readable-results").style.display = "block";
    document.getElementById("rr-verdict").innerText =
      "⚠️ No statistical result could be computed.";
    document.getElementById("rr-summary").innerText =
      "The provided inputs did not allow a valid statistical test.";
    document.getElementById("rr-action").innerText =
      "Check inputs or collect more data before rerunning the analysis.";
    return;
  }

  if (apiResult.results.length === 1) {
    renderSingleVariantResult(apiResult);
  } else {
    renderMultiVariantResults(apiResult);
  }
}

function applyBannerState({ lift, significant }) {
  const banner = document.getElementById("result-banner");

  banner.classList.remove("banner-green", "banner-red", "banner-amber");

  if (lift > 0 && significant) {
    banner.classList.add("banner-green");
  } else if (lift < 0 && significant) {
    banner.classList.add("banner-red");
  } else {
    banner.classList.add("banner-amber");
  }
}



function renderSingleVariantResult(apiResult) {
  const r = apiResult.results[0];
  const metricType = apiResult.summary.metric_type;
  const isBinary = metricType === "binary";

  const lift = r.lift_absolute;
  const relativeLift = r.lift_relative;
  const control = apiResult.summary.control_value;
  const confidence = 1 - apiResult.metadata.alpha;

  const impactList = document.getElementById("rr-impact");
  const confidenceTextEl = document.getElementById("rr-confidence");

  if (r.test_used === "unsupported_paired_binary") {
    document.getElementById("rr-verdict").innerText =
      "⚠️ Paired analysis not available for conversion rates";

    document.getElementById("rr-summary").innerText = r.interpretation;

    impactList.innerHTML = "";
    confidenceTextEl.innerText = "";

    document.getElementById("rr-action").innerText =
      "Use Independent data or switch to a continuous metric.";

    document.getElementById("readable-results").style.display = "block";
    return;
  }

  document.getElementById("readable-results").style.display = "block";

  // ---------- Verdict ----------
  let verdict;
  if (r.significant && r.lift_absolute > 0) {
    verdict = "✅ Statistically Significant Improvement";
  } else if (r.significant && r.lift_absolute < 0) {
    verdict = "⚠️ Statistically Significant Decline";
  } else if (!r.significant && r.lift_absolute > 0) {
    verdict = "❌ Inconclusive (Positive Trend, Not Proven)";
  } else {
    verdict = "➖ No Meaningful Change Detected";
  }

  const verdictEl = document.getElementById("rr-verdict");
  verdictEl.innerText = verdict;

  applyBannerState({
    lift: r.lift_absolute,
    significant: r.significant
  });

  verdictEl.classList.remove(
    "verdict-win",
    "verdict-loss",
    "verdict-inconclusive",
    "verdict-neutral"
  );

  if (r.significant && r.lift_absolute > 0) {
    verdictEl.classList.add("verdict-win");
  } else if (r.significant && r.lift_absolute < 0) {
    verdictEl.classList.add("verdict-loss");
  } else if (!r.significant && r.lift_absolute > 0) {
    verdictEl.classList.add("verdict-inconclusive");
  } else {
    verdictEl.classList.add("verdict-neutral");
  }

  // ---------- Summary ----------
  document.getElementById("rr-summary").innerText = isBinary
    ? `Observed lift: ${(lift * 100).toFixed(2)} percentage points at ${(confidence * 100).toFixed(0)}% confidence.`
    : `Observed lift: ${lift.toFixed(2)} units at ${(confidence * 100).toFixed(0)}% confidence.`;

  // ---------- Business Impact ----------
  impactList.innerHTML = isBinary
    ? `
      <li>Control conversion: ${(control * 100).toFixed(2)}%</li>
      <li>Absolute lift: ${(lift * 100).toFixed(2)}%</li>
      <li>Relative lift: ${(relativeLift * 100).toFixed(1)}%</li>
    `
    : `
      <li>Control mean: ${control.toFixed(2)}</li>
      <li>Absolute lift: ${lift.toFixed(2)} units</li>
      ${relativeLift !== null
        ? `<li>Relative lift: ${(relativeLift * 100).toFixed(1)}%</li>`
        : ""}
    `;

  // ---------- Confidence ----------
  const ciLow = r.confidence_interval[0];
  const ciHigh = r.confidence_interval[1];

  let confidenceText = isBinary
    ? `The true effect is likely between ${(ciLow * 100).toFixed(2)}% and ${(ciHigh * 100).toFixed(2)}%.`
    : `The true effect is likely between ${ciLow.toFixed(2)} and ${ciHigh.toFixed(2)} units.`;

  if (ciLow <= 0 && ciHigh >= 0) {
    confidenceText += " Zero is within this range, so no effect is still plausible.";
  }

  confidenceTextEl.innerText = confidenceText;

  // ---------- Recommended Action ----------
  let action;
  if (r.significant && r.lift_absolute > 0) {
    action = "Roll out the test variant.";
  } else if (r.significant && r.lift_absolute < 0) {
    action = "Stop the test and revert to control.";
  } else if (!r.significant && r.lift_absolute > 0) {
    action = "Run the experiment longer or collect more data.";
  } else {
    action = "Stop the experiment; impact appears minimal.";
  }

  const actionEl = document.getElementById("rr-action");
  actionEl.innerText = action;

  actionEl.classList.remove(
    "action-positive",
    "action-neutral",
    "action-negative"
  );

  if (r.significant && r.lift_absolute > 0) {
    actionEl.classList.add("action-positive");
  } else if (r.significant && r.lift_absolute < 0) {
    actionEl.classList.add("action-negative");
  } else {
    actionEl.classList.add("action-neutral");
  }

  // ---------- Statistical Details ----------
  document.getElementById("rr-test-used").innerText =
    r.test_used.replaceAll("_", " ");

  document.getElementById("rr-statistic").innerText =
    r.statistic.toFixed(3);

  const pValueEl = document.getElementById("rr-pvalue");
  const isBelowAlpha = r.p_value < apiResult.metadata.alpha;

  pValueEl.innerHTML = `
    ${r.p_value.toFixed(4)}
    <span class="stat-pill ${isBelowAlpha ? "green" : "red"}">
      ${isBelowAlpha ? "below α" : "above α"}
    </span>
  `;

  document.getElementById("rr-alpha").innerText =
    apiResult.metadata.alpha.toFixed(2);

  const significantEl = document.getElementById("rr-significant");

  significantEl.innerHTML = r.significant
    ? `
      <span class="significance yes">
        <span class="significance-icon">✓</span>
        Yes
      </span>
    `
    : `
      <span class="significance no">
        <span class="significance-icon">✕</span>
        No
      </span>
    `

  document.getElementById("rr-ci").innerText = isBinary
    ? `${(ciLow * 100).toFixed(2)}% to ${(ciHigh * 100).toFixed(2)}%`
    : `${ciLow.toFixed(2)} to ${ciHigh.toFixed(2)}`;

  document.getElementById("rr-comparisons").innerText =
    apiResult.metadata.comparisons;

  document.getElementById("rr-raw-json").innerText =
    JSON.stringify(apiResult, null, 2);
}

function formatTestGroupName(testId) {
  const parts = testId.split("_");
  return `Test Group ${parts[1]}`;
}

function renderMultiVariantResults(apiResult) {
  const results = apiResult.results;
  const isBinary = apiResult.summary.metric_type === "binary";
  const container = document.getElementById("readable-results");

  container.style.display = "block";
  const confidence = 1 - apiResult.metadata.alpha;

  // ---------- Winner selection ----------
  const winners = results.filter(
    r => r.significant && r.lift_absolute > 0
  );

  let winner = null;
  if (winners.length > 0) {
    winner = winners.reduce((best, cur) =>
      cur.lift_absolute > best.lift_absolute ? cur : best
    );
  }

  // ---------- Verdict ----------
  const verdictEl = document.getElementById("rr-verdict");
  verdictEl.className = "";

  if (winner) {
    verdictEl.innerText = "✅ Statistically Significant Improvement";
    verdictEl.classList.add("verdict-win");
  } else {
    verdictEl.innerText = "➖ No Variant Beats Control";
    verdictEl.classList.add("verdict-neutral");
  }

  // ---------- Summary ----------
  document.getElementById("rr-summary").innerText =
    `Multiple variants were tested against control at ${(confidence * 100).toFixed(0)}% confidence.`;

  // ---------- Business Impact ----------
  const impactList = document.getElementById("rr-impact");
  impactList.innerHTML = "";

  results.forEach(r => {
    const isWinner = winner && r.test_id === winner.test_id;

    impactList.innerHTML += `
      <li style="
        padding:10px 12px;
        margin-bottom:8px;
        border-left:5px solid ${isWinner ? "#10b981" : "#cbd5e1"};
        background:${isWinner ? "#ecfdf5" : "#f8fafc"};
        border-radius:6px;
      ">
        <strong>${formatTestGroupName(r.test_id)}</strong>
        ${isWinner ? " 🏆 WINNER" : ""}
        <br/>
        Lift: ${(r.lift_absolute * 100).toFixed(2)}%
        <br/>
        P-value: ${r.p_value.toFixed(4)}
        <br/>
        ${r.significant ? "Statistically significant" : "Not significant"}
      </li>
    `;
  });

  // ---------- Confidence ----------
  const confidenceEl = document.getElementById("rr-confidence");

  if (winner) {
    const [ciLow, ciHigh] = winner.confidence_interval;
    confidenceEl.innerText = isBinary
      ? `The winning variant’s true effect is likely between ${(ciLow * 100).toFixed(2)}% and ${(ciHigh * 100).toFixed(2)}%.`
      : `The winning variant’s true effect is likely between ${ciLow.toFixed(2)} and ${ciHigh.toFixed(2)} units.`;
  } else {
    confidenceEl.innerText =
      "None of the variants show a statistically reliable improvement over control.";
  }

  // ---------- Recommended Action ----------
  const actionEl = document.getElementById("rr-action");
  actionEl.className = "";

  if (winner) {
    actionEl.innerText =
      `Roll out ${formatTestGroupName(winner.test_id)}. It shows the highest statistically significant improvement (${(winner.lift_absolute * 100).toFixed(2)}% lift).`;
    actionEl.classList.add("action-positive");
  } else {
    actionEl.innerText =
      "Do not roll out any variant. Continue experimentation or collect more data.";
    actionEl.classList.add("action-neutral");
  }

  // ---------- Statistical Details ----------
  const r = winner || results[0];

  document.getElementById("rr-test-used").innerText =
    r.test_used.replaceAll("_", " ");

  document.getElementById("rr-statistic").innerText =
    r.statistic.toFixed(3);

  const pValueEl = document.getElementById("rr-pvalue");
  const isBelowAlpha = r.p_value < apiResult.metadata.alpha;

  pValueEl.innerHTML = `
    ${r.p_value.toFixed(4)}
    <span class="stat-pill ${isBelowAlpha ? "green" : "red"}">
      ${isBelowAlpha ? "below α" : "above α"}
    </span>
  `;

  document.getElementById("rr-alpha").innerText =
    apiResult.metadata.alpha.toFixed(2);

  const significantEl = document.getElementById("rr-significant");

  significantEl.innerHTML = r.significant
    ? `
      <span class="significance yes">
        <span class="significance-icon">✓</span>
        Yes
      </span>
    `
    : `
      <span class="significance no">
        <span class="significance-icon">✕</span>
        No
      </span>
    `;

  document.getElementById("rr-ci").innerText = isBinary
    ? `${(r.confidence_interval[0] * 100).toFixed(2)}% to ${(r.confidence_interval[1] * 100).toFixed(2)}%`
    : `${r.confidence_interval[0].toFixed(2)} to ${r.confidence_interval[1].toFixed(2)}`;

  document.getElementById("rr-comparisons").innerText =
    apiResult.metadata.comparisons;

  document.getElementById("rr-raw-json").innerText =
    JSON.stringify(apiResult, null, 2);
}
