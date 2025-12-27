def build_explanation(req, total_sample):
    details = []

    if req.mde < 0.02:
        details.append("Small effect sizes require much larger samples to detect reliably.")

    if req.baseline_value < 0.1:
        details.append("Low baseline rates increase uncertainty in measurement.")

    min_alloc = min(v.allocation_percent for v in req.variants)
    if min_alloc < 20:
        details.append("Highly skewed traffic allocation significantly increases required users.")

    details.append(
        f"This design guarantees {int(req.power * 100)}% power at a {int(req.alpha * 100)}% significance level."
    )

    headline = (
        f"Detecting a {int(req.mde * 100)}% absolute lift from a "
        f"{int(req.baseline_value * 100)}% baseline requires careful planning."
    )

    return {
        "headline": headline,
        "details": details
    }
