from typing import Dict, Any

from backend.v2.services.mde_service import compute_mde_v1
from backend.v2.models.phase3_feasibility import Phase3DetectabilityResult

from backend.v2.core.phase3_feasibility.baseline_sensitivity import (
    compute_baseline_sensitivity,
)



def validate_detectability_feasibility(
    *,
    snapshot: dict,
    minimum_worthwhile_effect: float,
    effect_scale: str,
    effect_direction_constraint: str,
) -> Phase3DetectabilityResult:

    """
    Phase 3 – Pillar 1: Detectability Feasibility

    This function:
    - Reads Phase 2 design inputs from snapshot
    - Reuses canonical V1 MDE engine
    - Evaluates whether business-meaningful effects are detectable
    - Does NOT mutate snapshot
    - Does NOT write to DB
    """

    warnings = []
    explanations = []

    # ----------------------------
    # 1. Extract Phase 2 inputs
    # ----------------------------
    design_inputs = snapshot.get("design_inputs") or {}

    metric_type = snapshot["metric_type"]  # still comes from definition
    design_type = design_inputs.get("design_type")
    planned_traffic = design_inputs.get("planned_traffic")
    baseline_obj = design_inputs.get("baseline")
    baseline = (
        baseline_obj.get("value")
        if isinstance(baseline_obj, dict)
        else baseline_obj
    )

    std_dev = design_inputs.get("std_dev")
    alpha = design_inputs.get("alpha")
    power = design_inputs.get("power")
    test_direction = design_inputs.get("test_direction", "two_tailed")


    if not planned_traffic:
        return Phase3DetectabilityResult(
            is_valid=False,
            computed={},
            warnings=[],
            errors=[{
                "code": "NO_PLANNED_TRAFFIC",
                "message": "Planned traffic is required before Phase 3 feasibility."
            }],
            explanations=[
                "Detectability cannot be evaluated without planned traffic."
            ],
        )


    # ----------------------------
    # 2. Compute statistical MDE
    # ----------------------------
    mde_result = compute_mde_v1(
        metric_type=metric_type,
        design_type=design_type,
        baseline_rate=baseline,
        std_dev=std_dev,
        discordance_rate=None,
        planned_traffic=planned_traffic,
        alpha=alpha,
        power=power,
        test_direction=test_direction,
    )

    if not mde_result["valid"]:
        return Phase3DetectabilityResult(
            is_valid=False,
            computed={},
            warnings=[],
            errors=[
                {"code": "MDE_ENGINE_INVALID", "message": msg}
                for msg in mde_result.get("engine_errors", [])
            ],
            explanations=[
                "Detectability could not be evaluated due to invalid design inputs."
            ],
        )


    pairwise = mde_result["pairwise_results"]
    max_mde = max(r["mde"] for r in pairwise)

    # ----------------------------
    # 3. Compute power at MWE
    # ----------------------------
    # Approximate power curve logic:
    # If MWE < MDE → power < target power
    # Linear approximation is acceptable at this stage (explicitly explained)

    power_at_mwe = min(1.0, power * (minimum_worthwhile_effect / max_mde))

    detectability_gap = max_mde - minimum_worthwhile_effect

    baseline_sensitivity = compute_baseline_sensitivity(
    snapshot=snapshot,
    minimum_worthwhile_effect=minimum_worthwhile_effect,
        )


    # ----------------------------
    # 4. Verdict logic
    # ----------------------------
    if power_at_mwe >= power:
        verdict = "feasible"
    elif power_at_mwe >= 0.6:
        verdict = "borderline"
        warnings.append({
            "code": "LOW_POWER_AT_MWE",
            "message": "There is a moderate risk of missing meaningful effects."
        })
    else:
        verdict = "not_feasible"
        warnings.append({
            "code": "VERY_LOW_POWER_AT_MWE",
            "message": "The experiment is unlikely to detect effects that matter."
        })

    # ----------------------------
    # 5. Explanations
    # ----------------------------
    explanations.append(
        f"Minimum detectable effect with current design is {round(max_mde * 100, 2)}%."
    )

    explanations.append(
        f"Power to detect the minimum worthwhile effect is approximately "
        f"{round(power_at_mwe * 100, 1)}%."
    )

    if verdict != "feasible":
        explanations.append(
            "Even if the experiment succeeds in reality, it may appear inconclusive."
        )


    clean_baseline_sensitivity = []

    for row in baseline_sensitivity:
        clean_baseline_sensitivity.append({
            "scenario": row["scenario"],
            "assumed_baseline": float(row["assumed_baseline"]),
            "statistical_mde": float(row["statistical_mde"]),
            "power_at_mwe": float(row["power_at_mwe"]),
            "verdict": row["verdict"],
        })


    # ----------------------------
    # 6. Final result
    # ----------------------------
    return Phase3DetectabilityResult(
    is_valid=True,
    computed={
        "statistical_mde": float(max_mde),
        "power_at_minimum_worthwhile_effect": float(power_at_mwe),
        "detectability_gap": float(detectability_gap),
        "feasibility_verdict": verdict,
        "baseline_sensitivity": clean_baseline_sensitivity,
    },
    warnings=warnings,
    errors=[],
    explanations=explanations,
    )

