# Agent Reliability and How to Measure It

> Sources: Yao et al. (Sierra), 2024-06-17; Khanal et al., 2026-03-31; Venkataramani et al., 2026-02-03; Wu et al., 2026-07-30
> Raw: [tau-bench](../../raw/agents/yao2024taubenchbenchmarktoolagentuserinteraction.md); [Beyond pass@1](../../raw/agents/khanal2026pass1reliabilityscienceframework.md); [MAS-ProVe](../../raw/agents/venkataramani2026masproveunderstandingprocessverification.md); [ClawTrack](../../raw/agents/wu2026clawtracktracelevelevaluationimprovement.md)
> Updated: 2026-08-24

## Overview

τ-bench's contribution is a metric, not a method. **pass^k** is "the chance that
all k i.i.d. task trials are successful" — the deliberate inverse of pass@k, "the
chance that at least one out of k i.i.d. task trials is successful". Swapping
"at least one" for "all" changes what the number means: pass@k rewards an agent
that can eventually stumble onto a solution, pass^k rewards one that cannot fail.

Under it, apparent progress evaporates. gpt-4o with function calling succeeds on
"< 50%" of tasks at pass^1, and "pass^8 < 25%" on retail. An agent that usually
completes a task frequently cannot complete it eight times running.

## Why this reframes the field

Single-run averaged benchmarks are structurally unable to see this. The same model
looks roughly twice as good under pass^1 as under pass^8, and every headline
number in the agent literature is a pass^1-style figure.

If the binding constraint is variance rather than capability, then work aimed at
raising peak ability is optimizing the wrong axis. τ-bench measures the collapse
without proposing a fix, closing only on "the need for methods that can improve
the ability of agents to act consistently".

## The benchmark grades itself generously

Reward is terminal-state only: the final database must be "identical to the unique
ground truth outcome database", plus required substrings in the agent's replies.
The authors state the consequence plainly — "r = 1 might be a necessary but not
sufficient condition for a successful episode e.g., the agent might issue the
return without explicit user confirmation, which violates the policy".

So a trajectory can violate the domain policy and still score 1. The reported
figures are an **upper bound** on compliance, and the true numbers are worse than
"< 50%". A trajectory-aware reward would tighten every result in the paper — a
well-scoped and unusually clear opening.

## Where agents actually break

The stated failure categories are "complex reasoning over databases, understanding
and following ad-hoc policies, and handling compound (more than one) requests" —
notably, none of which is tool invocation. Tool *calling* is not the bottleneck;
state tracking across sub-goals and adherence to natural-language rules are. Rules
expressed only in prose are precisely the class that cannot be enforced in code.

## Caveats on the measurement

Stochasticity comes from "LM sampling of the user and agent messages", so the user
is itself a language model. A simulated user can be inconsistent in ways a real
one would not be, and the paper does not separate agent-caused from
simulator-caused failure — some of the pass^8 collapse may be user variance
charged to the agent. Tasks are also annotated so each instruction "leads to a
unique database outcome", which excludes the underspecified requests where agents
plausibly fail worst. Both domains were hand-built as "the simplest possible
database schemas, APIs, and policies".

## The duration axis τ-bench left out

τ-bench measured pass^k on short tasks. The obvious missing variable — how
reliability changes as tasks get *longer* — was filled in two years later across
396 tasks (four duration buckets × three domains, 33 tasks per cell), 10 models,
two scaffolds, k = 3, and 23,392 episodes.

Aggregate pass@1 by human-time bucket: **76.3%** (≤ 5 min) → **59.8%** (5–30 min)
→ **50.5%** (30–120 min) → **52.1%** (≥ 120 min) — a 24.3 percentage-point
decline. Every model declines over the full range.

Three findings that a single-run short-task benchmark cannot produce:

**Decay is super-linear, and that is a claim about error correlation.** Against an
i.i.d. Bernoulli baseline, Qwen3 30B's geometric prediction for long horizon is
`0.758⁴ ≈ 33.0%` against **22.2%** observed (1.5× below); Mistral Nemo's medium
prediction is `0.535² ≈ 28.6%` against **12.1%** (2.4× below). Early-failure rates
corroborate — episodes terminating before the first subtask rise from 1% to 25%
for one model, 2% to 11% for another. The mechanism is positive inter-step error
correlation: a confused agent stays confused. The theoretical consequence is that
failure scales as `Ω(ϵ · e^{ρT})`, so "Reducing ρ … is therefore a higher-priority
training objective than reducing ϵ alone".

