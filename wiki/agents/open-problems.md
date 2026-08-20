# Open Problems in Agentic Systems

> Sources: Yao et al., 2023-03-10; Shinn et al., 2023-03-20; Yao et al. (Sierra), 2024-06-17
> Raw: [ReAct](../../raw/agents/yao2023reactsynergizingreasoningacting.md); [Reflexion](../../raw/agents/shinn2023reflexionlanguageagentsverbal.md); [tau-bench](../../raw/agents/yao2024taubenchbenchmarktoolagentuserinteraction.md)
> Updated: 2026-08-20

## Overview

Recurring weaknesses, not per-paper limitations. An entry earns a place here only
when it appears in more than one method — a single paper's flaw is an anecdote,
the same flaw across several is a problem the field has not solved. Each entry
names which methods exhibit it and what attacking it would require.

Compiled from 3 papers. Confidence in "recurring" is correspondingly low; entries
should be revised as more sources land.

## 1. Load-bearing magic numbers

**Exhibited by:** ReAct — backoff at 7 steps (HotpotQA) and 5 (FEVER), switch to
ReAct when majority vote falls below n/2. Reflexion — reflect after "more than 3
cycles" of repetition or "exceeds 30" actions.

Both papers' headline results depend on hand-set thresholds, tuned per domain and
never ablated. Reflexion's reflection trigger is the clearest case: the mechanism
credited with fixing loop entrapment is an `if` statement with two constants.

**What an attack requires:** show that the reported gains do or do not survive
when the agent decides for itself. A learned or self-assessed trigger that matches
the hardcoded one would be a clean contribution; showing the gain collapses
without the constant would be a stronger one. Neither experiment exists.

## 2. Nothing recovers within a trajectory

**Exhibited by:** ReAct — loop entrapment, where "the model repetitively generates
the previous thoughts and actions", and non-informative search at 23% of errors,
which gives the model "a hard time to recover". Reflexion — recovery is achieved
only by abandoning the episode and restarting from a reset environment.

The field has two options for a derailed trajectory: continue and fail, or throw
it away and start over. Mid-trajectory repair — backtracking to a decision point,
retracting a bad thought, re-planning from partial progress — is absent from all
three papers. ReAct's hard step budget makes this terminal, since "more steps will
not improve ReAct performance".

**What an attack requires:** a backtracking mechanism over the thought-action
trace, plus a benchmark that credits partial recovery. This is the largest
structural gap of the three and the most likely to generalize.

## 3. Measurement flatters the method

**Exhibited by:** ReAct — label ambiguity is 29% of judged cases against an EM gap
to CoT of 27.4 vs 29.4, so the comparison sits inside annotation noise. Reflexion
— 91% vs 80% compares multi-trial-with-feedback against single-shot while keeping
the pass@1 label. τ-bench — terminal-state reward means "r = 1 might be a
necessary but not sufficient condition", so a policy-violating trajectory scores 1.

Three papers, three different ways the evaluation is more permissive than the
claim it supports. τ-bench is the most honest, stating the flaw outright.

**What an attack requires:** for τ-bench specifically, a trajectory-aware reward
that checks policy compliance along the path rather than only the final database
state. That is well-scoped, clearly motivated by the authors' own admission, and
would tighten every number in the paper. Best entry point on this list.

## 4. Retry, reset, and oracle assumptions exclude deployment

**Exhibited by:** Reflexion — requires "reset the environment, and start a new
trial" plus an Evaluator that can judge correctness. τ-bench — measures precisely
the opposite setting, where the first attempt is the only one and pass^8 is the
target.

Methods are developed where retries are free and success is machine-checkable;
the reliability problem is measured where neither holds. See the Disputed block in
[Self-Reflection and Episodic Memory](self-reflection-and-memory.md).

**What an attack requires:** an improvement mechanism that operates within a
single episode, or a way to transfer lessons learned in a resettable environment
into a single-pass deployment. The second framing is closer to a thesis than a
paper.

## 5. Consistency is named but unaddressed

**Exhibited by:** τ-bench — "pass^8 < 25%", closing on "the need for methods that
can improve the ability of agents to act consistently". Neither ReAct nor
Reflexion reports variance across trials at all.

The problem is stated by the benchmark that measures it and targeted by nobody.
Note the interaction with entry 1: if headline results depend on domain-tuned
constants, some measured inconsistency may be those constants failing outside the
conditions they were fitted to — a hypothesis nobody has tested.

**What an attack requires:** first, an ablation separating agent variance from
user-simulator variance, since τ-bench does not. Without that split it is unclear
how much of the collapse is even the agent's fault — which makes this the
necessary precursor to any method work on consistency.

## See Also

- [The Reason-Act Loop](reason-act-loop.md)
- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Agent Reliability and How to Measure It](agent-reliability-evaluation.md)
