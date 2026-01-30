print(">>> LOADING experiments.py FROM:", __file__)

import uuid

from fastapi import APIRouter, HTTPException,Depends

from backend.v2.models.experiment import CreateExperimentRequest
from backend.v2.core.events.event_factory import build_experiment_created_event
from backend.v2.core.snapshots.snapshot_builder import build_initial_snapshot
from backend.v2.core.events.event_repository import insert_event
from backend.v2.core.snapshots.snapshot_repository import insert_snapshot
from backend.v2.db.connection import get_connection

from backend.v2.models.definition import DefinitionSavedRequest
from backend.v2.core.events.event_validators import validate_definition
from backend.v2.core.events.event_factory import build_definition_saved_event
from backend.v2.core.snapshots.snapshot_builder import apply_definition_to_snapshot

from backend.v2.models.design import DesignParametersRequest, DesignOverrideRequest
from backend.v2.core.design.design_validator import validate_design_feasibility


from backend.v2.core.events.event_factory import (
    build_design_parameters_saved_event,
    build_design_validated_event,
    build_design_override_accepted_event,
)

from backend.v2.core.snapshots.snapshot_builder import (
    apply_design_parameters_to_snapshot,
    apply_design_validation_to_snapshot,
    apply_design_override_to_snapshot,
)

#from backend.v2.models.phase3_feasibility import Phase3DetectabilityRequest
from backend.v2.core.phase3_feasibility.detectability import (
    validate_detectability_feasibility,
)

from backend.v2.core.events.event_factory import (
    build_phase3_detectability_evaluated_event,
)
from backend.v2.core.events.event_repository import insert_event
from backend.v2.models.phase3_feasibility import Phase3PowerGridRequest
from backend.v2.core.phase3_feasibility.power_grid import compute_power_grid

from backend.v2.core.phase3_feasibility.sample_time import (
    validate_sample_time_feasibility,
)
from backend.v2.core.events.event_factory import (
    build_phase3_sample_time_evaluated_event,
)

from backend.v2.db.connection import get_connection

from backend.v2.core.phase3_feasibility.decision_robustness import (
    validate_decision_robustness,
)

from backend.v2.core.events.event_factory import (
    build_phase3_decision_robustness_evaluated_event,
)

from backend.v2.core.events.event_factory import (
    build_phase3_risk_disclosure_evaluated_event
)

from backend.v2.core.events.event_factory import (
    build_phase3_design_accepted_event,
    build_phase3_design_blocked_event,
    build_phase3_design_redesign_requested_event,
)

from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot
from backend.v2.core.snapshots.snapshot_phase3 import persist_phase3_result
from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot

from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional

from backend.v2.auth.dependencies import get_current_user
from backend.v2.auth.utils import get_user_id_from_jwt
from backend.v2.auth.guards import require_experiment_owner,forbid_if_completed

from uuid import UUID

from backend.v2.core.phase4_implementation import phase4
from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot
from backend.v2.core.events.event_repository import insert_event
from backend.api.models import Phase3InferenceRequest
# ============================
# Phase 3 State Machine Rules
# ============================

PHASE3_ALLOWED_TRANSITIONS = {
    "phase3_complete": {"accept", "block", "redesign"},
    "redesign_requested": set(),  # flow restarts, no further actions allowed
    "running": set(),             # terminal
    "blocked": set(),             # terminal
}

def _build_phase5_observed_data(payload: dict) -> dict:
    """
    Extracts ONLY user-entered observed data from Phase 5 payload.
    Locked design inputs must never be touched here.
    """

    return {
        "control": {
            "n": payload["control"]["n"],
            "value": payload["control"]["value"],
            "sd": payload["control"].get("sd"),
        },
        "tests": [
            {
                "id": t.get("id"),
                "n": t["n"],
                "value": t["value"],
                "sd": t.get("sd"),
            }
            for t in payload.get("tests", [])
        ],
    }




def require_phase3_action_allowed(snapshot: dict, action: str):
    #  HARD GUARANTEE: Phase 3 must be complete
    if snapshot.get("current_status") != "phase3_complete":
        raise HTTPException(
            status_code=400,
            detail="Phase 3 analysis is not complete yet"
        )
    
    status = snapshot.get("current_status")

    allowed = PHASE3_ALLOWED_TRANSITIONS.get(status)
    if allowed is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown experiment status '{status}'"
        )

    if action not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Action '{action}' not allowed from status '{status}'"
        )



def apply_commitment_to_snapshot(snapshot: dict, new_status: str, occurred_at):
    snapshot["current_status"] = new_status
    snapshot["design_committed_at"] = occurred_at

    # ----------------------------
    # 🔑 Canonical Phase 3 decision
    # ----------------------------
    if new_status == "running":
        snapshot["decision"] = "accepted"
    elif new_status == "blocked":
        snapshot["decision"] = "blocked"

    # Commit is final
    if new_status in {"running", "blocked"}:
        snapshot["locked_version"] = 1
        snapshot["current_phase"] = 3
        snapshot["current_step"] = "phase3_decision"

    # Redesign resets flow
    if new_status == "redesign_requested":
        snapshot["locked_version"] = None
        snapshot["decision"] = None
        snapshot["current_phase"] = 1
        snapshot["current_step"] = "create_experiment"

    snapshot["last_updated_at"] = datetime.now(timezone.utc)
    return snapshot








