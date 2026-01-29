from backend.validation.stats.formulas import (
    z_test_proportion,
    welch_t_test,
    paired_t_test,
    mcnemar_test,
    mcnemar_ci,
    mcnemar_exact_test

)
from backend.validation.stats.guards import (
    guard_binary_approximation,
    guard_continuous_sd
)
from backend.validation.stats.verdicts import interpret

from scipy.stats import norm, t


def to_python(value):
    """
    Convert numpy / scipy scalar types to native Python types
    for JSON serialization.
    """
    try:
        import numpy as np
        if isinstance(value, np.generic):
            return value.item()
    except ImportError:
        pass

    return value



def run_inference(payload):
    """
    Phase 3 v1 Statistical Inference Engine
    """

    warnings = []
    results = []

    alpha = 1 - payload.settings.confidence_level
    control = payload.control

    # =========================================================
# Paired binary metric (McNemar) — handled separately
# =========================================================
    if payload.metric_type == "binary" and payload.data_structure == "paired":

        if payload.mcnemar is None:
            return [{
                "test_id": "paired_binary",
                "test_used": "unsupported_paired_binary",
                "lift_absolute": None,
                "lift_relative": None,
                "confidence_interval": [None, None],
                "p_value": 1.0,
                "statistic": 0.0,
                "significant": False,
                "interpretation": (
                    "Paired conversion analysis requires counts of users whose "
                    "conversion status changed (before → after)."
                )
            }], []

        b = payload.mcnemar.b
        c = payload.mcnemar.c

        if b + c < 25:
            stat, p_value = mcnemar_exact_test(b, c)
            test_used = "mcnemar_exact"
        else:
            stat, p_value = mcnemar_test(b, c)
            test_used = "mcnemar_chi_square"

        lift = c - b
        ci_low, ci_high = mcnemar_ci(b, c, alpha)
        ci = [ci_low, ci_high]

        significant = p_value < alpha

        return [{
            "test_id": "paired_binary",
            "test_used": test_used,
            "lift_absolute": to_python(lift),
            "lift_relative": None,
            "confidence_interval": ci,
            "p_value": to_python(p_value),
            "statistic": to_python(stat),
            "significant": bool(significant),
            "interpretation": interpret(
                bool(significant),
                to_python(lift),
                payload.settings.minimum_effect
            )
        }], []



    for test in payload.tests:


        # -------------------------
            # Binary metric (independent only)
        # -------------------------
        if payload.metric_type == "binary":

            # Convert counts -> proportions (EXPLICIT CONTRACT)
            p_control = control.value / control.n
            p_test = test.value / test.n

            # Guards now receive proportions
            warnings.extend(
                guard_binary_approximation(control.n, p_control)
            )
            warnings.extend(
                guard_binary_approximation(test.n, p_test)
            )

            stat, p_value, se = z_test_proportion(
                p_control,
                control.n,
                p_test,
                test.n,
                payload.settings.tail
            )

            lift = p_test - p_control
            ci_margin = norm.ppf(1 - alpha / 2) * se
            ci = [lift - ci_margin, lift + ci_margin]

            test_used = "two_sample_proportion_z_test"


        # -------------------------
        # Continuous metric
        # -------------------------
        else:

            # Paired continuous
            if payload.data_structure == "paired":
                mean_diff = test.value - control.value
                sd_diff = test.sd  # v1 approximation

                stat, p_value, se, df = paired_t_test(
                    mean_diff,
                    sd_diff,
                    test.n,
                    payload.settings.tail
                )

                lift = mean_diff
                ci_margin = t.ppf(1 - alpha / 2, df) * se if se else 0.0
                ci = [lift - ci_margin, lift + ci_margin]

                test_used = "paired_t_test"

            # Independent continuous
            else:
                warnings.extend(guard_continuous_sd(control.sd))
                warnings.extend(guard_continuous_sd(test.sd))

                stat, p_value, se, df = welch_t_test(
                    control.value,
                    control.sd or 1.0,
                    control.n,
                    test.value,
                    test.sd or 1.0,
                    test.n,
                    payload.settings.tail
                )

                lift = test.value - control.value
                ci_margin = t.ppf(1 - alpha / 2, df) * se
                ci = [lift - ci_margin, lift + ci_margin]

                test_used = "welch_t_test"

        # -------------------------
        # Final result packaging
        # -------------------------
        significant = p_value < alpha

        results.append({
            "test_id": test.id,
            "test_used": test_used,
            "lift_absolute": to_python(lift),
            "lift_relative": (
                to_python(lift / (control.value / control.n))
                if control.value and control.n else None
            ),
            "confidence_interval": [
                to_python(ci[0]),
                to_python(ci[1])
            ],
            "p_value": to_python(p_value),
            "statistic": to_python(stat),
            "significant": bool(to_python(significant)),
            "interpretation": interpret(
                bool(to_python(significant)),
                to_python(lift),
                payload.settings.minimum_effect
            )
        })

    return results, list(set(warnings))
