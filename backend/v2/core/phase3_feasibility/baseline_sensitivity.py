from backend.v2.services.mde_service import compute_mde_v1

BASELINE_SCENARIOS = {
    "lower_than_expected": 0.8,
    "as_expected": 1.0,
    "higher_than_expected": 1.2,
}


def compute_baseline_sensitivity(
    *,
    snapshot: dict,
    minimum_worthwhile_effect: float,
):
    design_inputs = snapshot.get("design_inputs") or {}
    baseline_obj = design_inputs.get("baseline")

    # Sensitivity only applies to binary metrics with baseline
    if not baseline_obj:
        return None

    if snapshot.get("metric_type") != "binary":
        return None

    baseline = baseline_obj.get("value")
    if baseline is None:
        return None

    results = []

    for label, multiplier in BASELINE_SCENARIOS.items():
        assumed_baseline = max(min(baseline * multiplier, 0.999999), 1e-6)

        mde_result = compute_mde_v1(
            metric_type="binary",
            design_type=design_inputs.get("design_type"),
            baseline_rate=assumed_baseline,
            std_dev=None,
            discordance_rate=None,
            planned_traffic=design_inputs.get("planned_traffic"),
            alpha=design_inputs.get("alpha"),
            power=design_inputs.get("power"),
            test_direction=design_inputs.get("test_direction", "two_tailed"),
        )

        if not mde_result["valid"]:
            continue

        max_mde = max(r["mde"] for r in mde_result["pairwise_results"])

        power_at_mwe = min(
            1.0,
            design_inputs["power"] * (minimum_worthwhile_effect / max_mde),
        )

        if power_at_mwe >= design_inputs["power"]:
            verdict = "feasible"
        elif power_at_mwe >= 0.6:
            verdict = "borderline"
        else:
            verdict = "not_feasible"

        results.append({
            "scenario": label,
            "assumed_baseline": assumed_baseline,
            "statistical_mde": max_mde,
            "power_at_mwe": power_at_mwe,
            "verdict": verdict,
        })

    return results