router = APIRouter(prefix="/v2/experiments", tags=["experiments"])


#abcd
@router.post("/")
def create_experiment(request: CreateExperimentRequest, current_user = Depends(get_current_user),):
    print(">>> HANDLER:", __name__, "FUNCTION:", create_experiment)
    print(">>> HANDLER: create_experiment ENTERED")  
     

    user_id = get_user_id_from_jwt(current_user)   
         
    experiment_id = request.experiment_id

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id

    existing = get_snapshot_by_experiment_id(experiment_id)

    if existing:
        require_experiment_owner(existing, user_id)

        updated = False

        if request.name is not None and existing.get("name") is None:
            existing["name"] = request.name
            updated = True

        if request.team is not None and existing.get("team") is None:
            existing["team"] = request.team
            updated = True

        if request.goal is not None and existing.get("goal") is None:
            existing["goal"] = request.goal
            updated = True

        if updated:
            #  Enforce Phase 1 invariants
            existing["current_phase"] = 1
            existing["current_step"] = "create_experiment"
            existing["current_status"] = "metadata_created"

            #  REQUIRED for dashboard_experiments NOT NULL constraint
            existing["current_view"] = "create_experiment"

            existing["last_updated_at"] = datetime.now(timezone.utc)
            upsert_snapshot(existing)

        return {
            "experiment_id": experiment_id,
            "snapshot": existing,
        }

    event = build_experiment_created_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload=request.model_dump(mode="json"),    
    )

    snapshot = build_initial_snapshot(
        experiment_id=experiment_id,
        user_id=user_id,
        name=request.name,
        team=request.team,
        goal=request.goal,
    )
    
    snapshot["current_phase"] = 1
    snapshot["current_step"] = "create_experiment"
    snapshot["current_status"] = "metadata_created"

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                print(">>> CALLING insert_snapshot")
                insert_snapshot(snapshot)
                print(">>> insert_snapshot COMPLETE")
                print(">>> CALLING insert_event")
                insert_event(event)
                print(">>> insert_event COMPLETE")
            conn.commit()
    except Exception as e:
        print(">>> EXCEPTION TYPE:", type(e)) 
        print(">>> EXCEPTION MESSAGE:", str(e))         
        print(">>> EXCEPTION DETAILS:", repr(e))        
        import traceback
        print(">>> TRACEBACK:")                         
        traceback.print_exc()   
        raise HTTPException(status_code=500, detail=str(e))
         
        
    assert experiment_id is not None, "experiment_id must never be None"

    return {
        "experiment_id": experiment_id,
        "snapshot": snapshot,
    }


class ExperimentMetadataUpdate(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    goal: Optional[str] = None


@router.patch("/{experiment_id}")
def update_experiment_metadata(
    experiment_id: uuid.UUID,
    payload: ExperimentMetadataUpdate,
    current_user = Depends(get_current_user),
):
    from backend.v2.core.snapshots.snapshot_reader import (
        get_snapshot_by_experiment_id,
    )

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    # Prevent edits after Phase 3 commit
    if snapshot.get("locked_version") is not None:
        raise HTTPException(
            status_code=400,
            detail="Experiment is locked and cannot be edited",
        )

    if payload.name is not None:
        snapshot["name"] = payload.name

    if payload.team is not None:
        snapshot["team"] = payload.team

    if payload.goal is not None:
        snapshot["goal"] = payload.goal

    snapshot["last_updated_at"] = datetime.now(timezone.utc)

    upsert_snapshot(snapshot)
    return snapshot



class DefinitionDraftUpdate(BaseModel):
    definition_inputs: dict





@router.post("/{experiment_id}/definition")
def save_definition(experiment_id: uuid.UUID,
                    request: DefinitionSavedRequest,
                    current_user = Depends(get_current_user)):
    print(">>> HANDLER:", __name__, "FUNCTION:", create_experiment)
    
    user_id = get_user_id_from_jwt(current_user)

    payload = request.dict()
    validate_definition(payload)

    # 1) Fetch existing snapshot
    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    # ----------------------------
    # HARD GUARD: Phase 1 metadata must exist
    # ----------------------------
    if snapshot.get("name") is None:
        raise HTTPException(
            status_code=409,
            detail="Experiment metadata not saved yet. Please complete Phase 1."
        )

    # Optional guard (future): prevent edits after lock
    if snapshot.get("locked_version") is not None:
        raise HTTPException(status_code=400, detail="Experiment design is locked")
    
    if snapshot.get("current_step") != "create_experiment":
        raise HTTPException(
            status_code=400,
            detail="Definition can only be saved once from Create Experiment"
        )

    # 2) Build event
    event = build_definition_saved_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload=payload
    )

    # 3) Apply snapshot delta
    snapshot = apply_definition_to_snapshot(
        snapshot=snapshot,
        payload=payload,
        occurred_at=event["occurred_at"]
        )


    # ---- NEW STATE MACHINE ENFORCEMENT ----


    snapshot["current_phase"] = 2
    snapshot["current_step"] = "design_parameters"
    snapshot["current_status"] = "draft_design"
    snapshot["last_updated_at"] = datetime.now(timezone.utc)


    # 4) Persist atomically
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                insert_event(event)
                upsert_snapshot(snapshot)
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return snapshot







