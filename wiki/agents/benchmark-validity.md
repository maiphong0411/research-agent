# Benchmark Validity

> Sources: Yao et al., 2023-03-10; Yao et al. (Sierra), 2024-06-17; Khanal et al., 2026-03-31; Rosset et al., 2026-04-05; Wu et al., 2026-07-30; Chen et al., 2026-08-07; Li, Zhu, 2026-08-18
> Raw: [ReAct](../../raw/agents/yao2023reactsynergizingreasoningacting.md); [tau-bench](../../raw/agents/yao2024taubenchbenchmarktoolagentuserinteraction.md); [Beyond pass@1](../../raw/agents/khanal2026pass1reliabilityscienceframework.md); [Universal Verifier](../../raw/agents/rosset2026artbuildingverifierscomputer.md); [ClawTrack](../../raw/agents/wu2026clawtracktracelevelevaluationimprovement.md); [The Horizon Gap](../../raw/agents/chen2026horizongapplanningmemory.md); [Auditing Self-Evolution](../../raw/agents/li2026auditingselfevolutionfinancialagents.md)
> Updated: 2026-08-24

## Overview

τ-bench's authors admitted their terminal-state reward meant "r = 1 might be a
necessary but not sufficient condition" for success. That was an inference about
one benchmark. It is now a measured, field-wide result: agentic benchmarks
systematically report more success than a careful check finds, and the gap is
large enough to reverse published comparisons.

This article collects the measurements. The methods that try to fix them are in
[Process Supervision and Verification](process-supervision-and-verification.md).

## The size of the gap

Re-scoring three benchmarks with a purpose-built rubric verifier (success rate, %):

| Benchmark / agent | Native verifier | Rubric verifier (outcome) |
|---|---|---|
| WebVoyager / Fara-7B | 74.6 | 37.9 |
| WebVoyager / GPT-5 | 90.6 | 71.0 |
| Online-Mind2Web / Fara-7B | 32.2 | 15.8 |
| Online-Mind2Web / GPT-5 | 62.0 | 48.6 |
| WebTailBench / Fara-7B | 39.6 | 23.2 |
| WebTailBench / GPT-5 | 62.5 | 39.9 |

False positive rates of native verifiers against the rubric verifier are above
20% on every pair, with WebVoyager (GPT-4o) worst at 0.60 and 0.72 and lowest
agreement (κ 0.33 on both agents).

