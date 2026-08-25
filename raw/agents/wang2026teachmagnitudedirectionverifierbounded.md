> Source: Wang et al. (Ant Group / Zhejiang University), arXiv preprint 2026
> URL: https://arxiv.org/abs/2608.13179
> Collected: 2026-08-24
> Published: 2026-08-13
> Bibkey: wang2026teachmagnitudedirectionverifierbounded
> Read: abstract-only

## Problem

Two supervision regimes, each broken differently. RLVR "offers a verifier-bounded
performance ceiling for training multi-turn tool-use agents, yet its
trajectory-level credit assignment conflates heterogeneous per-turn outcomes into
a single reward signal." On-policy distillation "provides dense per-token
supervision but is either teacher-bounded or prone to gradient concentration
collapse."

## Method

**CrEST**, hierarchical credit assignment resolving credit at two levels:
"turn-segmented verified advantages address inter-turn dilution, while
entropy-gated self-teacher modulation refines intra-turn token contributions."

The framing claim: "the teacher's role in policy optimization can be reduced from
determining update directions to modulating update magnitudes, unlocking dense
credit assignment without sacrificing the verifier-bounded ceiling."

## Results

Evaluated on BFCL V3 and WildToolBench. "consistently outperforms both RL and
distillation baselines across two model scales, with the largest gains on
long-trajectory and strict session-level metrics." No numbers in the abstract.

## Failure modes

Abstract-only — inferences from the abstract.

- `[observed]` **The abstract reports no numbers at all**, only orderings
  ("consistently outperforms", "largest gains"). Nothing bounds effect size, and
  "two model scales" with no seed count means the claim of consistency is
  unquantified from here.

- `[observed]` **A "privileged self-teacher" is the same model with extra
  information, so the ceiling argument may be self-defeating.** The pitch is that
  the verifier, not the teacher, sets the ceiling — but the dense signal comes from
  the policy's own privileged variant, whose errors are correlated with the
  policy's. Distillation from a correlated teacher can reinforce shared mistakes
  regardless of whether it sets direction or only magnitude.

- `[observed]` **"Entropy-gated" is an unspecified threshold.** Gating on entropy
  requires a cutoff, and per [[khanal2026pass1reliabilityscienceframework]] and the
  ReAct note, hand-set thresholds in this literature are usually load-bearing and
  unablated. Whether the gate is learned or constant is the thing to check.

## Relevance

One of several 2026 papers converging on the same target as open problem 3 —
terminal reward conflating per-turn outcomes — from the training side rather than
the evaluation side. The "verifier-bounded ceiling" framing matters: it makes
explicit that RLVR's quality is capped by verifier quality, which is exactly the
dependency [[yuan2026verifiableprocessrewardsagentic]] quantifies (bias ∝ verifier
disagreement rate) and [[rosset2026artbuildingverifierscomputer]] shows is poor
for computer-use tasks. Related to
[[zhao2026betteragentsmultiturnuser]], which attacks the same inter-turn dilution
with a simulator reaction signal instead of a self-teacher.
