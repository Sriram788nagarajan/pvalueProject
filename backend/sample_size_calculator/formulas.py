from scipy.stats import norm


def z_alpha(alpha, two_tailed=True):
    return norm.ppf(1 - alpha / 2) if two_tailed else norm.ppf(1 - alpha)


def z_beta(power):
    return norm.ppf(power)

def sample_size_binary(p, delta, alpha, power, two_tailed=True):
    """
    Binary outcome, independent samples.
    Baseline-only variance approximation.
    Matches standard pen-and-paper derivation.
    """
    z_a = z_alpha(alpha, two_tailed)
    z_b = z_beta(power)

    variance = p * (1 - p)

    n = (2 * (z_a + z_b) ** 2 * variance) / (delta ** 2)
    return int(n) + 1


def sample_size_continuous(sd, delta, alpha, power, two_tailed=True):
    z_a = z_alpha(alpha, two_tailed)
    z_b = z_beta(power)

    n = (2 * sd**2 * (z_a + z_b)**2) / (delta**2)
    return int(n) + 1
