---
title: "What Is Minimum Detectable Effect (MDE)?"
description: "Minimum Detectable Effect (MDE) is the smallest true difference between variants that an A/B test is statistically powered to detect at a given confidence level and power."
author: "pvalue.net Experimentation Team"
last_updated: "2026-02-03"
pillar: "sample-size-power-mde"
type: "supporting"
---



## Executive Summary
> **Minimum Detectable Effect (MDE)** is the smallest true difference between experimental variants that an A/B test is statistically powered to detect at a specified significance level and power.  
> It is a planning metric determined before an experiment starts and depends on sample size, metric variance, confidence level, and desired power.  
> A smaller MDE requires more data to detect reliably.  
> MDE does not describe observed results and should not be interpreted as the expected or minimum observed lift.

---

## Why This Matters in Real Experiments
Most A/B tests fail not because nothing changed, but because the experiment was **never capable of detecting the change** that actually occurred.

If your experiment’s MDE is larger than the real effect you care about, the test is effectively blind. This leads to false conclusions, wasted traffic, and repeated “no result” experiments that quietly erode trust in experimentation.

Understanding MDE forces you to confront a hard constraint: **what effects are realistically detectable given your data**.

---

## Simple Intuition
Imagine trying to hear a whisper in a noisy room. If the whisper is too quiet, you won’t hear it no matter how carefully you listen. The whisper has to be loud enough compared to the noise for you to notice it.

MDE is how loud the whisper must be before your experiment can hear it.

---

## Mental Model
Think of two overlapping hills representing the outcomes of your control and variant. When the hills are very close together, it’s hard to tell them apart. As the distance between them increases, it becomes easier to confidently say they are different.

---

## Formal Definition
In hypothesis testing, the Minimum Detectable Effect is the smallest effect size such that the statistical test achieves a predefined power \(1 - \beta\) at a given significance level \(\alpha\), assuming the effect is real.

It represents the detection threshold imposed by sampling variability and test design, not the magnitude of observed outcomes.

---

## Core Formula
```text
MDE = (z_crit + z_{1−β}) × SE
```

**Where:**
- `z_crit` = critical value for the chosen significance level  
- `z_{1−β}` = z-score corresponding to desired power  
- `SE` = standard error of the metric  

**Assumptions:**
- Correct test selection  
- Reasonable normal approximation  
- Variance estimates are realistic  

---

## Worked Example (With Numbers)

### Problem Setup
You are running a conversion rate experiment on a landing page.

### Inputs
- Baseline conversion rate = 10%  
- Sample size per variant = 20,000 users  
- Significance level = 5% (two-tailed)  
- Power = 80%  

### Calculation
For a binary metric, the standard error is driven by the baseline rate and sample size. Plugging values into the MDE formula yields an MDE of approximately **1.2 percentage points**.

### Interpretation
Your experiment can reliably detect changes of **±1.2% or larger**. Any true improvement smaller than that is likely to go undetected, even if it exists.

---

## How to Use This in Practice
Use MDE to decide **whether an experiment is worth running at all**.

If the smallest effect you care about is smaller than your MDE, the experiment cannot answer your question. You must either accept a larger detectable effect, collect more data, or reconsider the experiment entirely.

MDE is a constraint, not a goal.

---

## Common Mistakes and Misconceptions
- **Confusing MDE with observed lift:** MDE is about detectability, not results.  
- **Choosing unrealistically small MDEs:** This leads to infeasible sample size requirements.  
- **Ignoring variance assumptions:** Underestimated variance produces misleadingly small MDEs.  
- **Reinterpreting MDE after results are seen:** MDE must be fixed before the experiment starts.  

---

## When You Should Use a Calculator
In practice, calculating MDE requires combining sample size, variance, confidence level, and power correctly. This is why MDE calculators are typically used during experiment planning to ensure assumptions are internally consistent.

---

## Frequently Asked Questions

### Is MDE the same as lift?
No. Lift is an observed outcome. MDE is a planning threshold that defines what effects are detectable.

### Can MDE change after an experiment starts?
No. Changing MDE mid-experiment invalidates the original statistical guarantees.

### Is a smaller MDE always better?
Not necessarily. Smaller MDEs require more data and longer experiments, which may not be practical.

### Why do many experiments have large MDEs?
Because traffic, variance, or time constraints limit how much data can be collected.

---

