---
title: "Why Underpowered A/B Tests Fail"
description: "Underpowered A/B tests fail not because nothing changed, but because they lack the statistical power to detect real effects. Learn why this happens, how to recognize it, and how to avoid it."
author: "pvalue.net Experimentation Team"
last_updated: "2026-02-04"
pillar: "sample-size-power-mde"
type: "supporting"
---

## Executive Summary
> **Underpowered tests fail because they are statistically incapable of detecting the effects they are meant to measure.**  
> A non-significant result does not mean “no impact” — it often means the experiment lacked sufficient power.  
> Underpowered experiments waste traffic, time, and trust by producing inconclusive results that are misinterpreted as evidence.  
> Understanding why tests are underpowered is essential for designing experiments that can actually answer questions.

---

## What Does “Underpowered” Mean?
An experiment is **underpowered** when it has a low probability of detecting a real effect of interest, even if that effect truly exists.

Formally, this means:
\[
\text{Power} = P(\text{Detect effect} \mid \text{Effect is real})
\]
is too low for the decision being made.

A test with 40% power will miss real effects **60% of the time**.

---

## Why Underpowered Tests Are So Common
Most A/B tests are underpowered by default.

Common reasons include:
- Overestimating expected effect size
- Underestimating metric variance
- Limited traffic or short test durations
- Treating sample size as a goal rather than a constraint
- Running many experiments without feasibility checks

The result is a large number of experiments that *look valid* but cannot produce meaningful conclusions.

---

## Intuition: Listening for a Whisper
Imagine trying to hear a whisper in a noisy room.

If the whisper is too quiet relative to the background noise, you won’t hear it — no matter how carefully you listen.

An underpowered experiment is doing exactly that:  
trying to detect a signal that is too small relative to noise.

---

## Mental Model: Overlapping Distributions
Visualize the outcome distributions of the control and variant.

- With **low power**:
  - Distributions are wide
  - They overlap heavily
  - Real differences are indistinguishable from noise

- With **adequate power**:
  - Distributions narrow
  - Overlap decreases
  - Real effects become detectable

Power determines how separated these distributions must be before you can reliably tell them apart.

---

## The Statistical Mechanism Behind Failure
In hypothesis testing, detection depends on the inequality:

```text
Effect size ≥ (z_crit + z_{1−β}) × SE
```

If this inequality is not satisfied, the test cannot reliably detect the effect.

Underpowered tests fail because:
    - The effect size is too small
    - The standard error is too large
    - Or both.


## What Makes a Test Underpowered?

## 1. Small Effect Sizes

Most real-world product changes have modest effects.

If the true effect is smaller than what the test is powered to detect, the result will almost always be non-significant.


## 2. High Variance Metrics

Noisy metrics increase the standard error.

Higher standard error raises the detection threshold, making effects harder to detect even with large samples.


## 3. Insufficient Sample Size

Sample size reduces noise, but only gradually.

Doubling sample size does not double power — it produces diminishing returns.


## 4. Unrealistic Planning Assumptions

Underpowered tests often assume:
    - Optimistic lift
    - Stable variance
    - Ideal user behavior
    - When reality deviates from assumptions, power collapses.




## Worked Example: A Silent Failure

## Scenario

You run an A/B test on a landing page conversion rate.

## Inputs

    - Baseline conversion rate: 10%
    - True lift: +0.5 percentage points
    - Sample size per variant: 5,000 users
    - Significance level: 5% (two-tailed)


## Step 1: Standard Error

For a binary metric, the standard error is:

$$
SE = \sqrt{p(1 - p)\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}
$$

Using equal sample sizes:

$$
SE \approx \sqrt{0.1 \times 0.9 \times \frac{2}{10000}} \approx 0.0042
$$


## Step 2: Detection Threshold

For 80% power:

zcrit​+z1−β​≈1.96+0.84=2.80


Minimum detectable effect:

MDE≈2.80×0.006≈0.0168



## Interpretation

    - The experiment can only detect effects of ~1.7 percentage points or larger
    - The true effect is 0.5 percentage points
    - The test is guaranteed to fail, even though the effect is real
    - The expected outcome is a non-significant result.


## Why “No Result” Is Often Misinterpreted?

Underpowered tests frequently produce:
    - High p-values
    - Wide confidence intervals
    - No clear winner


These outcomes are often interpreted as: “The change didn’t work.”

Statistically, the correct interpretation is: “The experiment could not detect the effect.”

These are very different conclusions!! 


## Why Underpowered Tests Are Dangerous?

Underpowered experiments cause harm by:
    - Masking real improvements
    - Creating false confidence in the status quo
    - Wasting traffic and time
    - Training teams to distrust experimentation

A failed test is not neutral — it shapes future decisions.


## How to Avoid Underpowered Tests?

Before running any experiment:
    1. Define the smallest effect worth detecting
    2. Choose confidence level and desired power
    3. Estimate variance realistically
    4. Compute feasibility (sample size or MDE)

If feasibility fails, do not run the test.


## How This Relates to Sample Size and Power?

Underpowered tests are a direct consequence of misunderstanding the relationship between sample size and power.

To understand this relationship in detail, see
👉[Sample Size vs Power in A/B Testing](/public/articles/sample-size-vs-power/)


## How This Relates to MDE?

Minimum Detectable Effect (MDE) makes underpowering explicit.

MDE answers: “What effects can this experiment realistically detect?”

If the effect you care about is smaller than the MDE, the test will fail by design.

To understand MDE in depth, see
👉 [What Is Minimum Detectable Effect (MDE)?](/public/articles/what-is-mde/)


## Frequently Asked Questions

## Does increasing test duration fix underpowered tests?

Only if it increases sample size enough to meaningfully reduce standard error.

## Can I detect small effects with low power?

Occasionally, by chance — but not reliably.

## Are underpowered tests worse than no tests?

Often yes. They produce misleading evidence that appears rigorous but is not.