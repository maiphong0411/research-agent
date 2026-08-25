# The Reason-Act Loop

> Sources: Yao et al., 2023-03-10; Fan et al., 2026-08-04; Yang et al., 2026-08-11; Chen et al., 2026-08-07
> Raw: [ReAct](../../raw/agents/yao2023reactsynergizingreasoningacting.md); [Screenshots or Tools](../../raw/agents/fan2026screenshotstoolselicitingtool.md); [ReTree](../../raw/agents/yang2026selfcorrectinglonghorizonsearchagents.md); [The Horizon Gap](../../raw/agents/chen2026horizongapplanningmemory.md)
> Updated: 2026-08-24

## Overview

The reason-act loop is the base architecture of nearly every LLM agent: the model
alternates between emitting *thoughts* (free-text reasoning that changes nothing
externally) and *actions* (tool calls that return observations). ReAct introduced
it by augmenting the action space to `Â = A ∪ L`, where a language action "does
not affect the external environment, thus leading to no observation feedback" and
serves only to update context.

The motivating diagnosis was that chain-of-thought is "a static black box, in that
the model uses its own internal representations to generate thoughts and is not
grounded in the external world". Grounding thoughts in retrieved observations was
meant to cure hallucination — and it does, dramatically. It also introduces a
distinct family of failures that the paradigm still has no principled answer to.

## What grounding buys

Hallucination as a share of judged failures drops from 56% under chain-of-thought
to 0% under ReAct, and false positives fall from 14% to 6%. On interactive tasks
the gains are large: absolute success-rate improvements of 34% (ALFWorld) and 10%
(WebShop) over imitation and RL baselines, from one or two in-context examples.

## What grounding costs

The same structural constraint that grounds the agent also constrains it.
Reasoning errors rise from 16% under chain-of-thought to 47% under ReAct, because
"such a structural constraint also reduces its flexibility in formulating
reasoning steps". On HotpotQA, ReAct actually *loses* to chain-of-thought: 27.4
versus 29.4 exact match. It wins on FEVER, 60.9 versus 56.3, where retrieving
accurate knowledge matters more than reasoning freely.

So the paradigm is not a strict improvement. It trades reasoning flexibility for
factual grounding, and which side wins is task-dependent.

## Two failures with no principled fix

**Loop entrapment.** ReAct's signature failure is that "the model repetitively
generates the previous thoughts and actions", unable to break out. It is folded
into the 47% reasoning-error bucket, so its standalone frequency was never
reported. The authors attribute it to greedy decoding but do not test the claim.

**Unrecoverable retrieval failure.** Non-informative search accounts for 23% of
error cases. The damage is not the bad retrieval itself but the absence of any
backtracking mechanism to recover from it.

> **Status: Outdated** (2026-08-24)
> A backtracking mechanism now exists. ReTree (Yang et al., 2026) models search as
> a dependency tree over evidence, and on a confirmed contradiction it returns to
> the node that introduced the refuted fact, repairs it, regenerates that node's
> summary, prunes dependent descendants and resumes — Doyle's truth-maintenance
> principle inside the loop. Against Full-Trajectory ReAct on 2,149 questions it
> improves judge accuracy by 8.3–25.6 points per dataset. Two reasons this does not
> close the problem: the repair fires in only 9.6–17.5% of runs and the paper never
> isolates its contribution, and the horizon tested is eight searches with peak
> baseline context of 1,920 characters. See
> [Trajectory Repair and Recovery](trajectory-repair.md).

Both are made terminal by a hard step budget — 7 steps on HotpotQA, 5 on FEVER —
combined with the finding that "more steps will not improve ReAct performance".
An agent that has begun looping will exhaust its budget and fail. Additional
compute does not help; only trajectory *recovery* would.

> **Status: Outdated** (2026-08-20)
> Loop entrapment has since been given a partial answer. Reflexion detects it with
> a hand-written heuristic and reflects on the failed trajectory — see
> [Self-Reflection and Episodic Memory](self-reflection-and-memory.md). The
> detector is a hardcoded threshold rather than a learned mechanism, so the
> underlying problem is mitigated, not solved.

## Capability gating

The paradigm does not work on small models by prompting alone. With PaLM-8B and
62B, "prompting ReAct performs worst among four methods" — worse than plain
standard prompting. It only becomes the best method after finetuning on 3,000
trajectories. Cheap-model agents therefore need supervised data, not just a
prompt.

## Expanding the action space does not settle the outcome

ReAct's core move was to widen the action space with language. The 2026 version of
that question — widen it with *tools* alongside screenshots — produces a result
that should be read back onto the original.

Under one identical harness on a 309-task computer-use benchmark, the same tool
availability **improves a reasoning model by +4.0pp and degrades a non-reasoning
model by −5.9pp** (5 runs each, both beyond 2 SE). Same action space, opposite
sign, decided by the policy. The non-reasoning policy "ignores, misnames, or
falsely terminates around tools."

And the reasoning model that benefits still calls a tool on only 55 of 309 tasks —
**23.9%** of the tool-reachable ones. The authors call this the *adoption gap* and
diagnose both levels identically: "the model already has a cheaper route and is
never trained to take it."

This is the same shape as ReAct's own capability gating (below): an enriched action
space is not a free capability, it is a capability the policy must be able to
exploit. What is new is the demonstration that it can be actively harmful.

The attempted fix is the more important result. A dense reward for tool use raised
adoption from 0.03 to 0.33 and carried into greedy decoding — but "held-out
accuracy does not follow. Behavior is steerable; competence is not." Reward shaping
moved the measured behaviour and left the capability untouched, with an entirely
benign reward. See
[Process Supervision and Verification](process-supervision-and-verification.md).

The one thing that did transfer was an observation-side change: dropping the
screenshot made redundant by a successful tool call, then retraining under the same
rule, reaches **37.8%** against **33.0%** for the uncompressed operating point at
**53%** of the input cost. Managing what the loop *observes* paid off where
incentivizing what it *does* did not.

## Nobody is working on the loop itself

A 1,547-paper survey of long-horizon agent work classifies its largest category,
execution control, into orchestration (338 papers), recovery (245), and the
single-agent control loop — **1 paper**.

The survey reads this as ReAct's "near-total absorption into 'how agents just
work'", which is a real possibility: the loop became infrastructure. The simpler
explanation is that the survey's keyword filter does not select for papers about an
agent's inner loop, and a subcategory of one cannot support a claim either way.

Either way, the direction of effort is clear and worth noting against this article's
two open failure modes: the field scaled *out* (more agents, more structure around
them) rather than hardening any single loop's error correction. The survey's own
assessment is that hardening "is where the harder unsolved problem sits."

This is also the open question about where ReAct's value actually lives — in the
model, or in the harness wrapped around it. See
[Long-Horizon, Long-Context, Long-Term Memory](long-horizon-vocabulary.md).

## See Also

- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Trajectory Repair and Recovery](trajectory-repair.md)
- [Process Supervision and Verification](process-supervision-and-verification.md)
- [Long-Horizon, Long-Context, Long-Term Memory](long-horizon-vocabulary.md)
- [Open Problems in Agentic Systems](open-problems.md)
