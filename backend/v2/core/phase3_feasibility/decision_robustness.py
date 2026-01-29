from backend.v2.models.phase3_feasibility import (
    Phase3DecisionRobustnessResult,
    DecisionRobustnessSignal,
)


def validate_decision_robustness(
    *,
    snapshot: dict,
    detectability_result: dict,
) -> Phase3DecisionRobustnessResult:
    """
    Phase 3 – Pillar 4: Decision Robustness

    Evaluates whether the experiment is likely to yield
    a clear, actionable decision.
    """

    explanations = []
    signals = []
    actions = []

    design = snapshot.get("design_inputs") or {}

    target_mde = design.get("target_mde")
    test_direction = design.get("test_direction", "two_tailed")

    statistical_mde = detectability_result["computed"]["statistical_mde"]
    power_at_mwe = detectability_result["computed"]["power_at_minimum_worthwhile_effect"]

    # ----------------------------
    # 1. Decision Separation Ratio
    # ----------------------------
    decision_separation_ratio = statistical_mde / target_mde

    explanations.append(
        f"The minimum detectable effect is {decision_separation_ratio:.2f}× "
        f"the minimum worthwhile effect."
    )

    # ----------------------------
    # 2. Risk: Statistically significant but useless
    # ----------------------------
    if decision_separation_ratio <= 0.6 and power_at_mwe >= 0.8:
        signals.append(
            DecisionRobustnessSignal(
                code="SIGNIFICANT_BUT_USELESS",
                message=(
                    "The design is very sensitive and may detect effects "
                    "that are statistically significant but not meaningful."
                ),
            )
        )
        explanations.append(
            "High sensitivity increases the risk of shipping changes with negligible impact."
        )
        actions.append(
            "Consider increasing the minimum worthwhile effect or reframing success criteria."
        )

    # ----------------------------
    # 3. Risk: Directional but non-significant
    # ----------------------------
    if 0.6 < decision_separation_ratio <= 1.2 and power_at_mwe < 0.7:
        signals.append(
            DecisionRobustnessSignal(
                code="DIRECTIONAL_BUT_NON_SIGNIFICANT",
                message=(
                    "The experiment may show directional improvement "
                    "without reaching statistical significance."
                ),
            )
        )
        explanations.append(
            "Observed improvements may not be statistically reliable."
        )
        actions.append(
            "Increase sample size or duration to improve power at the business threshold."
        )

    # ----------------------------
    # 4. Knife-edge decisions
    # ----------------------------
    if 0.9 <= decision_separation_ratio <= 1.1:
        signals.append(
            DecisionRobustnessSignal(
                code="KNIFE_EDGE_DECISION",
                message=(
                    "Small fluctuations in results could change the final decision."
                ),
            )
        )
        explanations.append(
            "The design sits close to the decision boundary."
        )

    # ----------------------------
    # 5. Directional ambiguity
    # ----------------------------
    if test_direction == "two_tailed" and power_at_mwe < 0.75:
        explanations.append(
            "Using a two-sided test increases ambiguity when power is limited."
        )

    # ----------------------------
    # 6. Verdict resolution (NON-BLOCKING)
    # ----------------------------
    if len(signals) == 0 and power_at_mwe >= 0.8:
        verdict = "robust_decision"
    elif len(signals) <= 1:
        verdict = "fragile_decision"
    else:
        verdict = "weak_decision_signal"

    return Phase3DecisionRobustnessResult(
        is_valid=True,
        verdict=verdict,
        computed={
            "decision_separation_ratio": round(decision_separation_ratio, 3),
            "power_at_minimum_worthwhile_effect": round(power_at_mwe, 3),
        },
        signals=signals,
        explanations=explanations,
        recommended_actions=list(dict.fromkeys(actions)),  # de-dup
    )
