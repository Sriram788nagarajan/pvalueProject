from typing import Dict, List
from .schema import MDEInput
from .validation import ValidationResult


class PairwiseComparison:
    def __init__(
        self,
        control_name: str,
        test_name: str,
        n_control: int,
        n_test: int,
    ):
        self.control_name = control_name
        self.test_name = test_name
        self.n_control = n_control
        self.n_test = n_test


class IntegrityResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.comparisons = []
        self.has_paired_binary_approximation = False

    def is_valid(self):
        return len(self.errors) == 0



# -----------------------------------------
# Cross-field integrity checks
# -----------------------------------------

def check_mde_integrity(
    data: MDEInput, validation: ValidationResult
) -> IntegrityResult:
    result = IntegrityResult()

    # Propagate validation errors (fail-fast)
    if not validation.is_valid():
        result.errors.extend(validation.errors)
        return result

    # ----------------------------
    # Control & test separation
    # ----------------------------

    control = next(v for v in data.variants if v.is_control)
    tests = [v for v in data.variants if not v.is_control]

    if len(tests) == 0:
        result.errors.append(
            "At least one test variant is required for MDE computation."
        )
        return result

    # ----------------------------
    # Paired design constraints
    # ----------------------------

    if data.metric_type == "binary" and data.design_type == "paired":
        result.has_paired_binary_approximation = True

    
        for test in tests:
            if test.n != control.n:
                result.errors.append(
                    f"Paired design requires equal sample sizes for control "
                    f"and test variants. Found control n={control.n}, "
                    f"{test.name} n={test.n}."
                )


    # ----------------------------
    # Pairwise construction
    # ----------------------------

    for test in tests:
        result.comparisons.append(
            PairwiseComparison(
                control_name=control.name,
                test_name=test.name,
                n_control=control.n,
                n_test=test.n,
            )
        )

        # Unequal traffic warning
        ratio = max(control.n, test.n) / min(control.n, test.n)
        if ratio >= 2:
            result.warnings.append(
                f"Traffic allocation between control and '{test.name}' "
                f"is highly imbalanced. This increases MDE and reduces "
                "sensitivity for this comparison."
            )

    # ----------------------------
    # Multi-variant warning
    # ----------------------------

    if len(tests) > 1:
        result.warnings.append(
            "Multiple test variants detected. MDE is computed pairwise "
            "against the control for each test. No global multi-variant "
            "inference is performed."
        )

    return result
