# Hardcoded / Assumptions Log (v1)

This document tracks all hardcoded, defaulted, or implicitly assumed values
that materially affect statistical inference in the AB Testing product.

Rule:
Any value that influences validity, power, sample size, or interpretation
and is not explicitly provided by the user MUST be logged here.

---

## 1. Minimum Detectable Effect (MDE)

- **Where used:** Sample size calculation, power estimation
- **Current behavior:** Defaulted if user does not provide
- **Typical assumed value:** Implicit (e.g. 2–5% lift or 0.2σ)
- **Why hardcoded:** Power math requires an effect size
- **User-visible:** ❌
- **Risk:** Required sample and power are meaningless without knowing MDE
- **Planned fix:** Make MDE mandatory or explicitly display assumed MDE

---

## 2. Baseline Metric Value

- **Where used:** Variance estimation, power calculation
- **Current behavior:** Assumed if not provided
- **Typical assumed value:** Implicit (e.g. 10% conversion rate)
- **Why hardcoded:** Variance depends on baseline
- **User-visible:** ❌
- **Risk:** Power and feasibility depend heavily on baseline
- **Planned fix:** Require baseline or force user confirmation of assumed value

---

## 3. Estimated Power Presentation

- **Where used:** Validation output summary
- **Current behavior:** Power shown as `1`
- **Actual meaning:** Approximately 0.99+
- **Why hardcoded:** UX simplification
- **User-visible:** ⚠️ (potentially misleading)
- **Risk:** Users may interpret power as certainty
- **Planned fix:** Show numeric power or label as "very high (≈1)"

---

## 4. Distributional Assumptions (Normality, Equal Variance)

- **Where used:** Test eligibility, power formulas
- **Current behavior:** User-declared, not validated
- **Why hardcoded:** No data available in Phase 0
- **User-visible:** ✅
- **Risk:** Invalid math if assumptions are false
- **Planned fix:** Add diagnostics in Phase 1+

---

## 5. IID / Randomization Assumption

- **Where used:** Causal validity, inference eligibility
- **Current behavior:** Assumed true if user selects randomized
- **Why hardcoded:** No assignment logs yet
- **User-visible:** ✅
- **Risk:** Overconfidence in weak designs
- **Planned fix:** Stronger warnings + post-hoc checks

---

## Change Policy

- Every new hardcoded or defaulted value MUST be added to this log
- Every resolved assumption MUST be removed or marked resolved
- This log must be reviewed before advancing phases
