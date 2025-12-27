📌 Sample Size Calculator — Known Issues / Deferred Fixes Log

Status: Product is functionally correct and usable.
Scope: UI + backend logic for sample size calculator only.
Policy: Bugs listed here are non-blocking, cosmetic or explanatory, not computational.

1️⃣ Continuous explanation headline uses binary-style language

Status: ❌ Unfixed (intentionally deferred)

Description

For continuous outcomes, the explanation headline currently uses percentage-based language:

“Detecting a 20% absolute lift from a 320% baseline…”

This is semantically incorrect. Continuous metrics should use raw units, e.g.:

“Detecting a 0.2 unit improvement from a 3.2 baseline…”

Root cause

Backend explanation generator assumes binary metrics and multiplies baseline / MDE by 100.

Impact

❌ Confusing explanation text

✅ No impact on calculations

✅ No impact on output correctness

Fix required later

Add outcome-type branching in backend explanation logic:

Binary → percentage language

Continuous → unit-based language

2️⃣ Missing unit awareness for continuous metrics

Status: ❌ Unfixed (planned enhancement)

Description

The product does not currently know whether a continuous metric is:

seconds

milliseconds

currency

count

arbitrary units

Impact

Explanation uses generic “unit”

UI still understandable

No statistical issue

Fix required later (Phase 2)

Optional “metric unit” input (seconds / ms / ₹ / custom)

Render explanation with unit labels

3️⃣ Strict allocation validation (floating-point edge case)

Status: ❌ Unfixed (accepted by design)

Description

Allocation validation requires exactly 100:

return total === 100;


Inputs like 33.3 + 33.3 + 33.4 may fail due to floating-point precision.

Impact

Edge-case UX annoyance

No statistical risk

Encourages clean integer allocations

Decision

Accepted for Phase 1.
Can relax later with epsilon check if needed.

4️⃣ Sensitivity table is MDE-only (not power / alpha)

Status: ❌ Unfixed (by design)

Description

Sensitivity analysis currently explores only MDE variation.

Impact

Limited “what-if” scope

Still extremely useful and correct

Decision

This matches the original product agreement.
Power / alpha sensitivity intentionally deferred.

5️⃣ No frontend defensive guards for missing backend fields

Status: ❌ Unfixed (backend contract trusted)

Description

Frontend assumes backend always returns:

explanation.details

sensitivity.mde_variants

design_integrity

Impact

UI may break if backend schema changes

Currently safe because backend is controlled

Fix later

Add defensive checks (if (!data.sensitivity) return;) when product hardens.