@router.post("/{experiment_id}/design")
def save_design_parameters(experiment_id: uuid.UUID,
                            request: DesignParametersRequest,
                            current_user = Depends(get_current_user)):
    print(">>> HANDLER:", __name__, "FUNCTION:", create_experiment)
    print(">>> DESIGN FEASIBILITY ENDPOINT HIT <<<")
    
    user_id = get_user_id_from_jwt(current_user)

    payload = request.dict()

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    #  Idempotent guard for locked experiments
    if snapshot.get("locked_version") is not None:
        return {
            "validation": {
                "is_valid": True,
                "warnings": [],
                "errors": []
            },
            "snapshot": snapshot,
        }

    # 1) Save parameters event
    params_event = build_design_parameters_saved_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload=payload,
    )

    # 2) Run validator (PURE)
    validation = validate_design_feasibility(
    metric_type=request.metric_type,
    design_type=request.design_type,
    planned_traffic=request.planned_traffic.root,
    baseline=request.baseline.value if request.baseline else None,
    std_dev=request.std_dev,
    target_mde=request.target_mde,
    alpha=request.alpha,
    power=request.power,
    test_direction=request.test_direction,
        )


    severity = (
        "error"
        if not validation.is_valid
        else "warning"
        if validation.warnings
        else "info"
    )

    validation_event = build_design_validated_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload=validation.dict(),
        severity=severity,
    )

    # 3) Mutate snapshot
    snapshot = apply_design_parameters_to_snapshot(
    snapshot,
    payload,
    params_event["occurred_at"]
    )

    snapshot = apply_design_validation_to_snapshot(snapshot, validation, validation_event["occurred_at"])

    #  COMMIT DESIGN INPUTS (Phase 2 → Phase 3 contract)
    snapshot["design_inputs"] = payload

    # ---- STATE MACHINE ENFORCEMENT (Phase 2 → Phase 3) ----
    snapshot["current_phase"] = 3
    snapshot["current_step"] = "phase3_feasibility"
    snapshot["current_status"] = "phase3_in_progress"
    snapshot["last_updated_at"] = datetime.now(timezone.utc)


    # 4) Persist atomically
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                insert_event(params_event)
                insert_event(validation_event)
                upsert_snapshot(snapshot)
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "validation": validation,
        "snapshot": snapshot,
    }

@router.post("/{experiment_id}/design/override")
def override_design(experiment_id: uuid.UUID, 
                    request: DesignOverrideRequest,
                    current_user = Depends(get_current_user)):
    print(">>> HANDLER:", __name__, "FUNCTION:", create_experiment)
    
    user_id = get_user_id_from_jwt(current_user)

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    if snapshot["current_status"] != "blocked":
        raise HTTPException(status_code=400, detail="Override not required")

    event = build_design_override_accepted_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload=request.model_dump(mode="json")
    )

    snapshot = apply_design_override_to_snapshot(snapshot, event["occurred_at"])

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                insert_event(event)
                from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot
                upsert_snapshot(snapshot)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return snapshot


