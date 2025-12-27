const outcomeType = document.getElementById("outcomeType");
const baselineValue = document.getElementById("baselineValue");
const varianceValue = document.getElementById("varianceValue");
const varianceNote = document.getElementById("varianceNote");
const outputSection = document.getElementById("outputSection");
const API_BASE = "https://pvalueproject.onrender.com";

function updateVariance() {
  if (outcomeType.value === "binary") {
    const p = parseFloat(baselineValue.value);
    if (!isNaN(p) && p > 0 && p < 1) {
      const variance = p * (1 - p);
      varianceValue.value = variance.toFixed(4);
      varianceNote.textContent = `Derived as p × (1 − p) = ${variance.toFixed(4)}`;
    } else {
      varianceValue.value = "";
      varianceNote.textContent = "Enter a valid baseline between 0 and 1";
    }
    varianceValue.disabled = true;
  } else {
    varianceValue.disabled = false;
    varianceValue.value = "";
    varianceNote.textContent = "Enter the standard deviation of the metric";
  }
}

outcomeType.addEventListener("change", updateVariance);
baselineValue.addEventListener("input", updateVariance);



/* ===============================
   MULTI-VARIANT ALLOCATION LOGIC
   =============================== */

const variantsContainer = document.getElementById("variantsContainer");
const addTreatmentBtn = document.getElementById("addTreatmentBtn");

let treatmentCount = 0;
const MAX_TREATMENTS = 5;

function createTreatmentRow() {
  if (treatmentCount >= MAX_TREATMENTS) {
    alert(`Maximum of ${MAX_TREATMENTS} treatments allowed.`);
    return;
  }

  treatmentCount++;
  const label = `Treatment ${String.fromCharCode(64 + treatmentCount)}`;

  const row = document.createElement("div");
  row.className = "variant-row";
  row.dataset.variantType = "treatment";

  row.innerHTML = `
    <span class="variant-label">${label}</span>
    <input
      type="number"
      class="allocation-input"
      value="0"
      min="0"
      max="100"
    />
    <button class="delete-btn" title="Remove treatment">✕</button>
  `;

  row.querySelector(".delete-btn").addEventListener("click", () => {
    row.remove();
    treatmentCount--;
    renumberTreatments();
  });

  variantsContainer.appendChild(row);
}

function renumberTreatments() {
  const treatmentRows = variantsContainer.querySelectorAll(
    '[data-variant-type="treatment"]'
  );

  treatmentCount = 0;

  treatmentRows.forEach((row) => {
    treatmentCount++;
    const label = `Treatment ${String.fromCharCode(64 + treatmentCount)}`;
    row.querySelector(".variant-label").textContent = label;
  });
}

function getVariantAllocations() {
  const rows = variantsContainer.querySelectorAll(".variant-row");

  const variants = [];

  rows.forEach((row, index) => {
    const label = row.querySelector(".variant-label").textContent;
    const allocation = parseFloat(
      row.querySelector(".allocation-input").value
    );

    variants.push({
      name: label,
      allocation_percent: allocation,
      is_control: index === 0
    });
  });

  return variants;
}

function validateAllocationSum() {
  const variants = getVariantAllocations();
  const total = variants.reduce(
    (sum, v) => sum + (isNaN(v.allocation_percent) ? 0 : v.allocation_percent),
    0
  );

  return total === 100;
}

/* ===============================
   HOOK INTO CALCULATE BUTTON
   =============================== */

addTreatmentBtn.addEventListener("click", createTreatmentRow);




function buildSampleSizePayload() {
  const outcomeType = document.getElementById("outcomeType").value;
  const designType = document.getElementById("designType").value;
  const baselineValue = parseFloat(
    document.getElementById("baselineValue").value
  );
  const mdeValue = parseFloat(document.getElementById("mdeValue").value);
  const varianceValue = document.getElementById("varianceValue").value;
  const alpha = parseFloat(document.getElementById("alphaValue").value);
  const power = parseFloat(document.getElementById("powerValue").value);
  const testDirection =
    document.getElementById("testDirection").value === "two"
      ? "two_tailed"
      : "one_tailed";

  const variants = getVariantAllocations();

  return {
    outcome_type: outcomeType,
    design_type: designType,
    baseline_value: baselineValue,
    mde: mdeValue,
    variance:
      outcomeType === "continuous" ? parseFloat(varianceValue) : null,
    alpha,
    power,
    test_direction: testDirection,
    variants
  };
}

