from typing import Dict, List
from .engine import MDEResult
from .explanation import MDEExplanation
from .sensitivity import MDESensitivityResult


# -----------------------------------------
# Helpers
# -----------------------------------------

def round_value(value: float, decimals: int) -> float:
    return round(value, decimals)


def verdict_for_mde(
    mde: float,
    baseline: float | None,
    std_dev: float | None,
    metric_type: str,
) -> str:
    """
    Returns one of: 'positive', 'neutral', 'negative'
    """
    if metric_type == "binary" and std_dev is None:
    # Paired binary has no interpretable effect-size ratio
        return "neutral"


    if metric_type == "binary" and baseline is not None:
        ratio = mde / baseline if baseline > 0 else float("inf")

        if ratio <= 0.01:
            return "positive"
        elif ratio <= 0.05:
            return "neutral"
        else:
            return "negative"

    if metric_type == "continuous" and std_dev is not None:
        ratio = mde / std_dev if std_dev > 0 else float("inf")

        if ratio <= 0.2:
            return "positive"
        elif ratio <= 0.5:
            return "neutral"
        else:
            return "negative"

    return "neutral"


# -----------------------------------------
# Serialization
# -----------------------------------------

def serialize_mde_result(
    result: MDEResult,
    explanation: MDEExplanation,
    sensitivity: MDESensitivityResult,
    metric_type: str,
    baseline: float | None,
    std_dev: float | None,
) -> Dict:
    """
    Serializes a single pairwise MDE result into UI-ready JSON.
    """

    if metric_type == "binary":
        mde_display = round_value(result.mde, 4)
    else:
        mde_display = round_value(result.mde, 2)

    verdict = verdict_for_mde(
        mde=result.mde,
        baseline=baseline,
        std_dev=std_dev,
        metric_type=metric_type,
    )

    return {
        "comparison": f"{result.control_name} vs {result.test_name}",
        "mde": {
            "value": mde_display,
            "raw": result.mde,
            "units": "absolute",
        },
        "sample_sizes": {
            "control": result.n_control,
            "test": result.n_test,
        },
        "statistics": {
            "standard_error": round_value(result.se, 6),
            "z_critical": round_value(result.z_crit, 4),
            "z_power": round_value(result.z_power, 4),
        },
        "verdict": verdict,

        "explanation": {
            "has_small_sample_warning": explanation.has_small_sample_warning,
            "has_paired_approximation": explanation.has_paired_approximation,
            
        },
        
        "sensitivity": [
            {
                "name": s.name,
                "new_mde": round_value(s.new_mde, 4 if metric_type == "binary" else 2),
                "description": s.description,
            }
            for s in sensitivity.scenarios
        ],
    }


def serialize_all_results(
    results: List[MDEResult],
    explanations: Dict[str, MDEExplanation],
    sensitivities: Dict[str, MDESensitivityResult],
    metric_type: str,
    baseline: float | None,
    std_dev: float | None,
) -> List[Dict]:
    """
    Serializes all pairwise MDE results.
    """

    output: List[Dict] = []

    for r in results:
        key = f"{r.control_name}_vs_{r.test_name}"
        output.append(
            serialize_mde_result(
                result=r,
                explanation=explanations[key],
                sensitivity=sensitivities[key],
                metric_type=metric_type,
                baseline=baseline,
                std_dev=std_dev,
            )
        )

    return output