@router.post("/{experiment_id}/phase3/feasibility/detectability")
def run_phase3_detectability(
    experiment_id: uuid.UUID,
    current_user = Depends(get_current_user),
):
    """
    Phase 3 – Detectability Feasibility

    Evaluates whether the experiment can realistically detect
    business-meaningful effects, given the Phase 2 design.
    """

    # ----------------------------
    # 1. Load snapshot (Phase 2 must exist)
    # ----------------------------
    from backend.v2.core.snapshots.snapshot_reader import (
        get_snapshot_by_experiment_id,
    )

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    if snapshot.get("locked_version") is not None:
        raise HTTPException(
            status_code=400,
            detail="Experiment design is already committed",
        )

    design = snapshot.get("design_inputs")

    if design is None:
        raise HTTPException(
            status_code=400,
            detail="Design parameters are not yet available. Phase 3 cannot run."
        )

    required = ["target_mde", "alpha", "power", "planned_traffic"]
    missing = [k for k in required if k not in design]

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Design incomplete for Phase 3. Missing: {missing}"
        )


    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if snapshot["current_phase"] < 3:
        raise HTTPException(
            status_code=400,
            detail="Phase 3 cannot run before design is completed",
        )

    # ----------------------------
    # 2. Run Phase 3 detectability validator
    # ----------------------------
    result = validate_detectability_feasibility(
        snapshot=snapshot,
        minimum_worthwhile_effect=design["target_mde"],
        effect_scale="absolute",
        effect_direction_constraint=(
            "increase"
            if design["test_direction"] == "one_tailed"
            else "two_sided"
        ),
    )


    print("DEBUG PHASE3 RESULT OBJECT:", result)
    print("DEBUG PHASE3 RESULT TYPE:", type(result))

    # If result is a Pydantic model, this will work
    try:
        print("DEBUG PHASE3 RESULT DICT:", result.dict())
    except Exception as e:
        print("DEBUG RESULT DICT FAILED:", e)


        # ----------------------------
    # 3. Persist Phase 3 detectability event
    # ----------------------------
    
    

    event = build_phase3_detectability_evaluated_event(
    experiment_id=experiment_id,
    user_id=user_id,
    payload={
        "inputs": {
            "minimum_worthwhile_effect": design["target_mde"],
            "effect_scale": "absolute",
            "effect_direction_constraint": (
                "increase"
                if design["test_direction"] == "one_tailed"
                else "two_sided"
            ),
        },
        "result": result.dict(),
    },
)



    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                insert_event(event)
            conn.commit()  # 🔑 REQUIRED for psycopg v3
            # ----------------------------
            # 3.5 Persist result into snapshot
            # ----------------------------
            from backend.v2.core.snapshots.snapshot_reader import (
                get_snapshot_by_experiment_id,
            )

            snapshot = get_snapshot_by_experiment_id(experiment_id)
            require_experiment_owner(snapshot, user_id)
            

            snapshot = persist_phase3_result(
                snapshot=snapshot,
                pillar="detectability",
                result=result.dict(),
                event_id=event["event_id"],
                occurred_at=event["occurred_at"],
            )

            snapshot["current_step"] = "phase3_feasibility"
            snapshot["last_updated_at"] = datetime.now(timezone.utc)
            
            print(">>> SNAPSHOT AFTER persist_phase3_result:")
            print(snapshot.keys())
            print(">>> phase3_results value:")
            print(snapshot.get("phase3_results"))

            upsert_snapshot(snapshot)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    # ----------------------------
    # 4. Return result + event metadata
    # ----------------------------
    return {
        "phase": 3,
        "pillar": "detectability",
        "experiment_id": experiment_id,
        "event_id": event["event_id"],
        "result": result.dict(),
    }


@router.post("/{experiment_id}/phase3/feasibility/power-grid")
def run_phase3_power_grid(
    experiment_id: uuid.UUID,
    request: Phase3PowerGridRequest,
    current_user = Depends(get_current_user),
):
    """
    Phase 3 – Detectability (Power–Effect Grid)

    Computes power at multiple effect sizes for visualization.
    """

    from backend.v2.core.snapshots.snapshot_reader import (
        get_snapshot_by_experiment_id,
    )

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)
    
    if snapshot.get("locked_version") is not None:
        raise HTTPException(
            status_code=400,
            detail="Experiment design is already committed",
        )

    if snapshot["current_phase"] < 3:
        raise HTTPException(
            status_code=400,
            detail="Phase 3 cannot run before design is completed",
        )
    
    design = snapshot.get("design_inputs")

    if design is None:
        raise HTTPException(
            status_code=400,
            detail="Design parameters are not yet available. Phase 3 cannot run."
        )


    grid = compute_power_grid(
        snapshot=snapshot,
        effect_values=request.effect_values,
    )

    from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot
    from backend.v2.core.snapshots.snapshot_phase3 import persist_phase3_result
    from datetime import datetime, timezone

    snapshot = persist_phase3_result(
        snapshot=snapshot,
        pillar="power_grid",
        result={"grid": grid},
        event_id=None,
        occurred_at=datetime.now(timezone.utc),
    )

    upsert_snapshot(snapshot)

    return {
    "phase": 3,
    "pillar": "detectability",
    "artifact": "power_effect_grid",
    "experiment_id": experiment_id,
    "approximation": (
        "Power values are computed using a linearized normal-approximation "
        "around the design MDE. Use for visualization only."
    ),
    "grid": grid,
    }


@router.get("/{experiment_id}/snapshot")
def get_experiment_snapshot(experiment_id: uuid.UUID,
                            current_user = Depends(get_current_user),):
    from backend.v2.core.snapshots.snapshot_reader import (
        get_snapshot_by_experiment_id,
    )

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    

    # Frontend-safe subset only
    return {
        "experiment_id": snapshot["experiment_id"],
        "metric_type": snapshot["metric_type"],
        "design_inputs": snapshot.get("design_inputs"),
        "current_phase": snapshot["current_phase"],
    }




