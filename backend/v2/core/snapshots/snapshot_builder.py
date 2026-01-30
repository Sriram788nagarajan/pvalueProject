from datetime import datetime, timezone
from backend.v2.core.snapshots.snapshot_phase3 import invalidate_phase3


def build_initial_snapshot(
    *,
    experiment_id,
    user_id,
    name,
    team,
    goal=None,
):
    now = datetime.now(timezone.utc)

    return {
        "experiment_id": experiment_id,
        "user_id": user_id,
        "name": name,
        "team": team,
        "goal": goal,
        "current_status": "draft",
        "current_phase": 1,
        "current_step": "create_experiment",
        "current_view": "create_experiment",
        "has_warnings": False,
        "has_override": False,
        "locked_version": None,
        "primary_metric": None,
        "metric_type": None,
        "mde": None,
        "power": None,
        "alpha": None,
        "winning_variant": None,
        "decision": None,
        "phase4_decision": None,        
        "phase4_path": None,            
        "measurement_status": None,     
        "final_decision": None,         
        "final_notes": None,            
        "created_at": now,
        "last_updated_at": now
        
    }


def apply_definition_to_snapshot(snapshot, payload, occurred_at):

    # CENTRALIZED Phase 3 invalidation
    snapshot = invalidate_phase3(snapshot)

    snapshot["definition_inputs"] = payload

    # ----------------------------
    # Apply Phase 2 definition
    # ----------------------------
    snapshot["primary_metric"] = payload["primary_metric"]["name"]
    snapshot["metric_type"] = payload["primary_metric"]["type"]

    # ----------------------------
    # Invalidate downstream state
    # ----------------------------
    snapshot["design_inputs"] = None          # Phase 3 design invalid
    snapshot["has_warnings"] = False
    snapshot["has_override"] = False
    snapshot["locked_version"] = None

    # Clear any downstream outcomes (safety)
    snapshot["decision"] = None
    snapshot["winning_variant"] = None

    # ----------------------------
    # Reset workflow position
    # ----------------------------
    snapshot["current_phase"] = 2
    snapshot["current_status"] = "defined"
    snapshot["current_view"] = "define_experiment"
    snapshot["last_updated_at"] = occurred_at

    return snapshot


#def apply_design_parameters_to_snapshot(snapshot, occurred_at):
#    snapshot["current_phase"] = 3
#    snapshot["current_status"] = "Design Input Saved"
#    snapshot["last_updated_at"] = occurred_at
#    return snapshot

def apply_design_parameters_to_snapshot(snapshot, payload, occurred_at):
    #  Invalidate Phase 3 outputs on design change
    snapshot = invalidate_phase3(snapshot)
    snapshot["current_phase"] = 3
    snapshot["current_status"] = "design_ready"
    snapshot["current_view"] = "design_parameters"

    snapshot["design_inputs"] = {
        "metric_type": payload["metric_type"],
        "design_type": payload["design_type"],
        "planned_traffic": payload["planned_traffic"],
        "baseline": payload.get("baseline"),
        "std_dev": payload.get("std_dev"),
        "target_mde": payload["target_mde"],
        "alpha": payload["alpha"],
        "power": payload["power"],
        "test_direction": payload["test_direction"],
    }

    snapshot["last_updated_at"] = occurred_at
    return snapshot




def apply_design_validation_to_snapshot(snapshot, validation, occurred_at):
    snapshot["has_warnings"] = len(validation.warnings) > 0
    snapshot["current_status"] = "design_ready" if validation.is_valid else "blocked"
    snapshot["last_updated_at"] = occurred_at
    return snapshot



def apply_design_override_to_snapshot(snapshot, occurred_at):
    snapshot["has_override"] = True
    snapshot["current_status"] = "design_ready"
    snapshot["last_updated_at"] = occurred_at
    return snapshot


def build_allocated_snapshot(*, experiment_id, user_id, allocation_source="frontend"):
    now = datetime.now(timezone.utc)

    return {
        "experiment_id": experiment_id,
        "user_id": user_id,

        "name": None,
        "team": None,
        "goal": None,

        "current_status": "allocated",
        "current_phase": 1,
        "current_step": "create_experiment",
        "current_view": "create_experiment",

        "definition_inputs": None,
        "design_inputs": None,
        "phase3_results": None,
        "phase5_results": None,

        "has_warnings": False,
        "has_override": False,
        "locked_version": None,

        "allocation_source": allocation_source,

        "created_at": now,
        "last_updated_at": now,
    }