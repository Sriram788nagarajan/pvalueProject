"""
Phase 0.3 — Experiment Design Validation Engine

Orchestrates:
- Layer 1: Schema validation
- Layer 2: Semantic validation
- Layer 3: Statistical feasibility checks

This file contains NO business logic of its own.
It only coordinates layers and returns a canonical response.
"""

from backend.validation.schema import validate_schema
from backend.validation.semantic import validate_semantics

from backend.validation.stats.power_analysis import (
    analyze_power_and_sample_size,
    analyze_mean_metric
)

from backend.validation.stats.verdicts import classify_statistical_risk


def validate_experiment_design(payload: dict) -> dict:
    """
    Master validation entry point for Phase 0.3.

    Input:
        payload (dict): Raw UI / API payload describing experiment design

    Output:
        dict: Canonical validation response
    """

    # --------------------------------------------------
    # Layer 1 — Schema validation (structure only)
    # --------------------------------------------------
    schema_result = validate_schema(payload)

    if not schema_result.get("ok", False):
        return {
            "status": "BLOCKED",
            "layer": 1,
            "errors": schema_result.get("errors", [])
        }

    # --------------------------------------------------
    # Layer 2 — Semantic validation (meaning + typing)
    # --------------------------------------------------
    semantic_result = validate_semantics(payload)

    if not semantic_result.get("ok", False):
        return {
            "status": "BLOCKED",
            "layer": 2,
            "errors": semantic_result.get("errors", [])
        }

    metric_type = semantic_result["metric_type"]
    statistical_plan = semantic_result["statistical_plan"]
    traffic = semantic_result["traffic"]

    # --------------------------------------------------
    # Layer 3 — Statistical feasibility checks
    # --------------------------------------------------
    if metric_type == "proportion":
        stat_result = analyze_power_and_sample_size(
            hypothesis=semantic_result["hypothesis_inputs"],
            plan=statistical_plan,
            traffic=traffic
        )

    elif metric_type == "mean":
        stat_result = analyze_mean_metric(
            mean_inputs=semantic_result["mean_inputs"],
            plan=statistical_plan,
            traffic=traffic
        )

    else:
        return {
            "status": "BLOCKED",
            "layer": 3,
            "errors": [{
                "code": "UNSUPPORTED_METRIC_TYPE",
                "message": f"Metric type '{metric_type}' is not supported."
            }]
        }

    # --------------------------------------------------
    # Layer 3 verdict classification
    # --------------------------------------------------
    verdict = classify_statistical_risk(
        result=stat_result,
        desired_power=statistical_plan.power
    )

    # --------------------------------------------------
    # Canonical response
    # --------------------------------------------------
    return {
        "status": verdict["status"],
        "layer": 3,
        "statistics": stat_result,
        "verdict": verdict
    }




