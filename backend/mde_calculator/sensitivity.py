from typing import Dict, List
from .engine import MDEResult
from .schema import MDEInput
from . import formulas
import math


class MDESensitivityScenario:
    def __init__(
        self,
        name: str,
        new_mde: float,
        description: str,
    ):
        self.name = name
        self.new_mde = new_mde
        self.description = description


class MDESensitivityResult:
    def __init__(
        self,
        comparison_key: str,
        scenarios: List[MDESensitivityScenario],
    ):
        self.comparison_key = comparison_key
        self.scenarios = scenarios


# -----------------------------------------
# Sensitivity computation
# -----------------------------------------

def compute_sensitivity(
    result: MDEResult,
    data: MDEInput,
) -> MDESensitivityResult:
    """
    Computes what-if MDEs under different design changes
    for a single pairwise comparison.
    """

    scenarios: List[MDESensitivityScenario] = []

    # Shared z values
    zc = formulas.z_critical(data.alpha, data.test_direction)
    zp = formulas.z_power(data.power)

    # ---------------------------------
    # Select variance term by design
    # ---------------------------------

    if data.metric_type == "binary" and data.design_type == "independent":
        variance = data.baseline_rate * (1 - data.baseline_rate)

    elif data.metric_type == "binary" and data.design_type == "paired":
        variance = data.discordance_rate  # p01 + p10 (planning-only)

    elif data.metric_type == "continuous":
        variance = data.std_dev ** 2

    else:
        raise ValueError("Unsupported sensitivity configuration")


    # ---------------------------------
    # Scenario 1: Equal traffic
    # ---------------------------------

    n_equal = min(result.n_control, result.n_test)

    se_equal = math.sqrt(variance * (2 / n_equal))


    mde_equal = (zc + zp) * se_equal

    scenarios.append(
        MDESensitivityScenario(
            name="Equal traffic allocation",
            new_mde=mde_equal,
            description=(
                "Balances control and test sample sizes to improve "
                "statistical efficiency."
            ),
        )
    )

    # ---------------------------------
    # Scenario 2: Double test traffic
    # ---------------------------------

    n_test_double = result.n_test * 2

    se_double_test = math.sqrt(
        variance * (1 / result.n_control + 1 / n_test_double)
    )


    mde_double_test = (zc + zp) * se_double_test

    scenarios.append(
        MDESensitivityScenario(
            name="Double test traffic",
            new_mde=mde_double_test,
            description=(
                "Increases sensitivity by allocating more users to the test variant."
            ),
        )
    )

    # ---------------------------------
    # Scenario 3: Double total traffic
    # ---------------------------------

    n_control_double = result.n_control * 2
    n_test_double_total = result.n_test * 2

    se_double_total = math.sqrt(
        variance * (1 / n_control_double + 1 / n_test_double_total)
    )


    mde_double_total = (zc + zp) * se_double_total

    scenarios.append(
        MDESensitivityScenario(
            name="Double experiment duration",
            new_mde=mde_double_total,
            description=(
                "Collects more data overall, reducing uncertainty across variants."
            ),
        )
    )

    # ---------------------------------
    # Scenario 4: Reduce variance by 20%
    # ---------------------------------

    reduced_var = 0.8 * variance
    se_reduced_var = math.sqrt(
        reduced_var * (1 / result.n_control + 1 / result.n_test)
    )


    mde_reduced_var = (zc + zp) * se_reduced_var

    scenarios.append(
        MDESensitivityScenario(
            name="Reduce variance by 20%",
            new_mde=mde_reduced_var,
            description=(
                "Lower measurement noise improves detectability without "
                "changing traffic."
            ),
        )
    )

    comparison_key = f"{result.control_name}_vs_{result.test_name}"

    return MDESensitivityResult(
        comparison_key=comparison_key,
        scenarios=scenarios,
    )


# -----------------------------------------
# Batch sensitivity helper
# -----------------------------------------

def compute_all_sensitivities(
    results: List[MDEResult],
    data: MDEInput,
) -> Dict[str, MDESensitivityResult]:
    """
    Computes sensitivity scenarios for all pairwise MDE results.
    """

    output: Dict[str, MDESensitivityResult] = {}

    for r in results:
        res = compute_sensitivity(r, data)
        output[res.comparison_key] = res

    return output
