from typing import Dict, Any
from datetime import datetime


def apply_phase4_entry(snapshot: Dict[str, Any], occurred_at):
    """
    User enters Phase 4 (Implementation / Conclusion).
    Reversible.
    """
    snapshot["current_phase"] = 4
    snapshot["current_step"] = "phase4_entry"
    snapshot["current_view"] = "phase4"
    snapshot["last_updated_at"] = occurred_at
    return snapshot


def apply_phase4_decision_selected(
    snapshot: Dict[str, Any],
    decision: str,
    occurred_at,
):
    snapshot["current_phase"] = 4
    snapshot["current_step"] = "phase4_decision_selected"

    # Persist chosen path (reversible until finalization)
    snapshot["phase4_path"] = decision

    if decision == "no_analyze":
        snapshot["measurement_status"] = "not_requested"
    elif decision == "yes_analyze":
        snapshot["measurement_status"] = "requested"

    snapshot["last_updated_at"] = occurred_at
    return snapshot

def apply_phase4_finalization(
    snapshot: Dict[str, Any],
    *,
    final_decision: str,
    notes: str | None,
    occurred_at,
):
    """
    Terminal operation.
    After this, experiment is immutable.
    """

    snapshot["current_status"] = "completed"
    snapshot["current_phase"] = 4
    snapshot["current_step"] = "phase4_completed"

    # 🔑 Phase 4 business decision (namespaced)
    snapshot["phase4_decision"] = {
        "decision": final_decision,
        "notes": notes,
        
    }
    
    snapshot["final_decision"] = final_decision
    snapshot["final_notes"] = notes

    snapshot["last_updated_at"] = occurred_at
    return snapshot

