from typing import Dict, Any, List

from backend.sample_size_calculator.engine import compute_sample_sizes
from types import SimpleNamespace


def compute_sample_size_v1(
    *,
    metric_type: str,
    baseline_rate: float | None,
    std_dev: float | None,
    planned_traffic: Dict[str, int],
    alpha: float,
    power: float,
    test_direction: str,
    target_mde: float,
) -> Dict[str, Any]:
    """
    V2 → V1 adapter for Sample Size Calculator.

    - Builds canonical v1 SampleSizeInput
    - Calls v1 compute_sample_sizes
    - Normalizes output for Phase 3 Pillar 2
    """

    total_users = sum(planned_traffic.values())

    variants = []
    for name, n in planned_traffic.items():
        variants.append(
            SimpleNamespace(
                name=name,
                allocation_percent=(n / total_users) * 100,
                is_control=(name == "control")
            )
        )

    req = SimpleNamespace(
        outcome_type="binary" if metric_type == "binary" else "continuous",
        baseline_value=baseline_rate,
        variance=std_dev,
        mde=target_mde,
        alpha=alpha,
        power=power,
        test_direction=test_direction,
        variants=variants,
    )


    results = compute_sample_sizes(req)

    return {
        "required_sample_per_variant": {
            k: v for k, v in results.items() if k != "Total"
        },
        "required_total_sample": results["Total"],
        "engine": "v1_sample_size",
    }

    