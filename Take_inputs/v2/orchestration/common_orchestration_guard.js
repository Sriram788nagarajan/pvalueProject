// authFetch is globally available via window (loaded by script tag in HTML)
import { showEntryToast } from "./entry_toast.js";

const API_BASE =
  window.API_BASE ||
  (window.location.hostname === "localhost" ||
   window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://pvalueproject.onrender.com");


export async function enforceOrchestration(expectedView) {
  const params = new URLSearchParams(window.location.search);
  const experimentId = params.get("id");

  console.log("=".repeat(80));
  console.log(" ORCHESTRATION DEBUG");
  console.log("=".repeat(80));
  console.log("Expected view:", expectedView);
  console.log("Experiment ID:", experimentId);

  // New experiment flow → do nothing
  if (!experimentId) {
    console.log("No experiment ID - skipping orchestration");
    return;
  }

  //  Check if user is already inside workflow
  const isInternalNavigation = sessionStorage.getItem("workflow_active");
  console.log("workflow_active flag:", isInternalNavigation);
 

  if (isInternalNavigation) {
    console.log(" Internal navigation detected - SKIPPING orchestration");
    console.log("=".repeat(80));
    return;
  }

  console.log(" External entry detected - ENFORCING orchestration");

  //  External entry (dashboard/direct URL) → enforce orchestration
  let data;
  try {
    const res = await window.authFetch(
        `${API_BASE}/v2/orchestration/enter/${experimentId}`
      );

    if (!res.ok) return;
    data = await res.json();
  } catch {
    return;
  }

  const { resolved_view, entry_context } = data;
  console.log("Backend resolved view:", resolved_view);
  console.log("Current page:", expectedView);

  //  Wrong page → force canonical page
  if (resolved_view !== expectedView) {
    console.log("⚠️ MISMATCH - Redirecting to:", resolved_view);
    console.log("Setting workflow_active flag BEFORE redirect");
    
    // Mark as inside workflow before redirect
    sessionStorage.setItem("workflow_active", "1");
    
    console.log("workflow_active after set:", sessionStorage.getItem("workflow_active"));
    console.log("=".repeat(80));
    
    window.location.replace(
      `/Take_inputs/v2/experiments/${resolved_view}.html?id=${experimentId}`
    );
    return;
  }

  console.log("✅ MATCH - Allowing page load");
  console.log("Setting workflow_active flag");
  
  //  Correct page → mark as inside workflow and show toast
  sessionStorage.setItem("workflow_active", "1");
  
  console.log("workflow_active after set:", sessionStorage.getItem("workflow_active"));
  console.log("=".repeat(80));
  
  showEntryToast(entry_context);
}