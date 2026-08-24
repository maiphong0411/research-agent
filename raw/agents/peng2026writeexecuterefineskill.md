> Source: Peng et al. (Harbin Institute of Technology Shenzhen / CUHK / Huawei), arXiv preprint 2026
> URL: https://arxiv.org/abs/2608.17587
> Collected: 2026-08-24
> Published: 2026-08-18
> Bibkey: peng2026writeexecuterefineskill
> Read: abstract-only

## Problem

A clean, quantified premise: "Expert-written natural language skills can improve
tool-using agents, yet **agent-authored skills perform 8-11 points worse than
using no skill**. This gap suggests that following procedural guidance and
improving it from execution evidence are distinct capabilities."

And the gap in existing fixes: "Inference time loops can repair skills but do not
improve the model that writes the next one."

## Method

**WER** (Write, Execute, Refine): trains "a Skill Optimizer **outside a frozen
executor**. The optimizer proposes skills, a frozen agent executes each
repeatedly, and a programmatic verifier scores the outcomes. The scores provide
relative credit and select mixed-outcome records. Matched successful and failed
trajectories from these records form the next phase's refinement states, so the
optimizer learns from the consequences of its earlier outputs."

## Results

On BFCL v4 multi-turn and τ²-bench:

- Average Pass@1 over the no-skill baseline: **+7.80** and **+3.85** points.
- "Under an identical refinement workflow, it outperforms the same backbone without
  optimizer training by **9.35** and **10.29** points."
- "The trained 4B optimizer reaches **76.63 percent** on BFCL v4, outperforming all
  evaluated off-the-shelf general-purpose models used as skill optimizers on
  average."

## Failure modes

Abstract-only — inferences from the abstract.

- `[observed]` **The headline gain is measured against no-skill, which the premise
  says is already a strong baseline.** Agent-authored skills are 8–11 points *worse*
  than no skill; WER is 7.80 and 3.85 points *better* than no skill. So on τ²-bench
  the method recovers the self-authoring deficit and adds under 4 points. The
  larger numbers (9.35, 10.29) are against an untrained optimizer, i.e. the ablation
  of the paper's own contribution, not against the practically relevant
  alternative — expert-written skills, whose value the premise asserts and whose
  number the abstract never gives.

- `[observed]` **It depends on a programmatic verifier, which is why it works and
  why it will not transfer.** BFCL and τ²-bench have checkable end states. The
  motivating use case for agent-authored skills is novel software with no
  reference implementation, exactly where no programmatic verifier exists. This is
  the same boundary [[yuan2026verifiableprocessrewardsagentic]] hits, restated at
  the skill-authoring layer.

- `[observed]` **"Executes each repeatedly" hides the compute cost and the reliance
  on run-to-run variance.** "mixed-outcome records" are precisely trajectories
  where the same skill sometimes works — which requires the executor to be
  stochastic enough to produce both outcomes. That makes the training signal
  dependent on the very inconsistency
  [[khanal2026pass1reliabilityscienceframework]] measures, and it will thin out as
  executors get more reliable. Repeat count is unstated.

- `[observed]` **A 4B optimizer against off-the-shelf general-purpose models
  "on average"** invites the reading that it loses to some of them individually.
  Which ones, and by how much, is the thing to check.

## Relevance

The most concrete instance in this batch of a *within-loop* improvement mechanism
that keeps the executor frozen — which is a genuinely different answer to open
problem 4 (retry/reset assumptions exclude deployment): the retries happen during
optimizer training, not at deployment time, so the deployed executor is
single-pass. Worth recording as prior art for that entry.

Its premise is also independently valuable: a measured 8–11 point *penalty* for
agent-authored skills is hard evidence against the self-improvement assumption that
[[li2026auditingselfevolutionfinancialagents]] attacks from the security side.
