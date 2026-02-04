---
title: "Sample Size vs Power in A/B Testing"
description: "Learn the difference between sample size and statistical power in A/B testing, how they interact, and why increasing traffic alone does not guarantee reliable results."
author: "pvalue.net Experimentation Team"
last_updated: "2026-02-04"
pillar: "sample-size-power-mde"
type: "supporting"
---

## Executive Summary
> **Sample size** is how much data you collect.  
> **Statistical power** is the probability that your experiment will detect a real effect if it exists.  
> Increasing sample size increases power — but only relative to effect size, variance, and significance level.  
> Many experiments fail because teams confuse having “a lot of data” with having enough power to answer their question.

---

## Why This Confusion Exists
In experimentation discussions, “sample size” and “power” are often used interchangeably — but they are not the same thing.

Teams frequently say:
- “We had enough traffic.”
- “The sample size was large.”
- “We tested it for two weeks.”

Yet the experiment still produces no result.

The root cause is almost always the same: **power was never evaluated**.  
Sample size was tracked, but detectability was never assessed.

---

## Core Definitions

### Sample Size
Sample size is the number of observations collected per variant in an experiment.

Examples include:
- Users exposed to each variant
- Sessions measured
- Transactions observed

Sample size is a **quantity of data**, not a measure of experimental sensitivity.

---

### Statistical Power
Statistical power is the probability that a statistical test will correctly reject the null hypothesis when a true effect exists.

Formally:
\[
\text{Power} = P(\text{Detect effect} \mid \text{Effect is real})
\]

Commonly targeted power levels:
- **80%** — standard for most business experiments
- **90%** — used for high-risk or high-impact decisions

Power answers a forward-looking question:

> *If there is a real effect of the size I care about, how likely am I to detect it?*

---

## The Relationship Between Sample Size and Power
Sample size is **one input** into power — not the output.

Power depends jointly on:
- Sample size
- Effect size
- Metric variance
- Significance level (\(\alpha\))
- Test design (independent, paired, clustered, etc.)

Increasing sample size **increases power**, but:
- The relationship is **non-linear**
- Gains diminish as sample size grows
- Large samples cannot compensate for extremely small effects or very noisy metrics

More data does not automatically mean a more informative experiment.

---

## Intuition: A Signal vs Noise View
An experiment attempts to detect a signal buried in noise.

- **Noise** comes from natural randomness in user behavior
- **Signal** is the true causal effect of the change you introduced

Increasing sample size reduces noise by averaging it out.  
Statistical power measures whether the remaining signal is strong enough to be reliably detected.

If the signal is too weak relative to the noise, no reasonable amount of listening will help.

---

## Mental Model
Imagine two overlapping distributions representing the outcomes of your control and variant.

When sample size is small:
- The distributions are wide
- They overlap heavily
- It is difficult to distinguish one from the other

As sample size increases:
- The distributions narrow
- Overlap decreases
- Differences become easier to detect

Power describes **how separated these distributions must be** before the experiment can reliably tell them apart.

---

## Formal Statistical Framing
In classical hypothesis testing, detectability is governed by the inequality:

```text
Effect size ≥ (z_crit + z_{1−β}) × SE
```

where ,

**Effect Size** : The true difference between variants that you care about detecting.

Examples: 
- Absolute change in conversion rate
- Difference in average revenue
- Change in time-on-site


Power is always defined relative to a specific effect size.

**z₍crit₎** : Significance Threshold

The critical value corresponding to the chosen significance level (α).

- Two-tailed 5% test: Zcrit ~ 1.96
- One-tailed 5% test: Zcrit ~ 1.64

This term controls the false-positive rate.

**z₍1−β₎** : Power Requirement.

The z-score corresponding to the desired power level.

- 80% power → z₍1−β₎ ~ 0.84
- 90% power → z₍1−β₎ ~ 1.28

Higher power requires a larger safety margin for detection.

**SE — Standard Error** :

The standard error measures how much random variation exists in the estimated metric.

It depends on:
    - Metric variance
    - Sample size
    - Experimental design

Larger sample sizes reduce standard error, which increases power.
Intuitively , Think of it this way, the more you see something of, the more sure you are of it. That's why Larger sample size reduces standard error.

## Why Sample Size Alone Is Not Enough?

Two experiments can have the same sample size but very different power.

Power will be lower when:
    - The metric is highly variable
    - The baseline rate is extreme
    - The effect of interest is small
    - The design introduces dependence or clustering

This is why statements like “we had 50,000 users” are meaningless without context.


## Worked Example (With Calculation)

### Scenario
You run a conversion rate experiment on a landing page.

### Inputs
- Baseline conversion rate: 10%
- Sample size per variant: 10,000 users
- Significance level: 5% (two-tailed)
- Desired power: 80%

---

### Step 1: Standard Error
For a binary metric, the standard error is:

$$
SE = \sqrt{p(1 - p)\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}
$$

Using equal sample sizes:

$$
SE \approx \sqrt{0.1 \times 0.9 \times \frac{2}{10000}} \approx 0.0042
$$

---

### Step 2: Detection Threshold
The combined detection threshold is:

$$
z_{crit} + z_{1-\beta} \approx 1.96 + 0.84 = 2.80
$$

The minimum detectable effect is:

$$
\text{Detectable effect} \approx 2.80 \times 0.0042 \approx 0.0118
$$

---

### Interpretation
The experiment can reliably detect effects of about **1.2 percentage points or larger**.

Smaller true improvements are likely to go undetected, even if they exist.


## Common Misconceptions

- “Large sample size means high power.”
False. Power depends on the effect size you want to detect.

- “We ran the test long enough.”
Duration is irrelevant without variance and effect size.

- “We can calculate power after the test.”
Post-hoc power is statistically meaningless.

- “Non-significant means no effect.”
Often it simply means the experiment was underpowered.



## How to Use This in Practice?

Before launching any experiment, answer one question:

"What is the smallest effect that would justify acting on the result?"

Then:
    1. Choose confidence level and power
    2. Estimate variance realistically
    2. Compute required sample size or detectable effect

If the numbers do not work, do not run the experiment.


## How This Relates to MDE?

Minimum Detectable Effect (MDE) is the bridge between sample size and power.

MDE answers: "Given my sample size, variance, and desired power, what effects can I actually detect?"


To understand this constraint in detail, see  
👉 [What Is Minimum Detectable Effect (MDE)?](/public/articles/what-is-mde/)


## Frequently Asked Questions

## Can I increase power without increasing sample size?

Only by:

- Accepting a larger detectable effect
- Reducing metric variance
- Using a more sensitive experimental design

## Is 80% power always sufficient?

No. It is a convention, not a law. Higher-stakes decisions often require higher power.

## Why do many real-world experiments have low power?

Because effect sizes are overestimated, variance is underestimated, and feasibility constraints are ignored during planning.