console.log("MDE JS LOADED", Math.random());
const API_BASE = "https://pvalueproject.onrender.com";


const metricType = document.getElementById("metricType");
const designType = document.getElementById("designType");
const baselineGroup = document.getElementById("baselineGroup");
const stdDevGroup = document.getElementById("stdDevGroup");
const discordanceGroup = document.getElementById("discordanceGroup");
const variantsContainer = document.getElementById("variantsContainer");
const outputSection = document.getElementById("outputSection");

let testCount = 0;
const MAX_TESTS = 5;

/* ===============================
   INPUT VISIBILITY CONTROL
   =============================== */

  function updateMetricInputs() {
    const isBinary = metricType.value === "binary";
    const isPaired = designType.value === "paired";

    const baselineInput = document.getElementById("baselineRate");

    // ----------------------------
    // Binary vs Continuous
    // ----------------------------
    baselineGroup.style.display = isBinary ? "block" : "none";
    stdDevGroup.style.display = isBinary ? "none" : "block";

    // ----------------------------
    // Paired Binary handling
    // ----------------------------
    if (isBinary && isPaired) {
      // Show discordance
      discordanceGroup.classList.remove("hidden");

      // Disable baseline rate
      baselineGroup.classList.add("input-disabled");
      baselineInput.value = "";
      baselineInput.disabled = true;

    } else {
      // Hide discordance
      discordanceGroup.classList.add("hidden");

      // Enable baseline rate
      baselineGroup.classList.remove("input-disabled");
      baselineInput.disabled = false;
    }
  }




metricType.addEventListener("change", updateMetricInputs);
designType.addEventListener("change", updateMetricInputs);

updateMetricInputs();

/* ===============================
   VARIANT HANDLING
   =============================== */

function renumberTestVariants() {
  const testRows = variantsContainer.querySelectorAll(
    '[data-type="test"]'
  );

  let index = 0;

  testRows.forEach((row) => {
    index++;
    const label = `Test ${String.fromCharCode(64 + index)}`;
    row.querySelector(".variant-label").textContent = label;
  });

  testCount = index;
}


document.getElementById("addVariantBtn").addEventListener("click", () => {
  if (testCount >= MAX_TESTS) {
    alert(`Maximum of ${MAX_TESTS} test variants allowed.`);
    return;
  }

  testCount++;
  const label = `Test ${String.fromCharCode(64 + testCount)}`;

  const row = document.createElement("div");
  row.className = "variant-row";
  row.dataset.type = "test";

  row.innerHTML = `
    <span class="variant-label">${label}</span>
    <input type="number" class="sample-input" min="1" placeholder="Users">
    <button class="delete-btn">✕</button>
  `;

  row.querySelector(".delete-btn").addEventListener("click", () => {
    row.remove();
    renumberTestVariants();
    });


  variantsContainer.appendChild(row);
});

/* ===============================
   PAYLOAD BUILDER
   =============================== */

function buildMDEPayload() {
  const rows = variantsContainer.querySelectorAll(".variant-row");

  const variants = [];
  rows.forEach((row, idx) => {
    const n = parseInt(row.querySelector("input").value);
    if (isNaN(n) || n <= 0) {
      throw new Error("All sample sizes must be positive integers.");
    }
    variants.push({
      name: row.querySelector(".variant-label").textContent,
      n,
      is_control: idx === 0
    });
  });

  return {
    metric_type: metricType.value,
    design_type: designType.value.toLowerCase(),
    baseline_rate:
      metricType.value === "binary"
        ? parseFloat(document.getElementById("baselineRate").value)
        : null,
    std_dev:
      metricType.value === "continuous"
        ? parseFloat(document.getElementById("stdDevValue").value)
        : null,
    discordance_rate:
    metricType.value === "binary" && designType.value === "paired"
    ? parseFloat(document.getElementById("discordanceRate").value)
    : null,

    alpha: parseFloat(document.getElementById("alphaValue").value),
    power: parseFloat(document.getElementById("powerValue").value),
    test_direction: document.getElementById("testDirection").value,
    variants
  };
}

/* ===============================
   OUTPUT RENDERING
   =============================== */

