from .formulas import (
    sample_size_binary,
    sample_size_continuous
)


def compute_sample_sizes(req):
    control = next(v for v in req.variants if v.is_control)
    treatments = [v for v in req.variants if not v.is_control]

    per_comparison_control_sizes = []

    for _ in treatments:
        if req.outcome_type == "binary":
            n_c = sample_size_binary(
                p=req.baseline_value,
                delta=req.mde,
                alpha=req.alpha,
                power=req.power,
                two_tailed=(req.test_direction == "two_tailed")
            )
        else:
            n_c = sample_size_continuous(
                sd=req.variance,
                delta=req.mde,
                alpha=req.alpha,
                power=req.power,
                two_tailed=(req.test_direction == "two_tailed")
            )

        per_comparison_control_sizes.append(n_c)

    # Worst-case control size
    control_n = max(per_comparison_control_sizes)

    # Scale by allocation
    # Convert percentages to fractions
    alloc_fractions = {
        v.name: v.allocation_percent / 100.0
        for v in req.variants
    }

    min_frac = min(alloc_fractions.values())

    # Total users needed so that the smallest arm reaches control_n
    total_n = int(control_n / min_frac) + 1

    results = {}
    for v in req.variants:
        results[v.name] = int(total_n * alloc_fractions[v.name])

    results["Total"] = sum(results.values())
    return results
