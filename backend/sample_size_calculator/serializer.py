from copy import deepcopy

from .engine import compute_sample_sizes
from .sensitivity import mde_sensitivity
from .explanation import build_explanation
from .integrity import design_integrity


def build_response(req):
    """
    Builds the final layered response payload for the
    Sample Size Calculator.
    """

    # -----------------------
    # 1. Primary sample sizes
    # -----------------------
    sizes = compute_sample_sizes(req)

    variant_sizes = {
        k: v for k, v in sizes.items() if k != "Total"
    }

    sample_sizes = {
        "variants": variant_sizes,
        "total": sizes["Total"]
    }

    # -----------------------
    # 2. Experiment summary
    # -----------------------
    experiment_summary = {
        "outcome_type": req.outcome_type,
        "design": "independent",
        "baseline": req.baseline_value,
        "mde": req.mde,
        "alpha": req.alpha,
        "power": req.power,
        "test_direction": req.test_direction,
        "allocations": {
            v.name: v.allocation_percent for v in req.variants
        }
    }

    # -----------------------
    # 3. Plain-English explanation
    # -----------------------
    explanation = build_explanation(req, sizes["Total"])

    # -----------------------
    # 4. Sensitivity (MDE ±20%)
    # -----------------------
    sensitivity = {
        "mde_variants": mde_sensitivity(req)
    }

    # -----------------------
    # 5. Allocation impact preview
    # -----------------------
    alloc_values = list(experiment_summary["allocations"].values())
    allocation_comparison = None

    if len(set(alloc_values)) != 1:
        req_equal = deepcopy(req)
        equal_pct = 100 / len(req_equal.variants)

        for v in req_equal.variants:
            v.allocation_percent = equal_pct

        equal_sizes = compute_sample_sizes(req_equal)

        allocation_comparison = {
            "current_split": " / ".join(str(a) for a in alloc_values),
            "equal_split_total": equal_sizes["Total"],
            "current_split_total": sizes["Total"]
        }

    # -----------------------
    # 6. Design integrity badge
    # -----------------------
    design_integrity_block = design_integrity(
        sizes["Total"],
        req
    )

    # -----------------------
    # Final payload
    # -----------------------
    return {
        "sample_sizes": sample_sizes,
        "experiment_summary": experiment_summary,
        "explanation": explanation,
        "sensitivity": sensitivity,
        "allocation_comparison": allocation_comparison,
        "design_integrity": design_integrity_block
    }
