## This is a temporary test file for validation stats module . Not a production code.

from backend.validation.stats.inputs import *
from backend.validation.stats.power_analysis import analyze_power_and_sample_size
from backend.validation.stats.verdicts import classify_statistical_risk


hypothesis = HypothesisInputs(
    baseline_rate=0.12,
    expected_lift=0.02
)

plan = StatisticalPlan(
    alpha=0.05,
    power=0.8,
    test_type="two_tailed"
)

traffic = TrafficAssumptions(
    daily_users=1000,
    run_days=14,
    allocation=0.5
)

results = analyze_power_and_sample_size(hypothesis, plan, traffic)

verdict = classify_statistical_risk(
    planned_n=results["planned_sample_per_variant"],
    required_n=results["required_sample_per_variant"],
    achieved_power=results["achieved_power"],
    desired_power=plan.power
)

print(results)
print(verdict)