**Domain beats duration.** Software-engineering tasks collapse (aggregate partial-
credit score 0.90 → 0.44) while document-processing barely moves (0.74 → 0.71).
Human-time and agent-difficulty are near-orthogonal: document tasks that take
humans 45–60 minutes need only 4–8 tool calls. So "long-horizon" measured in human
time is the wrong independent variable, and the study's own aggregate curve is
non-monotonic because of it.

**Capability rank ≠ reliability rank.** One model goes from highest short-horizon
pass@1 (94.9%) to fourth at very-long (66.7%); another moves 74.7% → 54.5% while a
model with nearly identical short performance (75.8%) falls to 34.3%. Selecting a
model on short-task benchmarks can reverse the right deployment decision.

## Variance is a capability signature, not an instability signature

The counter-intuitive result. Variance Amplification Factor — long-horizon
outcome variance over short-horizon variance — bifurcates cleanly:

| Model | VAF |
|---|---|
| MiniMax M2.5 | 2.60 |
| DeepSeek V3 | 2.49 |
| Kimi K2.5 | 2.48 |
| GLM-4.5 Air | 2.37 |
| Qwen3 32B | 1.26 |
| Llama 3.1 8B | 0.26 |

The top cluster is also the top cluster by long-horizon pass@1. Weak models score
below 1 because they fail about as reliably at short horizons as at long ones —
there is no variance to amplify. High variance therefore requires high capability.

This matters for how [τ-bench's pass^k collapse](#overview) should be read: some
of the measured inconsistency is the signature of a model that has *found*
task-completion strategies and does not always execute them, not of a model that
is broken. It also complicates any method that suppresses variance directly.

Two caveats. The measured variance is conditional on a chosen constant —
"Episodes use temperature 0.7 to induce the stochasticity required to estimate
reliability" — never ablated, so a deployment at temperature 0 has a different
profile than any number here. And VAF is defined in the paper as
long-over-short but computed as long+very-long over short+medium, one of two
headline metrics with drifting definitions.

## A secondary-citation discrepancy worth knowing

The 2026 study cites τ-bench as showing "GPT-4o achieves 61% pass@1 but 25% pass@8
on retail agent tasks". τ-bench's own text reports gpt-4o with function calling
succeeding on "< 50%" of tasks at pass^1 and "pass^8 < 25%" on retail. The pass^8
figure is consistent; the pass^1 figure is not. Use the primary source.

## Measurement of the measurement is also unreliable

Two 2026 results push the problem up a level.

Process verification — evaluating intermediate steps rather than outcomes — was
expected to give a lower-variance signal. Across three verification paradigms, two
granularities, five verifiers, four context strategies and six multi-agent
frameworks, it "does not consistently improve performance and frequently exhibits
high variance". The premise of that study is that multi-agent systems "often
exhibit high variance in their reasoning trajectories", so verifier variance and
system variance are now entangled and nobody has separated them — the same
unsolved split τ-bench left between agent variance and user-simulator variance.

Separately, outcome-only scoring cannot distinguish reliable reasoning from lucky
success at all. ClawTrack scores Task and Process independently over 320 tasks and
21 models, and reports that process scores filter "lucky passes invisible to
outcome-only evaluation", with **result verification the systematic bottleneck**
among its four scored dimensions. An agent that does not check its own results is
one that cannot notice it needs to recover. See
[Trajectory Repair and Recovery](trajectory-repair.md).

## Infrastructure reliability is part of reliability

A study spanning four duration buckets surfaces a validity threat short-task
benchmarking never encounters: whether the run completes at all. Its own
recommendation is that completion rate — the fraction of planned episodes reaching
termination without infrastructure error — be treated as "a first-class validity
metric". Worth holding it to that standard: it loses 368 episodes between 23,760
planned and 23,392 completed "after deduplication", with no statement of what was
deduplicated or whether the loss fell evenly across buckets. See
[Benchmark Validity](benchmark-validity.md).

Cost is not the barrier to this kind of study: 1,322 validation episodes cost
**$4.26**, roughly **$0.0032** per episode, with the full study estimated at
**$80–120**. Duration-stratified reliability measurement is affordable, which makes
its absence for three years after τ-bench a choice rather than a constraint.

## See Also

- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Benchmark Validity](benchmark-validity.md)
- [Process Supervision and Verification](process-supervision-and-verification.md)
- [Trajectory Repair and Recovery](trajectory-repair.md)
- [Long-Horizon, Long-Context, Long-Term Memory](long-horizon-vocabulary.md)
- [Open Problems in Agentic Systems](open-problems.md)
