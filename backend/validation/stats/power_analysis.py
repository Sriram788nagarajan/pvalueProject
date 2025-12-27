from .inputs import (
    StatisticalPlan,
    HypothesisInputs,
    TrafficAssumptions
)
from .formulas import (
    required_sample_size_proportion,
    achieved_power_proportion,
    required_sample_size_mean,
    achieved_power_mean
)
from .guards import (
    guard_baseline_rate,
    guard_expected_lift,
    guard_alpha,
    guard_power,
    guard_traffic,
    guard_mean_inputs
)






def planned_sample_per_variant(traffic: TrafficAssumptions) -> int:
    total_users = traffic.daily_users * traffic.run_days
    return int(total_users * traffic.allocation)


def analyze_power_and_sample_size(
    hypothesis,
    plan,
    traffic
) -> dict:
    """
    Layer 3: Statistical feasibility analysis with guards.
    """

    errors = []

    errors.extend(guard_baseline_rate(hypothesis.baseline_rate))
    errors.extend(guard_expected_lift(
        hypothesis.baseline_rate,
        hypothesis.expected_lift
    ))
    errors.extend(guard_alpha(plan.alpha))
    errors.extend(guard_power(plan.power))
    errors.extend(guard_traffic(
        traffic.daily_users,
        traffic.run_days,
        traffic.allocation
    ))

    if errors:
        return {
            "status": "BLOCKED",
            "errors": errors
        }

    # ---- SAFE TO COMPUTE MATH BELOW ----

    two_tailed = plan.test_type == "two_tailed"
    planned_n = planned_sample_per_variant(traffic)

    required_n = required_sample_size_proportion(
        p0=hypothesis.baseline_rate,
        lift=hypothesis.expected_lift,
        alpha=plan.alpha,
        power=plan.power,
        two_tailed=two_tailed
    )

    achieved_power = achieved_power_proportion(
        p0=hypothesis.baseline_rate,
        lift=hypothesis.expected_lift,
        alpha=plan.alpha,
        n_per_variant=planned_n,
        two_tailed=two_tailed
    )

    return {
        "status": "OK",
        "planned_sample_per_variant": planned_n,
        "required_sample_per_variant": required_n,
        "achieved_power": float(round(achieved_power, 3))
    }



def analyze_mean_metric(
    mean_inputs,
    plan,
    traffic
) -> dict:
    errors = []

    errors.extend(guard_mean_inputs(
        mean_inputs.baseline_mean,
        mean_inputs.expected_delta,
        mean_inputs.assumed_std
    ))

    if errors:
        return {
            "status": "BLOCKED",
            "errors": errors
        }

    two_tailed = plan.test_type == "two_tailed"
    planned_n = planned_sample_per_variant(traffic)

    required_n = required_sample_size_mean(
        std_dev=mean_inputs.assumed_std,
        delta=mean_inputs.expected_delta,
        alpha=plan.alpha,
        power=plan.power,
        two_tailed=two_tailed
    )

    achieved_power = achieved_power_mean(
        std_dev=mean_inputs.assumed_std,
        delta=mean_inputs.expected_delta,
        alpha=plan.alpha,
        n_per_variant=planned_n,
        two_tailed=two_tailed
    )

    return {
        "status": "OK",
        "planned_sample_per_variant": planned_n,
        "required_sample_per_variant": required_n,
        "achieved_power": float(round(achieved_power, 3))
    }
