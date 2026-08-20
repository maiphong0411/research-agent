# The Reason-Act Loop

> Sources: Yao et al., 2023-03-10
> Raw: [ReAct](../../raw/agents/yao2023reactsynergizingreasoningacting.md)
> Updated: 2026-08-20

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

## See Also

- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Open Problems in Agentic Systems](open-problems.md)