@router.post("/{experiment_id}/phase3/feasibility/sample-time")
def run_phase3_sample_time(
    experiment_id: uuid.UUID,
    current_user = Depends(get_current_user),
):

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
         raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    if snapshot.get("locked_version") is not None:
        raise HTTPException(
            status_code=400,
            detail="Experiment design is already committed",
        )

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if snapshot["current_phase"] < 3:
        raise HTTPException(
            status_code=400,
            detail="Phase 3 cannot run before design is completed",
        )

    design = snapshot.get("design_inputs")

    if design is None:
        raise HTTPException(
            status_code=400,
            detail="Design parameters are not yet available. Phase 3 cannot run."
        )

    

    # ✅ NEW: forward to core validator
    result = validate_sample_time_feasibility(
        snapshot=snapshot,
        
    )

    
    

    event = build_phase3_sample_time_evaluated_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload={
                "inputs": snapshot.get("design_inputs", {}),
                "result": result.dict(),
            },
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)
        conn.commit()
        snapshot = get_snapshot_by_experiment_id(experiment_id)
        require_experiment_owner(snapshot, user_id)
        

        snapshot = persist_phase3_result(
            snapshot=snapshot,
            pillar="sample_time",
            result=result.dict(),
            event_id=event["event_id"],
            occurred_at=event["occurred_at"],
        )

        snapshot["current_step"] = "phase3_feasibility"
        snapshot["last_updated_at"] = datetime.now(timezone.utc)

        upsert_snapshot(snapshot)


    return {
        "phase": 3,
        "pillar": "sample_time",
        "experiment_id": experiment_id,
        "event_id": event["event_id"],
        "result": result.dict(),
    }


# @router.post("/{experiment_id}/phase3/feasibility/decision-robustness")
# def run_phase3_decision_robustness(experiment_id: uuid.UUID):

#     from backend.v2.core.snapshots.snapshot_reader import (
#         get_snapshot_by_experiment_id,
#     )

#     snapshot = get_snapshot_by_experiment_id(experiment_id)

#     if snapshot is None:
#         raise HTTPException(status_code=404, detail="Experiment not found")

#     if snapshot["current_phase"] < 3:
#         raise HTTPException(
#             status_code=400,
#             detail="Phase 3 cannot run before design is completed",
#         )

#     # ----------------------------
#     # Load latest detectability event
#     # ----------------------------
#     from backend.v2.core.events.event_reader import (
#         get_latest_phase3_detectability_event,
#     )

#     detectability_event = get_latest_phase3_detectability_event(experiment_id)

#     if detectability_event is None:
#         raise HTTPException(
#             status_code=400,
#             detail="Detectability must be evaluated before decision robustness",
#         )

#     detectability_result = detectability_event["payload"]["result"]

#     # ----------------------------
#     # Run validator
#     # ----------------------------
#     result = validate_decision_robustness(
#         snapshot=snapshot,
#         detectability_result=detectability_result,
#     )

#     # ----------------------------
#     # Persist event
#     # ----------------------------
#     current_user = Depends(get_current_user)
   #     user_id = get_user_id_from_jwt(current_user)

#     event = build_phase3_decision_robustness_evaluated_event(
#         experiment_id=experiment_id,
#         user_id=user_id,
#         payload={
#             "inputs": {
#                 "source": "detectability_outputs",
#             },
#             "result": result.dict(),
#         },
#     )

#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             insert_event(event)
#         conn.commit()

#     return {
#         "phase": 3,
#         "pillar": "decision_robustness",
#         "experiment_id": experiment_id,
#         "event_id": event["event_id"],
#         "result": result.dict(),
#     }



@router.post("/{experiment_id}/phase3/feasibility/decision-robustness")
def run_phase3_decision_robustness(experiment_id: uuid.UUID,
                                   current_user = Depends(get_current_user),):

    print(">>> ENTERED decision robustness endpoint")

    user_id = get_user_id_from_jwt(current_user)

    try:
        from backend.v2.core.snapshots.snapshot_reader import (
            get_snapshot_by_experiment_id,
        )

        snapshot = get_snapshot_by_experiment_id(experiment_id)
        
        

        if snapshot is None:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        require_experiment_owner(snapshot, user_id)
        forbid_if_completed(snapshot)

        if snapshot.get("locked_version") is not None:
            raise HTTPException(
                status_code=400,
                detail="Experiment design is already committed",
            )
        
        # ----------------------------
        # HARD GUARD: design must exist
        # ----------------------------
        design = snapshot.get("design_inputs")

        if design is None:
            raise HTTPException(
                status_code=400,
                detail="Design parameters are not available. Cannot evaluate decision robustness."
            )

        
        print(">>> SNAPSHOT LOADED:", snapshot is not None)

        if snapshot is None:
            raise Exception("Snapshot not found")

        if snapshot["current_phase"] < 3:
            raise Exception("Phase < 3")

       

       # ----------------------------
        # Recompute detectability (canonical source)
        # ----------------------------
        from backend.v2.core.events.event_reader import (
            get_latest_phase3_detectability_event,
        )

        detect_event = get_latest_phase3_detectability_event(experiment_id)

        if detect_event is None:
            raise HTTPException(
                status_code=409,
                detail="Detectability must complete before decision robustness"
            )

        detectability_result = detect_event["payload"]["result"]



        # ----------------------------
        # Run validator
        # ----------------------------
        from backend.v2.core.phase3_feasibility.decision_robustness import (
            validate_decision_robustness,
        )

        result = validate_decision_robustness(
            snapshot=snapshot,
            detectability_result=detectability_result,
        )

        print(">>> DECISION ROBUSTNESS RESULT:", result.dict())

        # ----------------------------
        # Persist event
        # ----------------------------
        from backend.v2.core.events.event_factory import (
            build_phase3_decision_robustness_evaluated_event,
        )

        
        

        event = build_phase3_decision_robustness_evaluated_event(
            experiment_id=experiment_id,
            user_id=user_id,
            payload={
                "inputs": {"source": "detectability_outputs"},
                "result": result.dict(),
            },
        )

        print(">>> EVENT TO INSERT:", event)

        from backend.v2.core.events.event_repository import insert_event

        with get_connection() as conn:
            with conn.cursor() as cur:
                insert_event(event)
            conn.commit()
            snapshot = get_snapshot_by_experiment_id(experiment_id)
            require_experiment_owner(snapshot, user_id)
            

            snapshot = persist_phase3_result(
                snapshot=snapshot,
                pillar="decision_robustness",
                result=result.dict(),
                event_id=event["event_id"],
                occurred_at=event["occurred_at"],
            )

            snapshot["current_step"] = "phase3_feasibility"
            snapshot["last_updated_at"] = datetime.now(timezone.utc)
            upsert_snapshot(snapshot)


        return {
            "phase": 3,
            "pillar": "decision_robustness",
            "experiment_id": experiment_id,
            "event_id": event["event_id"],
            "result": result.dict(),
        }

    except Exception as e:
        print("❌ DECISION ROBUSTNESS FAILURE:", repr(e))
        raise HTTPException(
            status_code=400,
            detail=f"Decision robustness failed: {repr(e)}"
        )

