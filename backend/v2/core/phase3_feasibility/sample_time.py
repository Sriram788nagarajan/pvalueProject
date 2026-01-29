from backend.v2.services.sample_size_service import compute_sample_size_v1
from backend.v2.models.phase3_feasibility import Phase3SampleTimeResult


DEFAULT_DURATION_DAYS = 30


def validate_sample_time_feasibility(
    *,
    snapshot: dict,

) -> Phase3SampleTimeResult:

    warnings = []
    explanations = []

    design = snapshot.get("design_inputs") or {}

    metric_type = snapshot["metric_type"]
    design_type = design.get("design_type")
    planned_traffic = design.get("planned_traffic")
    baseline_obj = design.get("baseline")
    baseline = baseline_obj.get("value") if isinstance(baseline_obj, dict) else baseline_obj
    std_dev = design.get("std_dev")
    alpha = design.get("alpha")
    power = design.get("power")
    target_mde = design.get("target_mde")
    test_direction = design.get("test_direction", "two_tailed")

    if not planned_traffic:
        return Phase3SampleTimeResult(
            is_valid=False,
            computed={},
            warnings=[],
            errors=[{
                "code": "NO_PLANNED_TRAFFIC",
                "message": "Planned traffic is required for sample-time feasibility."
            }],
            explanations=["Sample-time feasibility cannot be evaluated without traffic inputs."]
        )

    # ----------------------------
    # 1. Required sample (v1)
    # ----------------------------
    sample_result = compute_sample_size_v1(
    metric_type=metric_type,
    baseline_rate=baseline,
    std_dev=std_dev,
    planned_traffic=planned_traffic,   # ✅ REQUIRED
    target_mde=target_mde,
    alpha=alpha,
    power=power,
    test_direction=test_direction,
        )


    

    required = sample_result["required_sample_per_variant"]


    # ----------------------------
    # 2. Duration resolution
    # ----------------------------
    design = snapshot.get("design_inputs") or {}

    planned_duration_days = design.get("duration_days")

    if planned_duration_days is not None:
        duration_days = planned_duration_days
        duration_source = "user"
    else:
        duration_days = DEFAULT_DURATION_DAYS
        duration_source = "assumed"


    # ----------------------------
    # 3. Time-to-sample
    # ----------------------------
    time_to_completion = 0.0
    time_per_variant = {}

    for variant, planned_n in planned_traffic.items():
        daily = planned_n / duration_days
        days_needed = required[variant] / daily
        time_per_variant[variant] = round(days_needed, 1)
        time_to_completion = max(time_to_completion, days_needed)

    # ----------------------------
    # 4. Verdict logic
    # ----------------------------
    if time_to_completion <= duration_days:
        verdict = "feasible"
    elif time_to_completion <= 2 * duration_days:
        verdict = "borderline"
        warnings.append({
            "code": "LONG_DURATION",
            "message": "The experiment may take significantly longer than planned."
        })
    else:
        verdict = "not_feasible"
        warnings.append({
            "code": "EXCESSIVE_DURATION",
            "message": "The experiment is unlikely to complete in a reasonable time."
        })

    explanations.append(
        f"Based on the current design, the experiment is expected to reach "
        f"the required sample size in approximately {round(time_to_completion, 1)} days."
    )

    required_per_variant = max(required.values())
    required_daily = required_per_variant / duration_days

    explanations.append(
    f"To make this experiment feasible within {duration_days} days, you would need "
    f"approximately {round(required_per_variant):,} users per variant "
    f"(about {round(required_daily, 1)} users per day per variant)."
    )

    


    if duration_source == "assumed":
        explanations.append(
            "This estimate assumes a 30-day run because no duration was specified."
        )

    return Phase3SampleTimeResult(
        is_valid=True,
        computed={
            "required_sample_per_variant": required,
            "planned_sample_per_variant": planned_traffic,
            "duration_days": duration_days,
            "duration_source": duration_source,
            "time_to_completion_days": round(time_to_completion, 1),
            "time_per_variant_days": time_per_variant,
            "time_feasibility_verdict": verdict,
        },
        warnings=warnings,
        errors=[],
        explanations=explanations,
    )
