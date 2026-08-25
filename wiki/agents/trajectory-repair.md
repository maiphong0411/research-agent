# Trajectory Repair and Recovery

> Sources: Yang et al., 2026-08-11; Peng et al., 2026-08-18; Yu et al., 2026-08-19; Li, Cao, Qiao, Hu, 2026-08-19; Chen et al., 2026-08-07; Khanal et al., 2026-03-31
> Raw: [ReTree](../../raw/agents/yang2026selfcorrectinglonghorizonsearchagents.md); [WER](../../raw/agents/peng2026writeexecuterefineskill.md); [EvoResearcher](../../raw/agents/yu2026trainingfreeinferencetimeselfreflectioncostbounded.md); [RTPO](../../raw/agents/li2026rtporeverseturnpolicyoptimization.md); [The Horizon Gap](../../raw/agents/chen2026horizongapplanningmemory.md); [Beyond pass@1](../../raw/agents/khanal2026pass1reliabilityscienceframework.md)
> Updated: 2026-08-24

## Overview

For two years the field had exactly two responses to a derailed trajectory:
continue and fail, or throw the episode away and restart from a reset environment.
ReAct exhibits the first, Reflexion institutionalized the second. Mid-trajectory
repair — backtracking to a decision point, retracting a bad premise, re-planning
from partial progress — was absent.

2026 produced the first mechanism that actually does it, plus enough surrounding
evidence to say something uncomfortable about the whole direction: the compounding
model that motivates repair is wrong, and intrinsic self-correction may get *worse*
as models improve.

## The mechanism: dependency-directed revision

ReTree is the concrete answer. Memory is an external tree in which "a child is a
search state derived from its ancestor's evidence" — a dependency lineage,
explicitly not a Tree-of-Thoughts search over candidate continuations. Each node
holds a bounded task-state summary, the evidence introduced locally at that node,
and a revision history.

On a confirmed contradiction it locates the node that introduced the refuted fact,
replaces the fact and its source, regenerates that node's summary from corrected
evidence, **removes all descendants**, and resumes from the repaired node. This is
Doyle's 1979 truth-maintenance principle — changing a justification invalidates
dependent conclusions — dropped into an LLM search loop.

The framing is the useful part, and it names precisely what the existing wiki was
missing: existing compression methods often "replace erroneous facts without
repairing downstream reasoning derived from them". Fixing the fact is not fixing
the trajectory.

Results over 2,149 questions across four search benchmarks, judge accuracy / EM:

| System | Overall | vs. Full ReAct |
|---|---|---|
| Full-Trajectory ReAct | 30.1 / 20.6 | — |
| ReportMemory | 40.9 / 22.0 | |
| FlatUpdate | 40.4 / 25.5 | |
| ReTree | 44.0 / 28.0 | +13.9 pp accuracy, +7.4 pp EM |

Per-dataset the gain over Full ReAct is 8.3–25.6 pp. The comparison that isolates
the *repair* mechanism is against FlatUpdate, which shares the same summary
budget, evidence budget and conflict detector but replaces a refuted fact without
locating its introducer or pruning descendants: 2.2–4.7 pp.

### Why that 2.2–4.7 pp is not yet evidence

Backtracking "is triggered in 9.6–17.5% of ReTree runs". On the other ≥82.5%,
ReTree and FlatUpdate should behave near-identically — so the entire gap has to be
concentrated in the minority of runs that backtracked, requiring the repair to flip
roughly a fifth to a third of them. Possible, and it would be a strong result. But
the paper never reports accuracy conditioned on whether a backtrack fired, and
with a single seed (seed 0, no confidence intervals on any accuracy number) the gap
is equally consistent with noise.

**That stratification is the cheapest high-value experiment in this article.** It
requires no new runs, only a split of data already collected.

Two further limits worth recording. Peak per-step context for Full-Trajectory
ReAct is 1,920 characters at worst — nowhere near an 8B model's window — so
whatever ReTree fixes, it is not a context-limit effect, and "unbounded context
growth" is not the operative mechanism at this scale. And the provenance result the
architecture exists to deliver is Citation Precision 44.5: most cited passages do
not entail the claim attached to them. The tree preserved lineage; the claims still
do not check out.

## Repair that trains rather than patches

Three 2026 papers attack the same problem from the training side.

**WER** trains a *Skill Optimizer* outside a frozen executor: the optimizer
proposes a skill, the frozen agent executes it repeatedly, a programmatic verifier
scores outcomes, and matched successful/failed trajectories become the next
phase's refinement state. Its premise is the most quotable number in the batch —
"agent-authored skills perform 8-11 points worse than using no skill" — and its
gains over the no-skill baseline are +7.80 and +3.85 points on BFCL v4 multi-turn
and τ²-bench.

Read those together: on τ²-bench the method recovers a self-authoring deficit and
adds under four points. It also needs a programmatic verifier, which the motivating
use case (novel software with no reference implementation) does not have. But
architecturally it is the right shape for [open problem
4](open-problems.md) — retries happen during optimizer training, so the *deployed*
executor is single-pass.