@router.post("/{experiment_id}/phase3/feasibility/risk-disclosure")
def run_phase3_risk_disclosure(experiment_id: uuid.UUID,
                               current_user = Depends(get_current_user),):

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
    from backend.v2.core.events.event_reader import (
        get_latest_phase3_detectability_event,
        get_latest_phase3_sample_time_event,
    )
    from backend.v2.core.phase3_feasibility.risk_disclosure import (
        evaluate_risk_disclosure,
    )

    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    if snapshot.get("locked_version") is not None:
        raise HTTPException(
            status_code=400,
            detail="Experiment design is already committed",
        )
    
    # ----------------------------
    # HARD GUARD: design must exist
    # ----------------------------
    design = snapshot.get("design_inputs")

    if design is None:
        raise HTTPException(
            status_code=400,
            detail="Design parameters are not available. Cannot evaluate risk disclosure."
        )

    
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    detect_event = get_latest_phase3_detectability_event(experiment_id)
    sample_event = get_latest_phase3_sample_time_event(experiment_id)

    if not detect_event or not sample_event:
        raise HTTPException(
            status_code=409,
            detail="All Phase 3 prerequisites must complete before risk disclosure"
        )

    result = evaluate_risk_disclosure(
        snapshot=snapshot,
        detectability_result=detect_event["payload"]["result"],
        sample_time_result=sample_event["payload"]["result"],
    )

    
    

    event = build_phase3_risk_disclosure_evaluated_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload={
            "inputs": {
                "sources": ["detectability", "sample_time"],
            },
            "result": result.dict(),
        },
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)
        conn.commit()
        snapshot = get_snapshot_by_experiment_id(experiment_id)
        require_experiment_owner(snapshot, user_id)
       

        snapshot = persist_phase3_result(
            snapshot=snapshot,
            pillar="risk_disclosure",
            result=result.dict(),
            event_id=event["event_id"],
            occurred_at=event["occurred_at"],
        )

        


    # ----------------------------
    # MARK PHASE 3 AS COMPLETE
    # ----------------------------
    snapshot["current_status"] = "phase3_complete"
    snapshot["current_step"] = "phase3_feasibility"
    snapshot["last_updated_at"] = datetime.now(timezone.utc)

    upsert_snapshot(snapshot)


    return {
        "phase": 3,
        "pillar": "risk_disclosure",
        "experiment_id": experiment_id,
        "event_id": event["event_id"],
        "result": result.dict(),
    }


@router.post("/{experiment_id}/phase3/commit/accept")
def accept_experiment_design(experiment_id: uuid.UUID,
                             current_user = Depends(get_current_user),):

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
    from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot

    user_id = get_user_id_from_jwt(current_user) 

    snapshot = get_snapshot_by_experiment_id(experiment_id)
    
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    require_phase3_action_allowed(snapshot, "accept")

    
       

    event = build_phase3_design_accepted_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload={},
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)

            snapshot = apply_commitment_to_snapshot(
                snapshot,
                new_status="running",
                occurred_at=event["occurred_at"],
            )

            upsert_snapshot(snapshot)
        conn.commit()

    return {
        "status": "accepted",
        "state": "running",
    }


