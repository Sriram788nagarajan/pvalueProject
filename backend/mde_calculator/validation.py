from typing import List, Dict
from .schema import MDEInput


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.has_small_sample_warning = False

    def is_valid(self):
        return len(self.errors) == 0



# --------------------------------
# Field-level validation
# --------------------------------

def validate_mde_inputs(data: MDEInput) -> ValidationResult:
    result = ValidationResult()

    # ----------------------------
    # Variant checks
    # ----------------------------

    if len(data.variants) < 2:
        result.errors.append(
            "At least one control and one test variant are required."
        )

    controls = [v for v in data.variants if v.is_control]
    if len(controls) != 1:
        result.errors.append(
            "Exactly one control variant must be specified."
        )

    for v in data.variants:
        if v.n <= 0:
            result.errors.append(
                f"Sample size for variant '{v.name}' must be a positive integer."
            )

        if v.n < 30:
            result.warnings.append(
                f"Variant '{v.name}' has a small sample size (n < 30). "
                "Normal approximation may be unreliable, inflating uncertainty."
            )
            result.has_small_sample_warning = True


    # ----------------------------
    # Metric-specific checks
    # ----------------------------

    if data.metric_type == "binary" and data.design_type == "independent":
        if data.baseline_rate is None:
            result.errors.append(
                "Baseline conversion rate is required for independent binary metrics."
            )

        else:
            p = data.baseline_rate
            if p <= 0 or p >= 1:
                result.errors.append(
                    "Baseline conversion rate must be strictly between 0 and 1."
                )

        if data.design_type == "paired":
            result.warnings.append(
                "Paired binary MDE is an approximation based on discordant pairs. "
                "Results are suitable for planning, not exact inference."
            )

        if data.metric_type == "binary" and data.design_type == "paired":
            if data.discordance_rate is None:
                result.errors.append(
                    "Paired binary MDE requires an explicit estimate of discordant-pair probability "
                    "(p01 + p10). This cannot be inferred from baseline conversion rate."
                )
            elif not (0 < data.discordance_rate < 1):
                result.errors.append(
                    "Discordance rate (p01 + p10) must be strictly between 0 and 1."
                )


    if data.metric_type == "continuous":
        if data.std_dev is None:
            result.errors.append(
                "Standard deviation is required for continuous metrics."
            )
        elif data.std_dev <= 0:
            result.errors.append(
                "Standard deviation must be greater than zero."
            )

    # ----------------------------
    # Risk parameter checks
    # ----------------------------

    if not (0 < data.alpha < 1):
        result.errors.append("Alpha must be between 0 and 1.")

    if not (0 < data.power < 1):
        result.errors.append("Power must be between 0 and 1.")

    # ----------------------------
    # Design warnings
    # ----------------------------

    if data.design_type == "paired":
        control = controls[0]
        if control.n < 30:
            result.warnings.append(
                "Paired design with small sample size may lead to unstable "
                "variance estimates for differences."
            )

    return result
