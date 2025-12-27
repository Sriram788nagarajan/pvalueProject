import math 
from scipy.stats import norm, t, chi2 , binom

def normal_cdf(z: float) -> float:
    """
    Standard normal cumulative distribution function.
    Φ(z)
    """
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def z_alpha(alpha: float, two_tailed: bool) -> float:
    """
    Returns critical Z value for alpha.
    """
    if two_tailed:
        return norm.ppf(1- alpha/2 )
    return norm.ppf(1 - alpha)


def z_beta(power: float) -> float:
    """
    Returns Z value corresponding to desired power (1 - beta).
    """
    return norm.ppf(power)


def bernoulli_variance(p: float) -> float:
    """
    Variance of a Bernoulli random variable.
    """
    return p * (1 - p)


def required_sample_size_proportion(
    p0: float,
    lift: float,
    alpha: float,
    power: float,
    two_tailed: bool
) -> int:
    """
    Computes required sample size per variant for a two-sample
    test of proportions using normal approximation.
    """
    p1 = p0 + lift

    z_a = z_alpha(alpha, two_tailed)
    z_b = z_beta(power)

    var0 = bernoulli_variance(p0)
    var1 = bernoulli_variance(p1)

    numerator = (z_a * math.sqrt(2 * var0) + z_b * math.sqrt(var0 + var1)) ** 2
    denominator = (p1 - p0) ** 2

    return math.ceil(numerator / denominator)



def achieved_power_proportion(
    p0: float,
    lift: float,
    alpha: float,
    n_per_variant: int,
    two_tailed: bool
) -> float:
    """
    Computes achieved power given fixed sample size.
    """
    p1 = p0 + lift

    z_a = z_alpha(alpha, two_tailed)
    var0 = bernoulli_variance(p0)
    var1 = bernoulli_variance(p1)

    pooled_std = math.sqrt((var0 + var1) / n_per_variant)
    effect = abs(p1 - p0)

    z_effect = effect / pooled_std
    return norm.cdf(z_effect - z_a)


def required_sample_size_mean(
    std_dev: float,
    delta: float,
    alpha: float,
    power: float,
    two_tailed: bool
) -> int:
    z_a = z_alpha(alpha, two_tailed)
    z_b = z_beta(power)

    numerator = 2 * (std_dev ** 2) * (z_a + z_b) ** 2
    denominator = delta ** 2

    return math.ceil(numerator / denominator)


def achieved_power_mean(
    std_dev: float,
    delta: float,
    alpha: float,
    n_per_variant: int,
    two_tailed: bool
) -> float:
    z_a = z_alpha(alpha, two_tailed)

    se = std_dev * math.sqrt(2 / n_per_variant)
    z_effect = abs(delta) / se

    return normal_cdf(z_effect - z_a)


def z_test_proportion(p_c, n_c, p_t, n_t, tail):
    """
    Two-sample z-test for proportions
    """
    p_pool = (n_c * p_c + n_t * p_t) / (n_c + n_t)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t))
    if se == 0:
    # No statistical uncertainty → test undefined
        return 0.0, 1.0, 0.0
    z = (p_t - p_c) / se

    if tail == "two_sided":
        p_value = 2 * (1 - norm.cdf(abs(z)))
    else:
        p_value = 1 - norm.cdf(z)

    return z, p_value, se


def welch_t_test(mu_c, sd_c, n_c, mu_t, sd_t, n_t, tail):
    """
    Welch's t-test for difference in means
    """
    se = math.sqrt(sd_c**2 / n_c + sd_t**2 / n_t)
    t_stat = (mu_t - mu_c) / se

    df_num = se**4
    df_den = ((sd_c**2 / n_c)**2) / (n_c - 1) + ((sd_t**2 / n_t)**2) / (n_t - 1)
    df = df_num / df_den

    if tail == "two_sided":
        p_value = 2 * (1 - t.cdf(abs(t_stat), df))
    else:
        p_value = 1 - t.cdf(t_stat, df)

    return t_stat, p_value, se, df



def paired_t_test(mean_diff: float, sd_diff: float, n: int, tail: str):
    """
    Paired t-test using summary stats of differences.
    """
    if n <= 1 or sd_diff is None or sd_diff == 0:
        return 0.0, 1.0, 0.0, max(n - 1, 0)

    se = sd_diff / math.sqrt(n)
    t_stat = mean_diff / se
    df = n - 1

    if tail == "two_tailed":
        p_value = 2 * (1 - t.cdf(abs(t_stat), df))
    else:
        p_value = 1 - t.cdf(t_stat, df)

    return t_stat, p_value, se, df



def mcnemar_test(b: int, c: int):
    """
    McNemar's test for paired binary outcomes.

    Parameters
    ----------
    b : int
        Converted before, but not after
    c : int
        Not converted before, but converted after

    Returns
    -------
    statistic : float
    p_value : float
    """

    if b + c == 0:
        # No discordant pairs → no information
        return 0.0, 1.0

    # Continuity-corrected McNemar test
    statistic = ((abs(b - c) - 1) ** 2) / (b + c)
    p_value = 1 - chi2.cdf(statistic, df=1)

    return statistic, p_value



def mcnemar_ci(b: int, c: int, alpha: float):
    """
    Confidence interval for McNemar effect size:
    Delta = (c - b) / (b + c)

    Uses normal approximation. Suppressed for small samples.
    """

    n = b + c
    if n < 10:
        return None, None

    delta = (c - b) / n

    # Standard error of delta
    se = (4 * b * c) ** 0.5 / (n ** 1.5)

    z = norm.ppf(1 - alpha / 2)

    lower = delta - z * se
    upper = delta + z * se

    return lower, upper




def mcnemar_exact_test(b: int, c: int):
    """
    Exact McNemar test using binomial distribution.

    Tests whether the probability of change in either direction
    is equal (p = 0.5).

    Parameters
    ----------
    b : int
        Converted before, but not after
    c : int
        Not converted before, but converted after

    Returns
    -------
    statistic : float
        Number of discordant pairs (b + c)
    p_value : float
        Exact two-sided p-value
    """

    n = b + c
    if n == 0:
        return 0.0, 1.0

    # Two-sided exact binomial test
    p_value = 2 * min(
        binom.cdf(min(b, c), n, 0.5),
        1 - binom.cdf(max(b, c) - 1, n, 0.5)
    )

    return float(n), float(p_value)