@router.post("/{experiment_id}/phase3/commit/block")
def block_experiment_design(experiment_id: uuid.UUID,
                            current_user = Depends(get_current_user),):

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
    from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    require_phase3_action_allowed(snapshot, "block")

    
    

    event = build_phase3_design_blocked_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload={},
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)

            snapshot = apply_commitment_to_snapshot(
                snapshot,
                new_status="blocked",
                occurred_at=event["occurred_at"],
            )

            upsert_snapshot(snapshot)
        conn.commit()

    return {
        "status": "blocked",
        "state": "blocked",
    }


@router.post("/{experiment_id}/phase3/commit/redesign")
def request_experiment_redesign(experiment_id: uuid.UUID,
                                current_user = Depends(get_current_user),):

    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
    from backend.v2.core.snapshots.snapshot_updater import upsert_snapshot

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    require_phase3_action_allowed(snapshot, "redesign")

    
    

    event = build_phase3_design_redesign_requested_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload={},
    )

    snapshot["redesign_requested_at"] = event["occurred_at"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)

            snapshot = apply_commitment_to_snapshot(
                snapshot,
                new_status="redesign_requested",
                occurred_at=event["occurred_at"],
            )

            upsert_snapshot(snapshot)
        conn.commit()

    return {
        "status": "redesign_requested",
        "next_step": "create_new_experiment",
    }


@router.get("/{experiment_id}/snapshot/full")
def get_experiment_snapshot_full(experiment_id: uuid.UUID,current_user = Depends(get_current_user),):
    from backend.v2.core.snapshots.snapshot_reader import (
        get_snapshot_by_experiment_id,
    )

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    require_experiment_owner(snapshot, user_id)
    

    return snapshot


@router.delete("/{experiment_id}")
def delete_experiment(experiment_id: uuid.UUID,current_user = Depends(get_current_user),):
    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)
    

    if snapshot is None:
        # Idempotent delete — already gone
        return {"status": "already_deleted"}
    
    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    # ❌ Do NOT allow deletion after Phase 3 commitment
    if snapshot.get("locked_version") is not None:
        raise HTTPException(
            status_code=400,
            detail="Committed experiments cannot be deleted"
        )

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1️⃣ Delete events FIRST (foreign key safety)
                cur.execute(
                    "DELETE FROM experiment_events WHERE experiment_id = %s",
                    (experiment_id,)
                )

                # 2️⃣ Delete snapshot
                cur.execute(
                    "DELETE FROM experiment_snapshots WHERE experiment_id = %s",
                    (experiment_id,)
                )

            conn.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "deleted"}


