# Agent Reliability and How to Measure It

> Sources: Yao et al. (Sierra), 2024-06-17
> Raw: [tau-bench](../../raw/agents/yao2024taubenchbenchmarktoolagentuserinteraction.md)
> Updated: 2026-08-20

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

## See Also

- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Open Problems in Agentic Systems](open-problems.md)