function renderOutput(response) {
    outputSection.classList.remove("hidden");

    const resultsHTML = response.results.map(r => {

      // ----------------------------
      // Derive experiment-specific drivers
      // ----------------------------
      const derivedDrivers = [];

      // Driver: relative MDE magnitude
      if (r.mde.value > 0.05) {
        derivedDrivers.push(
          "The minimum detectable effect is large relative to typical business impact, meaning only substantial changes would be detectable."
        );
      }

      // Driver: imbalance
      if (r.sample_sizes.control !== r.sample_sizes.test) {
        derivedDrivers.push(
          "Unequal sample sizes between control and test reduce statistical efficiency and increase the detectable threshold."
        );
      }

      // Driver: paired approximation (binary paired)
      if (r.explanation?.has_paired_approximation) {
        derivedDrivers.push(
          "This result relies on an approximate planning formula for paired binary outcomes, which increases uncertainty."
        );
      }


      // ----------------------------
      // Identify strongest improvement lever
      // ----------------------------
      let bestLever = null;

      if (Array.isArray(r.sensitivity) && r.sensitivity.length > 0) {
        bestLever = r.sensitivity.reduce((best, curr) =>
          curr.new_mde < best.new_mde ? curr : best
        );
      }

      // Require meaningful improvement (at least 10% reduction in MDE)
      if (
        bestLever &&
        bestLever.new_mde >= r.mde.value * 0.9
      ) {
        bestLever = null;
      }


    

      const verdictClass =
        r.verdict === "positive"
          ? "mde-positive"
          : r.verdict === "neutral"
          ? "mde-warning"
          : "mde-negative";
      

      const finalDrivers = derivedDrivers;


      return `
        <div class="card ${verdictClass}">
          <div class="result-header">
            <h2>${r.comparison}</h2>
            <span class="verdict-badge verdict-${r.verdict}">
              ${
                r.verdict === "positive"
                  ? "Easily detectable"
                  : r.verdict === "neutral"
                  ? "Borderline detectability"
                  : "Hard to detect"
              }
            </span>
          </div>

          <p class="decision-framing">
              ${
                r.verdict === "positive"
                  ? "This experiment design is well powered to detect meaningful improvements."
                  : r.verdict === "neutral"
                  ? "This experiment may detect moderate improvements but will likely miss smaller effects."
                  : "This experiment is unlikely to reliably detect small or moderate improvements with the current design."
              }
          </p>


          <div class="metric-grid">
            <div class="metric-card">
              <div class="metric-label">Minimum Detectable Effect</div>
              <div class="metric-value">
                ${r.mde.value}
                <span class="metric-units">
                  absolute ${metricType.value === "binary" ? "conversion rate" : "units"}
                </span>
              </div>
              <div class="metric-subtext">
                ${
                    metricType.value === "binary"
                      ? `This corresponds to an absolute change of approximately ${(r.mde.value * 100).toFixed(1)} percentage points.`
                      : "This represents the minimum average difference required between variants."
                  }

              </div>
            </div>
          </div>


          

          <div class="blind-spot-box">
            <strong>Blind spot</strong><br>
            Any real improvement smaller than the minimum detectable effect shown above is unlikely to be detected reliably by this experiment.
          </div>


          ${
            finalDrivers.length
              ? `
                <div class="drivers-title">Why this MDE is this large</div>
                <ul>
                  ${finalDrivers.map(d => `<li>${d}</li>`).join("")}
                </ul>
              `
              : `
                <div class="drivers-title">Why this MDE is this large</div>
                <p>No single design factor disproportionately increases the minimum detectable effect for this experiment.</p>
              `
          }




          <div class="output-section">
            <div class="output-title">What you can change to improve detectability</div>
              ${
                bestLever
                  ? `
                    <p class="action-recommendation">
                      The most effective way to improve detectability in this design is
                      <strong>${bestLever.name}</strong>,
                      which would reduce the minimum detectable effect to
                      <strong>${bestLever.new_mde}</strong>.
                    </p>
                  `
                  : `
                    <p class="action-recommendation">
                      Detectability can be improved by increasing sample size, improving measurement precision,
                      or adjusting traffic allocation across variants.
                    </p>
                  `
              }


            <table>
              <thead>
                <tr>
                  <th>Change</th>
                  <th>New MDE</th>
                  <th>Why this helps</th>
                </tr>
              </thead>
              <tbody>
                ${r.sensitivity.map(s => `
                  <tr>
                    <td>${s.name}</td>
                    <td>${s.new_mde}</td>
                    <td>${s.description}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>

          ${
            (() => {
              const limitations = [];

              if (r.explanation?.has_paired_approximation) {
                limitations.push(
                  "This result relies on an approximate planning formula for paired binary outcomes."
                );
              }

              return `
                <div class="explanation-box">
                  <div class="risks-title">Design limitations</div>
                  ${
                    limitations.length
                      ? `<ul>${limitations.map(l => `<li>${l}</li>`).join("")}</ul>`
                      : "No major statistical limitations were detected beyond the minimum detectable effect shown above."
                  }
                </div>
              `;
            })()
          }


        </div>

      `;
    }).join("");

    document.getElementById("mdeResultsBlock").innerHTML = `
      <div class="output-section">
        <div class="output-title">Results</div>
        ${resultsHTML}
      </div>
    `;


    // Global warnings
    
  }


/* ===============================
   API CALL
   =============================== */

document.getElementById("calculateBtn").addEventListener("click", async () => {
  let payload;
  try {
    payload = buildMDEPayload();
  } catch (e) {
    alert(e.message);
    return;
  }

  console.log("MDE PAYLOAD:", payload);

  try {
    const response = await fetch(`${API_BASE}/api/mde`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Backend error");

    renderOutput(data);

  } catch (err) {
  if (err.detail && err.detail.errors) {
    alert(err.detail.errors.join("\n"));
  } else if (typeof err.message === "string") {
    alert(err.message);
  } else {
    alert("An unexpected error occurred. Please check inputs.");
  }
}

});
