# Self-Reflection and Episodic Memory

> Sources: Shinn et al., 2023-03-20
> Raw: [Reflexion](../../raw/agents/shinn2023reflexionlanguageagentsverbal.md)
> Updated: 2026-08-20

## Overview

Reflexion answers the question the reason-act loop leaves open: how does an agent
carry a lesson from a failed episode into the next one, without training? Its
answer is to "reinforce language agents not by updating weights, but instead
through linguistic feedback". After a failed trial, a Self-Reflection model turns
the trajectory and its reward into a verbal summary, which is appended to an
episodic memory and prepended to the next attempt.

The results are strong — 130 out of 134 ALFWorld tasks, and 91% pass@1 on
HumanEval against a reported 80% for GPT-4. The mechanism is also thinner than
the framing suggests, in three specific ways.

## The trigger is a hardcoded threshold

Reflection does not fire when the agent judges it useful. It fires on a
hand-written rule: "if the agent executes the same action and receives the same
response for more than 3 cycles, or if the number of actions taken in the current
environment exceeds 30 (inefficient planning), we self-reflect".

This is a loop detector — and loop entrapment is exactly the signature failure of
[the reason-act loop](reason-act-loop.md). So the headline improvement rests
partly on two unablated constants (3 cycles, 30 actions) tuned to one domain. The
paper never tests whether the gain survives if the agent must decide for itself
when to reflect. That question is the most tractable opening in this line of work.

## "Long-term memory" holds three entries

Memory is bounded at Ω, "usually set to 1-3", and for ALFWorld "we truncate the
agent's memory to the last 3 self-reflections (experiences)" — explicitly "to
adhere to max context LLM limitations". Learning is nonetheless reported across 12
consecutive trials, so whatever is learned by trial 12 must be carried by the last
three reflections alone, not by accumulated experience. The authors point at
vector databases as future work.

## Reflection can entrench a wrong diagnosis

Acknowledged: verbal policy optimization "may still succumb to non-optimal local
minima solutions". A mistaken self-diagnosis becomes a memory entry that steers
the next trial, and nothing in the architecture detects or discards a bad
reflection. Self-critique has no error-correction layer of its own.

## The unstated scope limit

The loop requires the agent to "reset the environment, and start a new trial".
Every reported gain depends on retrying a task from a clean state. That silently
restricts the method to simulators and sandboxes: irreversible actions — a sent
message, a payment, a physical movement — admit no retry. Progress also depends on
an Evaluator judging correctness, which needs unit tests or an environment reward.
Tasks whose success is not machine-checkable get no learning signal at all.

Neither constraint appears in the paper's Limitations section, and together they
exclude most of the deployment settings agents are being built for.

> **Status: Disputed**
> Whether retry-based self-improvement addresses the real reliability problem.
> Shinn et al. (2023) demonstrate large gains from reflecting on a failed trial and
> retrying from a reset environment. Yao et al. (Sierra, 2024) measure agents in a
> customer-service setting where pass^k — "the chance that all k i.i.d. task trials
> are successful" — is the target, and no retry is available: the first attempt is
> the only attempt. Under that metric performance collapses to "pass^8 < 25%". The
> two are not directly contradictory, but they cannot both be the priority: the
> dominant improvement mechanism in the literature is unavailable in precisely the
> setting where the measured failure is worst. See
> [Agent Reliability and How to Measure It](agent-reliability-evaluation.md).

## Reading the headline number

91% versus 80% on HumanEval is not a like-for-like comparison. Reflexion gets
multiple trials plus test feedback; the GPT-4 baseline gets one shot with neither.
The metric label (pass@1) stays fixed while the attempt budget changes underneath
it, so the gap conflates method quality with extra attempts. The ALFWorld
comparison is cleaner: baseline ReAct plateaus, its "performance increase halts
between trials 6 and 7", converging at a 22% hallucination rate "with no signs of
long-term recovery".

## See Also

- [The Reason-Act Loop](reason-act-loop.md)
- [Open Problems in Agentic Systems](open-problems.md)
