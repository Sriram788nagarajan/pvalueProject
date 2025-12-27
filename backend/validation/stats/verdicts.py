def classify_statistical_risk(
    planned_n: int,
    required_n: int,
    achieved_power: float,
    desired_power: float
) -> dict:
    """
    Converts math into product decisions.
    """

    if planned_n < required_n * 0.5:
        return {
            "status": "BLOCKED",
            "reason": "Severely underpowered experiment"
        }

    if achieved_power < desired_power:
        return {
            "status": "RISKY",
            "reason": "Planned sample size cannot achieve desired power"
        }

    return {
        "status": "VALID",
        "reason": "Statistical design is feasible"
    }


def classify_statistical_risk(result: dict, desired_power: float) -> dict:
    if result["status"] == "BLOCKED":
        return {
            "status": "BLOCKED",
            "reason": "Invalid statistical assumptions",
            "errors": result["errors"]
        }

    planned_n = result["planned_sample_per_variant"]
    required_n = result["required_sample_per_variant"]
    achieved_power = result["achieved_power"]

    if planned_n < required_n * 0.5:
        return {
            "status": "BLOCKED",
            "reason": "Severely underpowered experiment"
        }

    if achieved_power < desired_power:
        return {
            "status": "RISKY",
            "reason": "Planned sample size cannot achieve desired power"
        }

    return {
        "status": "VALID",
        "reason": "Statistical design is feasible"
    }


def interpret(significant: bool, lift: float, minimum_effect: float | None):
    """
    Phase 3 inference interpretation.
    Converts statistical outcome into a human-readable explanation.
    """
    if significant:
        if minimum_effect is not None and abs(lift) < minimum_effect:
            return "Statistically significant but effect size is small."
        return "Statistically significant lift detected."
    else:
        if abs(lift) > 0:
            return "No statistical significance; results are inconclusive."
        return "No meaningful difference detected."