**The important caveat, stated by the paper itself: "The UV is treated as the
reference label."** So these are disagreements, not proven errors. The rubric
verifier's own agreement with humans is κ 0.58–0.64, and its near-zero false
positive rate is an optimization constraint ("any FPR-increasing change is
automatically rolled back") with a corresponding false *negative* rate of
0.31–0.32. A verifier tuned never to over-credit will systematically under-report
success, which pushes in exactly the direction that makes native verifiers look
loose. The honest reading: benchmark verifiers are **loose**, by an amount this
study does not calibrate.

The one place humans adjudicate is a spot check on AgentRewardBench: of 30
trajectories that terminated within budget and were human-labelled successful, 8
were judged false positives — FPR ≈ 0.27. n = 30, one annotator's guidelines.

## SWE-bench: what a decade of scrutiny found

The closest thing agent evaluation has to a common currency, audited:

- **32.67%** of successful patches involve solution leakage — the fix was already
  in the issue report or comments.
- A further **31.08%** pass only because the test suite is too weak to verify
  correctness.
- Filtering both drops one leaderboard-topping system from **12.47% to 3.97%**.
- Independently: passing patches diverge behaviorally from human ground truth in
  nearly **30%** of cases even when tests pass.
- A trajectory-level diagnostic finds that "even where capable models localize the
  right code, they still fail after reaching it" — "coherence collapse" — meaning
  Pass@1 alone "actively misdiagnoses why the remaining" 30–35% of issues go
  unsolved. That finding required decomposing **16,758** stored trajectories into
  aligned stages.

Generalized across agentic benchmarks: task-setup and reward-design flaws "can
over- or under-estimate reported performance by up to **100%** in relative terms",
and a best-practice checklist "reduced measured overestimation on one complex
benchmark by **33%**". τ-bench's specific exhibit: it "counts empty responses as
successes".

These arrive here as secondary citations from a survey. Verify against the primary
papers before citing any of them.

## The benchmark can cap the score

A distinct failure from leniency: benchmark *noise* setting a ceiling. Top-scoring
GUI agents "plateau around" 60% on AndroidControl "because benchmark noise —
ambiguities and factual errors in the benchmark itself — caps the achievable
score".

The same shape appeared in ReAct three years earlier: label ambiguity at 29% of
judged cases against an EM gap to chain-of-thought of ~2 points, putting the
headline comparison inside annotation noise. See
[The Reason-Act Loop](reason-act-loop.md).

## Harness compatibility can dwarf the effect being measured

The most alarming single measurement in this batch is not about agents at all. In
an audit of three self-evolution methods, one (Agent Workflow Memory) carried "a
literal WebArena text-action envelope" that "disrupts tool execution in our native
function-calling executor". Removing only that envelope moved utility from
**0.319 to 0.756** — while exposure to injected content rose 0.299 → 0.909 and
attack success rate 0.195 → 0.575.

A 43-point utility swing from a prompt-format mismatch, larger than any security
effect in the study. Two consequences:

1. Any cross-harness comparison of these methods may be measuring envelope
   compatibility rather than method quality.
2. The low attack success rate AWM appeared to have was an artifact of a broken
   executor, not a safety property.

Tracking "artifact-executor compatibility" belongs on every agent evaluation
checklist, and is the kind of thing an unpinned experimental setup hides completely.

## Whether the run finished is part of the result

The duration-stratified reliability study argues that completion rate — the
fraction of planned episodes reaching termination without infrastructure error —
should be "a first-class validity metric". It then loses 368 episodes between
23,760 planned and 23,392 completed "after deduplication", with no statement of what
was deduplicated or whether the loss fell evenly across duration buckets. A gap
concentrated in the hardest bucket and a gap spread evenly imply very different
headline numbers.

Unterminated trajectories are the same problem in a different guise: **17.0%** for
one agent on WebTailBench and **7.2%** for another on Online-Mind2Web, with no
statement of how they count toward the reported success rates. That 17.0% slice is
larger than several of the native-verifier disagreements being interpreted in the
same table.

## Nobody reports the statistic that horizon measurement depends on

Of roughly fifteen well-known agentic benchmarks checked against their own papers,
only GAIA "reports a clean, level-by-level human-time-to-complete statistic".
SWE-bench, WebArena and OSWorld — three of the most used — report "no human-time
baseline at all" in their own papers.

So the time-horizon metric the field increasingly quotes as its aggregate progress
measure cannot be computed on most of its benchmarks. The survey carrying this
observation treats the reported growth trend as measured rather than settled, with
cross-model-era comparability and generalization beyond benchmark tasks both
contested.

## The metric can be undermined by its own implementation

Two examples from a single paper, worth recording because they are the kind of flaw
that only shows up on a close read:

- A meltdown detector was specified with two conditions — high tool-call entropy
  **and** an entropy spike — where the spike condition was argued to be what
  "distinguishes meltdown from legitimate task exploration". Calibration returned
  the spike threshold as **δ* = 0.000**, making that condition vacuous. Every
  meltdown number is therefore a sustained-high-entropy detector.
- The same experiment ran a loop-detection circuit breaker aborting on "3 repeated
  (tool, args) pairs within 6 steps" — which censors precisely the *low*-entropy
  repetition that ReAct-lineage work calls loop entrapment. The meltdown metric can
  then only fire on high-entropy spirals, which is consistent with its
  counter-intuitive finding that frontier models melt down most.

## Practical rules this suggests

1. **Report the verifier, not just the score.** A success rate without a stated
   check is uninterpretable to within a factor of two.
2. **Score the trajectory, not only the end state.** Outcome-only checks cannot
   separate reliable reasoning from lucky success — the explicit motivation for
   ClawTrack's dual Task/Process scoring over 320 tasks and 12,541 rubric items.
3. **Pin the harness and record its version.** See the 43-point envelope swing
   above.
4. **Report completion rate and unterminated fraction** alongside accuracy.
5. **Distrust agreement as a proxy for correctness.** A verifier described as
   "robust to evaluator choice across different judge LLMs" has demonstrated
   consistency, not correctness; a shared bias produces exactly that result. The
   number that separates them is human agreement.

Rule 2 has a direct consequence for this repo's experiment protocol: a frozen
read-only evaluation harness is the structural fix for the failure mode this field
keeps exhibiting, which is why `CLAUDE.md` requires it.

## See Also

- [Agent Reliability and How to Measure It](agent-reliability-evaluation.md)
- [Process Supervision and Verification](process-supervision-and-verification.md)
- [Self-Evolution and Skill Accumulation](self-evolution.md)
- [Long-Horizon, Long-Context, Long-Term Memory](long-horizon-vocabulary.md)
- [Open Problems in Agentic Systems](open-problems.md)
