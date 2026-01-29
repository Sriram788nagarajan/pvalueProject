import uuid
from datetime import datetime, timezone


from backend.v2.core.events.event_types import EXPERIMENT_CREATED
from backend.v2.core.events.event_types import DEFINITION_SAVED
from backend.v2.core.events.event_types import PHASE3_FEASIBILITY_DETECTABILITY_EVALUATED
from backend.v2.core.events.event_types import PHASE3_SAMPLE_TIME_FEASIBILITY_EVALUATED

from backend.v2.core.events.event_types import (
    DESIGN_PARAMETERS_SAVED,
    DESIGN_VALIDATED,
    DESIGN_OVERRIDE_ACCEPTED,
    PHASE3_DESIGN_ACCEPTED,
    PHASE3_DESIGN_BLOCKED,
    PHASE3_DESIGN_REDESIGN_REQUESTED
)



def build_experiment_created_event(
    *,
    experiment_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: dict,
) -> dict:
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": EXPERIMENT_CREATED,
        "phase": 1,
        "severity": "info",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }



def build_definition_saved_event(
    *,
    experiment_id,
    user_id,
    payload
):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": DEFINITION_SAVED,
        "phase": 2,
        "severity": "info",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }


def build_design_parameters_saved_event(*, experiment_id, user_id, payload):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": DESIGN_PARAMETERS_SAVED,
        "phase": 3,
        "severity": "info",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }


def build_design_validated_event(*, experiment_id, user_id, payload, severity):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": DESIGN_VALIDATED,
        "phase": 3,
        "severity": severity,  # info | warning | error
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }


def build_design_override_accepted_event(*, experiment_id, user_id, payload):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": DESIGN_OVERRIDE_ACCEPTED,
        "phase": 3,
        "severity": "warning",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }

def build_phase3_detectability_evaluated_event(
    *,
    experiment_id,
    user_id,
    payload,
):
    result = payload.get("result", {})

    verdict = (
        result.get("computed", {}).get("feasibility_verdict")
        if result.get("is_valid")
        else None
    )

    severity = (
        "info" if verdict == "feasible"
        else "warning" if verdict in ("borderline", "not_feasible")
        else "warning"  # invalid Phase 3 still matters
    )

    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": PHASE3_FEASIBILITY_DETECTABILITY_EVALUATED,
        "phase": 3,
        "severity": severity,
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }


def build_phase3_sample_time_evaluated_event(
    *,
    experiment_id,
    user_id,
    payload,
):
    verdict = payload.get("result", {}).get("computed", {}).get("time_feasibility_verdict")

    severity = (
        "info" if verdict == "feasible"
        else "warning"
    )

    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": PHASE3_SAMPLE_TIME_FEASIBILITY_EVALUATED,
        "phase": 3,
        "severity": severity,
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }



def build_phase3_decision_robustness_evaluated_event(
    *,
    experiment_id,
    user_id,
    payload: dict,
):
    verdict = payload.get("result", {}).get("verdict")

    severity = (
        "info" if verdict == "robust_decision"
        else "warning"
    )

    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": "PHASE3_DECISION_ROBUSTNESS_EVALUATED",
        "phase": 3,
        "severity": severity,
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }


def build_phase3_risk_disclosure_evaluated_event(
    *,
    experiment_id,
    user_id,
    payload: dict,
):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": "PHASE3_RISK_DISCLOSURE_EVALUATED",
        "phase": 3,
        "severity": "info",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }


def build_phase3_design_accepted_event(*, experiment_id, user_id, payload=None):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": PHASE3_DESIGN_ACCEPTED,
        "phase": 3,
        "severity": "info",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload or {},
    }


def build_phase3_design_blocked_event(*, experiment_id, user_id, payload=None):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": PHASE3_DESIGN_BLOCKED,
        "phase": 3,
        "severity": "warning",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload or {},
    }


def build_phase3_design_redesign_requested_event(*, experiment_id, user_id, payload=None):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": PHASE3_DESIGN_REDESIGN_REQUESTED,
        "phase": 3,
        "severity": "info",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload or {},
    }


def build_generic_event(
    *,
    experiment_id,
    user_id,
    event_type: str,
    phase: int,
    severity: str = "info",
    payload: dict | None = None,
):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": event_type,
        "phase": phase,
        "severity": severity,
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload or {},
    }


def build_phase5_inference_completed_event(
    *,
    experiment_id,
    user_id,
    payload: dict,
):
    return {
        "event_id": uuid.uuid4(),
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": "PHASE5_INFERENCE_COMPLETED",
        "phase": 5,
        "severity": "info",
        "occurred_at": datetime.now(timezone.utc),
        "schema_version": 1,
        "payload": payload,
    }