/* ===============================
   OUTPUT RENDERING (LAYERED)
   =============================== */

  function renderSampleSizes(data) {
    const block = document.getElementById("sampleSizeBlock");

    const variants = data.sample_sizes.variants;
    const total = data.sample_sizes.total;

    let html = `
      <h2>Required Sample Size</h2>
      <p class="helper-text">
        Users required per variant to reliably detect the specified effect.
      </p>
      <ul>
    `;

    for (const [name, value] of Object.entries(variants)) {
      html += `
        <li>
          <strong>${name}:</strong>
          <span style="float:right">
            ${value.toLocaleString()} users
          </span>
        </li>
      `;
    }

    html += `
      </ul>
      <hr />
      <p>
        <strong>Total:</strong>
        ${total.toLocaleString()} users
      </p>
    `;

    block.innerHTML = html;
  }




  function renderSummary(data) {
    const s = data.experiment_summary || data.experiment_configuration;

    const block = document.getElementById("summaryBlock");

    block.innerHTML = `
      <h3>Experiment Configuration Used</h3>
      <ul>
        <li>Outcome type: ${s.outcome_type}</li>
        <li>Design: ${s.design}</li>
        <li>Baseline: ${s.baseline}</li>
        <li>MDE: ${s.mde}</li>
        <li>Alpha: ${s.alpha}</li>
        <li>Power: ${s.power}</li>
        <li>Test direction: ${s.test_direction}</li>
      </ul>
    `;
  }

  function renderExplanation(data) {
    const block = document.getElementById("explanationBlock");

    let html = `
      <h3>${data.explanation.headline}</h3>
      <ul>
    `;

    data.explanation.details.forEach(line => {
      html += `<li>${line}</li>`;
    });

    html += `
      </ul>
    `;

    block.innerHTML = html;
  }


  function renderSensitivity(data) {
    const block = document.getElementById("sensitivityBlock");

    const rows = data.sensitivity.mde_variants;

    let html = `
      <h3>Sensitivity: What if MDE changes?</h3>
      <table>
        <tr>
          <th>MDE</th>
          <th>Total Sample</th>
        </tr>
    `;

    rows.forEach(row => {
      html += `
        <tr>
          <td>${row.mde}</td>
          <td>${row.total_sample.toLocaleString()}</td>
        </tr>
      `;
    });

    html += `</table>`;
    block.innerHTML = html;
  }



  function renderAllocation(data) {
    if (!data.allocation_comparison) return;

    const a = data.allocation_comparison;
    const block = document.getElementById("allocationBlock");

    block.innerHTML = `
      <h3>Allocation Impact</h3>
      <p>
        <strong>Equal split (50 / 50):</strong>
        ${a.equal_split_total.toLocaleString()} users
      </p>
      <p>
        <strong>Your split (${a.current_split}):</strong>
        ${a.current_split_total.toLocaleString()} users
      </p>
    `;
  }



  function renderIntegrity(data) {
    const b = data.design_integrity;
    const block = document.getElementById("integrityBlock");

    block.innerHTML = `
      <h3>Design Integrity</h3>
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <span class="badge badge-${b.badge}">
          ${b.badge.toUpperCase()}
        </span>
        <span class="helper-text">Overall feasibility assessment</span>
      </div>
      <p>${b.reason}</p>
    `;
  }


  function renderOutput(data) {
    document.getElementById("outputSection").classList.remove("hidden");

    renderSampleSizes(data);
    renderSummary(data);
    renderExplanation(data);
    renderSensitivity(data);
    renderAllocation(data);
    renderIntegrity(data);
  }




document.getElementById("calculateBtn").addEventListener("click", async () => {
  // 1. Allocation validation
  if (!validateAllocationSum()) {
    alert("Allocation percentages must sum to exactly 100.");
    return;
  }

  // 2. Build payload
  let payload;
  try {
    payload = buildSampleSizePayload();
  } catch (e) {
    alert("Please check all inputs.");
    return;
  }

  // 3. Call backend
  try {
    const response = await fetch(`${API_BASE}/api/sample-size`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Backend error");
    }

    // 4. Render output
    renderOutput(data);

  } catch (err) {
    alert(err.message);
  }
});
