from typing import Dict, List
from .engine import MDEResult
from .schema import MDEInput
from .integrity import IntegrityResult
from .validation import ValidationResult


# -----------------------------------------
# Explanation object (internal)
# -----------------------------------------

class MDEExplanation:
    def __init__(
        self,
        *,
        has_small_sample_warning: bool = False,
        has_paired_approximation: bool = False,
    ):
        self.has_small_sample_warning = has_small_sample_warning
        self.has_paired_approximation = has_paired_approximation


# -----------------------------------------
# Explanation generator
# -----------------------------------------

def explain_mde_result(
    result: MDEResult,
    data: MDEInput,
    integrity: IntegrityResult,
    validation: ValidationResult,
) -> MDEExplanation:
    """
    Generates a human-readable explanation for a single pairwise MDE result.
    """

    # ----------------------------
    # Headline
    # ----------------------------

    headline = (
        f"The experiment can reliably detect changes of at least "
        f"{result.mde:.4f} (absolute units) between "
        f"{result.control_name} and {result.test_name}."
    )

    # ----------------------------
    # Interpretation
    # ----------------------------

    interpretation = (
        f"With the current traffic and variability, only effects at or above "
        f"{result.mde:.4f} are expected to cross the statistical threshold "
        f"defined by {int(data.power * 100)}% power and "
        f"{int((1 - data.alpha) * 100)}% confidence. "
        f"Smaller effects may exist but cannot be distinguished from random "
        f"noise using this design."
    )

    # ----------------------------
    # Blind spot
    # ----------------------------

    blind_spot = (
        f"Any real improvement smaller than {result.mde:.4f} will likely "
        f"appear as statistically inconclusive in this experiment."
    )

    # ----------------------------
    # Drivers (why MDE is this size)
    # ----------------------------

    drivers: List[str] = []

    if result.n_test != result.n_control:
        drivers.append(
            "Unequal traffic allocation between control and test increases "
            "uncertainty and worsens detectability."
        )

    if data.metric_type == "binary":
        drivers.append(
            "Binary metrics are inherently noisy, especially near 50% "
            "conversion, which increases the minimum detectable effect."
        )

    if data.metric_type == "continuous":
        drivers.append(
            "Higher natural variability in the metric directly increases the "
            "minimum detectable effect."
        )

    # ----------------------------
    # Risks & warnings
    # ----------------------------

    risks: List[str] = []

    for w in validation.warnings:
        risks.append(w)

    for w in integrity.warnings:
        risks.append(w)

    if data.design_type == "paired" and data.metric_type == "binary":
        risks.append(
            "Paired binary MDE is based on an approximation and should be "
            "used only for planning, not precise inference."
        )

    return MDEExplanation(
    has_small_sample_warning=validation.has_small_sample_warning,
    has_paired_approximation=integrity.has_paired_binary_approximation,
    )


# -----------------------------------------
# Batch explanation helper
# -----------------------------------------

def explain_all_results(
    results: List[MDEResult],
    data: MDEInput,
    integrity: IntegrityResult,
    validation: ValidationResult,
) -> Dict[str, MDEExplanation]:
    """
    Generates explanations for all pairwise MDE results.
    """

    explanations: Dict[str, MDEExplanation] = {}

    for r in results:
        key = f"{r.control_name}_vs_{r.test_name}"
        explanations[key] = explain_mde_result(
            result=r,
            data=data,
            integrity=integrity,
            validation=validation,
        )

    return explanations
