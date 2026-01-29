from backend.v2.models.phase3_risk_disclosure import (
    Phase3RiskDisclosureResult,
    RiskDisclosureItem,
    ApproximationItem,
)


def evaluate_risk_disclosure(
    *,
    snapshot: dict,
    detectability_result: dict,
    sample_time_result: dict,
):
    design = snapshot.get("design_inputs", {})

    assumptions = []
    approximations = []
    fragilities = []
    invalidations = []

    # ----------------------------
    # Explicit assumptions
    # ----------------------------
    assumptions.append(
        RiskDisclosureItem(
            code="STABLE_TRAFFIC",
            statement=(
                "Daily traffic is assumed to remain stable throughout the "
                "experiment duration."
            ),
            source="sample_time",
        )
    )

    assumptions.append(
        RiskDisclosureItem(
            code="BASELINE_ACCURACY",
            statement=(
                "The baseline metric value entered is assumed to be a "
                "reasonable estimate of the true baseline."
            ),
            source="design",
        )
    )

    if design.get("test_direction") == "two_tailed":
        assumptions.append(
            RiskDisclosureItem(
                code="SYMMETRIC_EFFECTS",
                statement=(
                    "Positive and negative effects are treated as equally "
                    "likely and equally important."
                ),
                source="design",
            )
        )

    # ----------------------------
    # Approximations
    # ----------------------------
    approximations.append(
        ApproximationItem(
            code="NORMAL_APPROXIMATION",
            statement=(
                "Power and minimum detectable effect calculations rely on "
                "normal approximation methods."
            ),
            impact=(
                "Results may be slightly inaccurate for very small sample sizes "
                "or extreme baseline rates."
            ),
        )
    )

    approximations.append(
        ApproximationItem(
            code="LINEARIZED_POWER_AT_MWE",
            statement=(
                "Power at the minimum worthwhile effect is estimated using "
                "a linearized approximation."
            ),
            impact=(
                "Exact power may differ slightly, especially when the minimum "
                "worthwhile effect is close to the statistical detection limit."
            ),
        )
    )

    # ----------------------------
    # Known fragilities
    # ----------------------------
    baseline_sensitivity = detectability_result.get("computed", {}).get(
        "baseline_sensitivity", []
    )

    if baseline_sensitivity:
        fragilities.append(
            RiskDisclosureItem(
                code="BASELINE_SENSITIVITY",
                statement=(
                    "Detectability varies meaningfully across plausible baseline "
                    "scenarios, indicating sensitivity to baseline uncertainty."
                ),
                source="detectability",
            )
        )

    if sample_time_result.get("computed", {}).get("time_feasibility_verdict") != "feasible":
        fragilities.append(
            RiskDisclosureItem(
                code="TIME_PRESSURE",
                statement=(
                    "The experiment timeline is tight, increasing the risk of "
                    "early termination or underpowered results."
                ),
                source="sample_time",
            )
        )

    # ----------------------------
    # Invalidation conditions
    # ----------------------------
    invalidations.append(
        RiskDisclosureItem(
            code="TRAFFIC_DROP",
            statement=(
                "A sustained traffic drop of more than ~20% would invalidate "
                "sample size and timing conclusions."
            ),
            source="sample_time",
        )
    )

    invalidations.append(
        RiskDisclosureItem(
            code="METRIC_DEFINITION_CHANGE",
            statement=(
                "Any change to metric definition, logging, or attribution "
                "during the experiment would invalidate results."
            ),
            source="global",
        )
    )

    return Phase3RiskDisclosureResult(
        explicit_assumptions=assumptions,
        approximations=approximations,
        known_fragilities=fragilities,
        invalidation_conditions=invalidations,
    )