@router.post("/{experiment_id}/phase4/enter")
def enter_phase4(
    experiment_id: UUID,
    current_user = Depends(get_current_user),
):
    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_by_experiment_id(experiment_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    event, snapshot = phase4.enter_phase4(
        snapshot=snapshot,
        experiment_id=experiment_id,
        user_id=user_id,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)
            upsert_snapshot(snapshot)
        conn.commit()

    return {"status": "phase4_entered"}




@router.post("/{experiment_id}/phase4/select-path")
def select_phase4_path(
    experiment_id: UUID,
    payload: dict,
    current_user = Depends(get_current_user),
):
    choice = payload.get("choice")
    if choice not in {"yes_analyze", "no_analyze"}:
        raise HTTPException(status_code=400, detail="Invalid choice")

    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_by_experiment_id(experiment_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    from backend.v2.core.gaurds.experiment_state import assert_phase4_not_finalized

    assert_phase4_not_finalized(snapshot)

    event, snapshot = phase4.select_phase4_analysis_path(
        snapshot=snapshot,
        experiment_id=experiment_id,
        user_id=user_id,
        choice=choice,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)
            upsert_snapshot(snapshot)
        conn.commit()

    return {"status": "phase4_path_selected"}



@router.post("/{experiment_id}/phase4/finalize")
def finalize_phase4(
    experiment_id: UUID,
    payload: dict,
    current_user = Depends(get_current_user),
):
    decision = payload.get("decision")
    notes = payload.get("notes")

    if not decision:
        raise HTTPException(status_code=400, detail="Decision is required")

    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_by_experiment_id(experiment_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    try:
        event, snapshot = phase4.finalize_phase4(
            snapshot=snapshot,
            experiment_id=experiment_id,
            user_id=user_id,
            decision=decision,
            notes=notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)
            upsert_snapshot(snapshot)
        conn.commit()

    return {"status": "experiment_completed"}


@router.post("/{experiment_id}/phase4/finalize-with-analysis")
def finalize_phase4_with_analysis(
    experiment_id: UUID,
    current_user = Depends(get_current_user),
):
    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_by_experiment_id(experiment_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    event, snapshot = phase4.finalize_phase4_with_analysis(
        snapshot=snapshot,
        experiment_id=experiment_id,
        user_id=user_id,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)
            upsert_snapshot(snapshot)
        conn.commit()

    return {"status": "phase4_finalized_with_analysis"}


@router.post("/{experiment_id}/phase5/inference")
def run_phase5_inference(
    experiment_id: UUID,
    payload: Phase3InferenceRequest,
    current_user = Depends(get_current_user),
):
    """
    Phase 5 — Experiment Measurement (Inference)

    Runs inference ONCE and persists results as a terminal event.
    """

    from backend.api.inference import run_inference
    from backend.v2.core.events.event_factory import (
        build_phase5_inference_completed_event
    )
    from backend.v2.core.events.event_repository import insert_event
    from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id

    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_by_experiment_id(experiment_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    require_experiment_owner(snapshot, user_id)

    if snapshot.get("current_status") == "completed":
        raise HTTPException(
            status_code=400,
            detail="Experiment is completed and read-only"
        )

    if snapshot.get("current_status") != "analysis_pending":
        raise HTTPException(
            status_code=400,
            detail="Phase 5 inference is not allowed in current state"
        )

    # HARD GUARD: Phase 4 must be finalized with analysis
    if snapshot.get("current_phase") < 4:
        raise HTTPException(
            status_code=400,
            detail="Phase 5 cannot run before Phase 4 is complete"
        )

    # HARD GUARD: inference can run ONLY ONCE
    from backend.v2.db.connection import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM experiment_events
                WHERE experiment_id = %s
                  AND event_type = %s
                LIMIT 1
                """,
                (str(experiment_id), "PHASE5_INFERENCE_COMPLETED"),
            )
            if cur.fetchone():
                raise HTTPException(
                    status_code=409,
                    detail="Inference has already been computed for this experiment"
                )

    # ----------------------------
    # Run inference engine (PURE)
    # ----------------------------
    inference_result, warnings = run_inference(payload)
    print("=" * 80)
    print(" FORENSIC: What does run_inference() actually return?")
    print("=" * 80)
    print(f"Type of inference_result: {type(inference_result)}")
    print(f"inference_result keys (if dict): {inference_result.keys() if isinstance(inference_result, dict) else 'NOT A DICT'}")
    print(f"inference_result value: {inference_result}")
    print("=" * 80)

    # ----------------------------
    # Build Phase 5 event payload
    # ----------------------------
    from backend.v2.core.serialization.inference_serializer import (
    serialize_inference_inputs
    )

    event_payload = {
        "inputs": serialize_inference_inputs(payload),
        "results": inference_result,
        "warnings": list(set(warnings)),
        "engine": {
            "name": "inference_engine",
            "version": "v1.0"
        }
    }

    event = build_phase5_inference_completed_event(
        experiment_id=experiment_id,
        user_id=user_id,
        payload=event_payload,
    )

    # ----------------------------
    # Persist atomically (EVENT + SNAPSHOT)
    # ----------------------------
    snapshot["current_status"] = "analysis_completed"
    snapshot["current_phase"] = 5
    snapshot["current_step"] = "analysis_completed"
    snapshot["last_updated_at"] = datetime.now(timezone.utc)

    # ----------------------------
    # Persist Phase 5 results into snapshot (WITH USER INPUTS)
    # ----------------------------

    observed_data = _build_phase5_observed_data(
        payload=payload.model_dump(mode="json")
    )

    snapshot["phase5_results"] = {
        #  ACTIVE USER INPUTS (for hydration)
        "observed_data": observed_data,

        #  ENGINE OUTPUTS (already correct)
        "results": inference_result,
        "warnings": warnings,

        "engine": {
            "name": "inference_engine",
            "version": "v1.0",
        },

        # Audit metadata
        "event_id": event["event_id"],
        "occurred_at": event["occurred_at"],
    }

    if "created_at" not in snapshot:
        snapshot["created_at"] = datetime.now(timezone.utc)

    with get_connection() as conn:
        with conn.cursor() as cur:
            insert_event(event)
            upsert_snapshot(snapshot)
        conn.commit()

    return {
        "phase": 5,
        "experiment_id": experiment_id,
        "event_id": event["event_id"],
        "result": inference_result,
        "warnings": warnings,
    }





@router.post("/{experiment_id}/phase5/complete")
def complete_phase5_experiment(
    experiment_id: UUID,
    payload: dict,
    current_user = Depends(get_current_user),
):
    decision = payload.get("decision")
    notes = payload.get("notes")

    if not decision:
        raise HTTPException(status_code=400, detail="Decision is required")

    user_id = get_user_id_from_jwt(current_user)
    snapshot = get_snapshot_by_experiment_id(experiment_id)

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    require_experiment_owner(snapshot, user_id)
    forbid_if_completed(snapshot)

    if snapshot.get("current_status") != "analysis_completed":
        raise HTTPException(
            status_code=400,
            detail="Experiment must complete analysis before finishing"
        )

    snapshot["final_decision"] = decision
    snapshot["final_notes"] = notes
    snapshot["current_status"] = "completed"
    snapshot["current_step"] = "experiment_completed"
    snapshot["completed_at"] = datetime.now(timezone.utc)
    snapshot["last_updated_at"] = datetime.now(timezone.utc)

    upsert_snapshot(snapshot)

    return {"status": "experiment_completed"}