from typing import List, Dict
from .schema import MDEInput
from .integrity import IntegrityResult, PairwiseComparison
from . import formulas


# -----------------------------------------
# Engine output record (internal)
# -----------------------------------------

class MDEResult:
    def __init__(
        self,
        control_name: str,
        test_name: str,
        n_control: int,
        n_test: int,
        se: float,
        z_crit: float,
        z_power: float,
        mde: float,
    ):
        self.control_name = control_name
        self.test_name = test_name
        self.n_control = n_control
        self.n_test = n_test
        self.se = se
        self.z_crit = z_crit
        self.z_power = z_power
        self.mde = mde


# -----------------------------------------
# Core engine
# -----------------------------------------

def run_mde_engine(
    data: MDEInput,
    integrity: IntegrityResult,
) -> List[MDEResult]:
    """
    Computes pairwise MDEs for each test variant vs control.
    Assumes validation + integrity checks have already passed.
    """

    results: List[MDEResult] = []

    for comp in integrity.comparisons:
        # ----------------------------
        # Z-values (shared)
        # ----------------------------
        zc = formulas.z_critical(data.alpha, data.test_direction)
        zp = formulas.z_power(data.power)

        # ----------------------------
        # Select formula
        # ----------------------------

        if data.metric_type == "binary" and data.design_type == "independent":
            se = (
                (data.baseline_rate * (1 - data.baseline_rate))
                * (1 / comp.n_control + 1 / comp.n_test)
            ) ** 0.5

            mde = formulas.mde_binary_independent(
                p=data.baseline_rate,
                n_control=comp.n_control,
                n_test=comp.n_test,
                alpha=data.alpha,
                power=data.power,
                test_direction=data.test_direction,
            )

        elif data.metric_type == "continuous" and data.design_type == "independent":
            se = data.std_dev * (
                (1 / comp.n_control + 1 / comp.n_test) ** 0.5
            )

            mde = formulas.mde_continuous_independent(
                sigma=data.std_dev,
                n_control=comp.n_control,
                n_test=comp.n_test,
                alpha=data.alpha,
                power=data.power,
                test_direction=data.test_direction,
            )

        elif data.metric_type == "continuous" and data.design_type == "paired":
            se = data.std_dev / (comp.n_control ** 0.5)

            mde = formulas.mde_continuous_paired(
                sigma_d=data.std_dev,
                n=comp.n_control,
                alpha=data.alpha,
                power=data.power,
                test_direction=data.test_direction,
            )

        elif data.metric_type == "binary" and data.design_type == "paired":
            # NOTE: baseline_rate not used here
            # p01 and p10 are expected to be passed via std_dev field
            # (advanced / approximate mode)
            d = data.discordance_rate  # p01 + p10

            se = (d / comp.n_control) ** 0.5

            mde = (zc + zp) * se

        else:
            raise ValueError(
                f"Unsupported MDE configuration: "
                f"{data.metric_type}, {data.design_type}"
            )

        # ----------------------------
        # Collect result
        # ----------------------------

        results.append(
            MDEResult(
                control_name=comp.control_name,
                test_name=comp.test_name,
                n_control=comp.n_control,
                n_test=comp.n_test,
                se=se,
                z_crit=zc,
                z_power=zp,
                mde=mde,
            )
        )

    return results
