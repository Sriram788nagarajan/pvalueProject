from typing import Dict, Any

from backend.v2.models.design import DesignValidationResult
from backend.v2.services.mde_service import compute_mde_v1


def  validate_design_feasibility(
    *,
    metric_type: str,
    design_type: str,
    planned_traffic: Dict[str, int],
    baseline: float | None,
    std_dev: float | None,
    target_mde: float,
    alpha: float,
    power: float,
    test_direction: str,
) -> DesignValidationResult:

    """
    Phase 3 design feasibility validator.

    This function:
    - Calls the canonical V1 MDE engine
    - Interprets its output
    - Classifies the design as valid / warning / error

    NO statistical formulas live here.
    """

    warnings = []
    errors = []
    explanations = []

    # ----------------------------
# Phase 3 input completeness checks
# ----------------------------
    if metric_type == "continuous":
        # Phase 3 requires explicit variance for continuous metrics
        # Do NOT infer or default
        if std_dev  is None:
            return DesignValidationResult(
                is_valid=False,
                computed={},
                warnings=[],
                errors=[
                    {
                        "code": "STD_DEV_REQUIRED",
                        "message": "Standard deviation is required for continuous metrics.",
                    }
                ],
                explanations=[
                    "Continuous metrics require an estimate of variability to evaluate detectability."
                ],
            )


    # ----------------------------
    # 1. Call V1 MDE engine via service
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

        # ----------------------------
    # Capture V1 warnings (DO NOT DROP)
    # ----------------------------
    for w in mde_result.get("engine_warnings", []):
        warnings.append(
            {
                "code": "V1_MDE_WARNING",
                "message": w,
            }
        )



    # ----------------------------
    # 2. Handle engine-level failures
    # ----------------------------
    if not mde_result["valid"]:
        if warnings:
            explanations.append(
            "The design has warnings in addition to blocking errors."
            )


        return DesignValidationResult(
            is_valid=False,
            computed={},
            warnings=warnings,
            errors=[
                {
                    "code": "MDE_ENGINE_INVALID",
                    "message": msg,
                }
                for msg in mde_result.get("engine_errors", [])
            ],
            explanations=[
                "The design could not be evaluated due to invalid inputs."
            ],
        )

    pairwise = mde_result["pairwise_results"]

    if not pairwise:
        return DesignValidationResult(
            is_valid=False,
            computed={},
            warnings=warnings,
            errors=[
                {
                    "code": "NO_PAIRWISE_RESULTS",
                    "message": "No valid variant comparisons could be computed.",
                }
            ],
            explanations=[
                "At least one control vs test comparison is required."
            ],
        )

    # ----------------------------
    # 3. Interpret MDE results (business logic)
    # ----------------------------
    max_mde = max(r["mde"] for r in pairwise)

    computed = {
    "mde": max_mde,
    "alpha": alpha,
    "power": power,
    "engine": mde_result["engine"],
    }   


    explanations.append(
        f"With the planned traffic, the minimum detectable effect is {round(max_mde * 100, 2)}%."
    )
    if warnings:
        explanations.append(
            "Based on these warnings, you may detect only large effects or experience inconclusive results."
        )


    # Warning: high MDE
    if max_mde > 0.05:
        warnings.append(
            {
                "code": "HIGH_MDE",
                "message": "The minimum detectable effect is large, meaning only big changes can be detected.",
            }
        )
        explanations.append(
            "Smaller but potentially meaningful effects are likely to be missed."
        )

    # Error: extremely small samples
    min_n = min(planned_traffic.values())
    if min_n < 100:
        errors.append(
            {
                "code": "TOO_FEW_SAMPLES",
                "message": "Sample size per variant is too small for reliable inference.",
            }
        )
        explanations.append(
            "Statistical tests are unreliable with very small sample sizes, even if calculations succeed."
        )

    # ----------------------------
    # 4. Final validity classification
    # ----------------------------
    is_valid = len(errors) == 0


    return DesignValidationResult(
        is_valid=is_valid,
        computed=computed,
        warnings=warnings,
        errors=errors,
        explanations=explanations,
    )
