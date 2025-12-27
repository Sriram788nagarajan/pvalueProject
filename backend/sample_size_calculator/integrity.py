def design_integrity(total_sample, req):
    """
    Assigns a design integrity badge based on
    total required sample size and allocation skew.
    """

    # Base classification by total sample size
    if total_sample <= 5000:
        badge = "efficient"
    elif total_sample <= 20000:
        badge = "costly"
    else:
        badge = "impractical"

    # Allocation skew adjustment (soft downgrade only)
    min_alloc = min(v.allocation_percent for v in req.variants)

    if min_alloc < 15 and badge == "efficient":
        badge = "costly"
    # IMPORTANT: do NOT downgrade costly → impractical due to allocation

    reason_map = {
        "efficient": "This experiment can be run efficiently with reasonable traffic.",
        "costly": "This experiment is statistically valid but requires substantial traffic.",
        "impractical": "This experiment may be infeasible due to extremely large sample requirements."
    }

    return {
        "badge": badge,
        "reason": reason_map[badge]
    }