**RTPO** attacks instability in multi-turn RL itself, naming three coupled causes:
rollout-training context mismatch, weak turn-level credit under sparse terminal
rewards, and "asynchronous policy drift when short and long trajectories are
optimized under different policy versions". Reported improvements of 21.50% and
10.76% over trajectory- and turn-level baselines, on unnamed benchmarks with
unnamed baselines — so treat as a pointer, not a citation. The framing matters
regardless: some measured agent inconsistency may be an optimizer artifact rather
than an agent property.

**EvoResearcher** is the negative control everyone needs. A training-free
generate → self-critique → revise loop on a frozen backbone, with a `CONFIRMED`
sentinel for early stopping. On its primary benchmark it "does not raise accuracy
beyond the 95% Wilson interval"; its contribution is cost, terminating 82-88% of
items early at equal accuracy, about 2.1 generations per question. All experiments
are pure-reasoning benchmarks with no tools.

If a zero-gradient prompt loop matches trained accuracy, the training papers owe a
comparison against it. Almost none of them run one.

## The compounding model that justifies repair is wrong

Everything above is designed against an intuition: per-step error `ϵ`, independent
compounding, exponential decay in horizon. The measurements do not support it.

Vending-Bench, on runs exceeding 20M tokens, finds not smooth decay but "capable
models turn a profit in most runs, but every model has some runs that derail into a
'meltdown' loop from which they rarely recover" — and "derailment shows no clear
correlation with the context window filling up". The survey's synthesis:
degradation is bimodal, "fine, or catastrophically derailed", with a trigger the
field cannot predict.

The reliability study points the same way from a different angle: observed decay
runs *faster* than the i.i.d. baseline, consistent with positive inter-step error
correlation — a confused agent stays confused. Its theoretical consequence, if the
correlation `ρ` holds, is that failure scales as `Ω(ϵ · e^{ρT})`, which makes
"Reducing ρ … is therefore a higher-priority training objective than reducing ϵ alone".

That is the strongest available argument for repair as a research direction: the
quantity to attack is not per-step accuracy but error *persistence*. It also means
context-compaction thresholds and step budgets justified by exponential-decay
reasoning are fitted to a curve the data rejects.

> **Status: Disputed**
> What long-horizon failure is actually caused by. Yang et al. (2026) motivate
> ReTree with unbounded context growth and retrieval-induced error cascade, and
> bound per-step context accordingly. Vending-Bench, via Chen et al. (2026), finds
> meltdown showing "no clear correlation with the context window filling up", and
> ReTree's own peak baseline context is 1,920 characters — far below any limit. The
> context-growth motivation and the measured trigger of derailment do not line up.

## Intrinsic self-correction may get worse with scale

The counter-intuitive finding worth carrying forward: decomposing self-correction
into detection, localization and correction produces an "accuracy-correction
paradox" — the weaker model in a three-model comparison (66% base accuracy)
corrects its own errors intrinsically at 26.8%, while the strongest (94% base
accuracy) manages 16.7%, and error-detection rate does not predict correction
success.

The proposed **Error Depth Hypothesis** is that stronger models make fewer but
structurally deeper errors that intrinsic correction is specifically bad at
reaching — which would mean the long-standing finding that intrinsic
self-correction does not reliably help is "not a capability gap current models
simply haven't crossed yet, but a pattern that could get worse, not better, as
models improve."

n = 3 models, arriving here as a secondary citation, so this is a lead. But it
predicts a specific measurable trend across model generations, and it implies
external grounding is not a temporary crutch.

## Related: memory scaffolds do not help

The obvious adjacent intervention — give the agent an episodic scratchpad — is
measured across 10 models and 23,392 episodes and never helps at long horizons: 6
models hurt, 4 neutral within ±0.03 GDS, largest penalties −0.14 and −0.13. See
[Self-Reflection and Episodic Memory](self-reflection-and-memory.md) for the
full disputed block.

## The field is not working on this

From the 1,547-paper survey, the execution category splits orchestration 338 to
recovery 245 — and the survey's own assessment is that the field "has invested far
more engineering effort in scaling out … than in hardening any one agent's own
error-correction — even though the self-correction evidence above suggests
hardening is where the harder unsolved problem sits."

Corroborating from the engineering side: across 39 "open-source agent frameworks"
and 439 "agentic applications", "tools and workflows absorb over" 70% of testing
effort while "the model-driven planning component itself receives under" 5% and
prompts under 1%. The least deterministic part of every agent is the least tested
part.

## See Also

- [The Reason-Act Loop](reason-act-loop.md)
- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Process Supervision and Verification](process-supervision-and-verification.md)
- [Long-Horizon, Long-Context, Long-Term Memory](long-horizon-vocabulary.md)
- [Open Problems in Agentic Systems](open-problems.md)
