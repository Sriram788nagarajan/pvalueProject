import math
from scipy.stats import norm


# ----------------------------------------
# Z-value helpers
# ----------------------------------------

def z_critical(alpha: float, test_direction: str) -> float:
    """
    Returns the critical z value based on alpha and tail direction.
    """
    if test_direction == "two_tailed":
        return norm.ppf(1 - alpha / 2)
    elif test_direction == "one_tailed":
        return norm.ppf(1 - alpha)
    else:
        raise ValueError("Invalid test direction.")


def z_power(power: float) -> float:
    """
    Returns the z value corresponding to desired power (1 - beta).
    """
    return norm.ppf(power)


# ----------------------------------------
# Binary — Independent samples
# ----------------------------------------

def mde_binary_independent(
    p: float,
    n_control: int,
    n_test: int,
    alpha: float,
    power: float,
    test_direction: str,
) -> float:
    """
    Minimum detectable absolute difference in proportions.
    """
    se = math.sqrt(p * (1 - p) * (1 / n_control + 1 / n_test))
    zc = z_critical(alpha, test_direction)
    zp = z_power(power)
    return (zc + zp) * se


# ----------------------------------------
# Continuous — Independent samples
# ----------------------------------------

def mde_continuous_independent(
    sigma: float,
    n_control: int,
    n_test: int,
    alpha: float,
    power: float,
    test_direction: str,
) -> float:
    """
    Minimum detectable absolute difference in means.
    """
    se = sigma * math.sqrt(1 / n_control + 1 / n_test)
    zc = z_critical(alpha, test_direction)
    zp = z_power(power)
    return (zc + zp) * se


# ----------------------------------------
# Continuous — Paired samples
# ----------------------------------------

def mde_continuous_paired(
    sigma_d: float,
    n: int,
    alpha: float,
    power: float,
    test_direction: str,
) -> float:
    """
    Minimum detectable mean difference for paired design.
    """
    se = sigma_d / math.sqrt(n)
    zc = z_critical(alpha, test_direction)
    zp = z_power(power)
    return (zc + zp) * se


# ----------------------------------------
# Binary — Paired samples (Approximate)
# ----------------------------------------

def mde_binary_paired_approx(
    p01: float,
    p10: float,
    n: int,
    alpha: float,
    power: float,
    test_direction: str,
) -> float:
    """
    Approximate MDE for paired binary outcomes (planning only).
    """
    se = math.sqrt((p01 + p10) / n)
    zc = z_critical(alpha, test_direction)
    zp = z_power(power)
    return (zc + zp) * se
