from typing import List, Dict

from backend.v2.services.mde_service import compute_mde_v1

POWER_APPROXIMATION_NOTE = (
    "Power values are computed using a linearized normal-approximation "
    "around the design MDE. This is an approximation for visualization, "
    "not an exact power calculation."
)


def compute_power_grid(
    *,
    snapshot: dict,
    effect_values: List[float],
) -> List[Dict[str, float]]:

    design_inputs = snapshot.get("design_inputs") or {}

    metric_type = snapshot["metric_type"]
    design_type = design_inputs.get("design_type")
    planned_traffic = design_inputs.get("planned_traffic")
    
    raw_baseline = design_inputs.get("baseline")

    baseline = (
        raw_baseline.get("value")
        if isinstance(raw_baseline, dict)
        else raw_baseline
    )


    std_dev = design_inputs.get("std_dev")
    alpha = design_inputs.get("alpha")
    target_power = design_inputs.get("power")
    test_direction = design_inputs.get("test_direction", "two_tailed")

    if not planned_traffic:
        raise ValueError("Planned traffic missing")

    # ----------------------------
    # 1. Run MDE engine ONCE
    # ----------------------------
    mde_result = compute_mde_v1(
        metric_type=metric_type,
        design_type=design_type,
        baseline_rate=baseline,
        std_dev=std_dev,
        discordance_rate=None,
        planned_traffic=planned_traffic,
        alpha=alpha,
        power=target_power,
        test_direction=test_direction,
    )

    if not mde_result["valid"]:
        raise ValueError("Invalid design for power grid computation")

    pairwise = mde_result["pairwise_results"]
    max_mde = max(r["mde"] for r in pairwise)

    # ----------------------------
    # 2. Compute power per effect
    # ----------------------------
    results = []

    for effect in effect_values:
        if effect <= 0:
            raise ValueError("Effect sizes must be positive")

        power_at_effect = min(1.0, target_power * (effect / max_mde))

        results.append({
            "effect": effect,
            "power": power_at_effect,
        })

    return results
