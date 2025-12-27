import math
from typing import List, Dict


def guard_baseline_rate(p: float) -> List[Dict]:
    errors = []

    if not 0 < p < 1:
        errors.append({
            "code": "INVALID_BASELINE_RATE",
            "message": "Baseline rate must be strictly between 0 and 1."
        })

    if p < 0.01:
        errors.append({
            "code": "BASELINE_TOO_LOW",
            "message": "Baseline rate below 1% leads to unstable normal approximation."
        })

    if p > 0.99:
        errors.append({
            "code": "BASELINE_TOO_HIGH",
            "message": "Baseline rate above 99% leads to degenerate variance."
        })

    return errors


def guard_expected_lift(p0: float, lift: float) -> List[Dict]:
    errors = []

    if lift <= 0:
        errors.append({
            "code": "NON_POSITIVE_LIFT",
            "message": "Expected lift must be greater than zero."
        })

    if p0 + lift >= 1:
        errors.append({
            "code": "LIFT_EXCEEDS_PROBABILITY_SPACE",
            "message": "Baseline + lift must be less than 1."
        })

    if lift < 0.001:
        errors.append({
            "code": "LIFT_TOO_SMALL",
            "message": "Lift below 0.1% is not detectable with normal approximation."
        })

    return errors



def guard_alpha(alpha: float) -> List[Dict]:
    errors = []

    if not 0 < alpha < 0.2:
        errors.append({
            "code": "INVALID_ALPHA",
            "message": "Alpha must be between 0 and 0.2."
        })

    if alpha < 0.001:
        errors.append({
            "code": "ALPHA_TOO_STRICT",
            "message": "Alpha below 0.1% is impractical for product experiments."
        })

    return errors


def guard_power(power: float) -> List[Dict]:
    errors = []

    if not 0.5 <= power < 0.99:
        errors.append({
            "code": "INVALID_POWER",
            "message": "Power must be between 0.5 and 0.99."
        })

    return errors


def guard_traffic(daily_users: int, run_days: int, allocation: float) -> List[Dict]:
    errors = []

    if daily_users <= 0 or run_days <= 0:
        errors.append({
            "code": "INVALID_TRAFFIC_INPUT",
            "message": "Daily users and run days must be positive."
        })

    total_users = daily_users * run_days * allocation

    if total_users < 100:
        errors.append({
            "code": "INSUFFICIENT_TOTAL_SAMPLE",
            "message": "Fewer than 100 users per variant makes inference invalid."
        })

    return errors


def guard_mean_inputs(
    baseline_mean: float,
    expected_delta: float,
    assumed_std: float
) -> list:
    errors = []

    if assumed_std <= 0:
        errors.append({
            "code": "INVALID_STD_DEV",
            "message": "Assumed standard deviation must be positive."
        })

    if expected_delta == 0:
        errors.append({
            "code": "ZERO_EFFECT_SIZE",
            "message": "Expected mean difference must be non-zero."
        })

    if abs(expected_delta) < 0.01 * assumed_std:
        errors.append({
            "code": "EFFECT_TOO_SMALL",
            "message": "Expected effect is too small relative to variance."
        })

    return errors



def guard_binary_approximation(n: int, p: float):
    """
    Checks validity of normal approximation for proportion tests.
    Returns warnings (non-blocking).
    """
    warnings = []

    if n * p < 5 or n * (1 - p) < 5:
        warnings.append(
            "Low expected successes; normal approximation may be weak."
        )

    return warnings


def guard_continuous_sd(sd):
    """
    Checks validity of standard deviation for mean-based tests.
    Returns warnings (non-blocking).
    """
    warnings = []

    if sd is None:
        warnings.append(
            "Standard deviation missing; approximation used."
        )
    elif sd <= 0:
        warnings.append(
            "Non-positive standard deviation; results may be invalid."
        )

    return warnings
