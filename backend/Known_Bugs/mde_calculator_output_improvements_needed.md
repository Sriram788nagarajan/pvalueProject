MDE Calculator — Output Quality Review (5-Case Validation)

This document evaluates what the user sees, how they interpret it, and where the output currently falls short of paid-product quality.

CASE 1 — Independent Binary, 2-tailed, 1 Control vs 1 Test
What works well

MDE value is statistically correct

Absolute + percentage-point interpretation is clear

“Blind spot” explanation is intuitive

Sensitivity table is actionable (duration, traffic, variance)

Detectability label (“Hard to detect”) aligns with numbers

Where output falls short

No business anchoring

User still asks: “Is 1.2pp big or small for my business?”

Output does not contextualize MDE relative to:

Baseline volatility

Typical effect sizes in similar experiments

Revenue / KPI impact

Why-this-is-large explanation is generic

“No single factor disproportionately increases MDE” is technically correct

But feels empty as insight

Action hierarchy is unclear

Table shows 4 actions

Only one is called out as “most effective”

But why that one dominates is not quantified

Product gap

Missing “Decision readiness” framing

User wants to know:

“Should I even run this experiment?”

CASE 2 — Independent Binary, 1-tailed, 1 Control vs 2 Tests
What works well

Pairwise breakdown is correct

Differences between Test A and Test B are surfaced numerically

Multi-variant warning is appropriate

Sensitivity results differ per variant (good)

Where output falls short

No cross-variant comparison

User sees two cards, but:

Which test is more promising?

Which one is wasting traffic?

Product forces mental aggregation

No multiple-testing acknowledgment

Even though MDE is design-time:

Users will assume inference later

No reminder about alpha inflation risk

Detectability labels feel repetitive

Both say “Hard to detect”

But magnitudes differ meaningfully

Product gap

Missing portfolio-level guidance

Paid product should answer:

“If I can only keep one variant, which should it be?”

CASE 3 — Independent Continuous, 2-tailed, 1 Control vs 1 Test
What works well

Absolute units respected (no % abuse)

MDE is numerically consistent with σ and n

Sensitivity behaves correctly

Detectability = “Easily detectable” makes sense

Where output falls short

Units lack semantic meaning

“4.43 units” means nothing without:

Typical daily variance

Historical distribution

Business tolerance thresholds

Verdict feels optimistic without guardrails

“Well powered” sounds like success is likely

But power is conditional on effect size exceeding MDE

Why-this-is-large section is weak

Says “large relative to business impact”

But does not justify why

Product gap

Missing scale normalization

Users want:

“Is 4.43 units a lot in practice?”

CASE 4 — Independent Continuous, 1-tailed, 1 Control vs 2 Tests
What works well

One-tailed direction reflected correctly

Pairwise results differ appropriately

Sensitivity logic scales correctly

Where output falls short

Directionality not emphasized enough

Output does not clearly remind:

Negative effects will not be detected

This is a directional bet

No experiment-selection guidance

Test A vs Test B:

Which is more realistic?

Which aligns better with business expectations?

Repetitive structure hides insight

Two nearly identical cards

Forces user to scan numbers manually

Product gap

Missing comparative prioritization

Paid product should say:

“Test A is more viable under current design.”

CASE 5 — Paired Binary (Advanced)
What works well

Correct planning-only MDE

Approximation caveat is explicit

Output is numerically stable

Warnings are visible

Where output seriously falls short

High cognitive load

Discordance rate is abstract

Users do not naturally think in p01 + p10

Sensitivity recommendations are weak

“Double duration” and “reduce variance” are vague

No concrete path to improving discordance

Baseline absence feels confusing

Even when disabled, users wonder:

“Why am I not allowed to enter baseline?”

Trust gap

Users will ask:

“How reliable is 6.3pp really?”

Product gap (major)

Paired binary output is not self-sufficient

Requires statistical literacy

Should be:

Advanced

Gated

Possibly excluded from v1 marketing

Cross-Cutting Output Weaknesses (All Cases)
1. No explicit “Run / Don’t Run” recommendation

Users want a decision

Output stops at explanation

2. Sensitivity table is powerful but unranked

Shows numbers

Does not explain why one lever dominates

3. Detectability labels lack calibration

“Hard / Borderline / Easy” are heuristic

No confidence bands or uncertainty framing

4. No business cost framing

No mention of:

Traffic cost

Time cost

Opportunity cost

Is This Output Worth Paying For — Today?
For whom it is worth paying

Data scientists

Experimentation leads

Statistically literate PMs

For whom it is not yet worth paying

Founders

Marketers

Growth PMs without stats background

Why

Output explains statistics well

But does not yet answer business decisions directly

What Would Make This a Paid-Grade Product (Output-Only)

Without adding new math:

Add Decision Summary

“Given your design, this experiment is / is not worth running.”

Add Comparative Insights

Rank variants

Highlight dominated designs

Add Business Anchors

“This MDE equals ~X% of baseline”

“This change would require a large behavioral shift”

Gate Paired Binary

Advanced toggle

Stronger warning language

Reduced sensitivity noise