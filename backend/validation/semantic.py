from backend.validation.stats.inputs import (
    HypothesisInputs,
    MeanMetricInputs,
    StatisticalPlan,
    TrafficAssumptions
)


def validate_semantics(payload: dict) -> dict:
    """
    Layer 2: Meaning validation + object construction.
    """

    metric_type = payload["metric_type"]

    statistical_plan = StatisticalPlan(**payload["statistical_plan"])
    traffic = TrafficAssumptions(**payload["traffic"])

    if metric_type == "proportion":
        hypothesis_inputs = HypothesisInputs(**payload["hypothesis"])

        return {
            "ok": True,
            "metric_type": metric_type,
            "hypothesis_inputs": hypothesis_inputs,
            "statistical_plan": statistical_plan,
            "traffic": traffic
        }

    if metric_type == "mean":
        mean_inputs = MeanMetricInputs(**payload["mean_metric"])

        return {
            "ok": True,
            "metric_type": metric_type,
            "mean_inputs": mean_inputs,
            "statistical_plan": statistical_plan,
            "traffic": traffic
        }

    return {
        "ok": False,
        "errors": [{
            "code": "UNSUPPORTED_METRIC_TYPE",
            "message": f"Unsupported metric type: {metric_type}"
        }]
    }


