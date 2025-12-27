from copy import deepcopy
from .engine import compute_sample_sizes


def mde_sensitivity(req):
    """
    Computes total sample size for MDE sensitivity:
    [0.8 × MDE, 1.0 × MDE, 1.2 × MDE]

    Does not mutate the original request.
    """
    base_mde = req.mde
    deltas = [0.8 * base_mde, base_mde, 1.2 * base_mde]

    results = []

    for d in deltas:
        req_copy = deepcopy(req)
        req_copy.mde = d

        sizes = compute_sample_sizes(req_copy)

        results.append({
            "mde": round(d, 4),
            "total_sample": sizes["Total"]
        })

    return results
