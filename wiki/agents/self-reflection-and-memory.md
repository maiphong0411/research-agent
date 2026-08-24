# Self-Reflection and Episodic Memory

> Sources: Shinn et al., 2023-03-20; Khanal et al., 2026-03-31; Yang et al., 2026-08-11; Yu et al., 2026-08-19; Chen et al., 2026-08-07
> Raw: [Reflexion](../../raw/agents/shinn2023reflexionlanguageagentsverbal.md); [Beyond pass@1](../../raw/agents/khanal2026pass1reliabilityscienceframework.md); [ReTree](../../raw/agents/yang2026selfcorrectinglonghorizonsearchagents.md); [WER](../../raw/agents/peng2026writeexecuterefineskill.md); [EvoResearcher](../../raw/agents/yu2026trainingfreeinferencetimeselfreflectioncostbounded.md); [The Horizon Gap](../../raw/agents/chen2026horizongapplanningmemory.md); [Auditing Self-Evolution](../../raw/agents/li2026auditingselfevolutionfinancialagents.md)
> Updated: 2026-08-24

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

> **Status: Disputed**
> Whether an episodic memory scaffold helps at all on long tasks. Shinn et al.
> (2023) treat the episodic buffer as the mechanism carrying learning across
> trials. Khanal et al. (2026) run ReAct against a ReAct-plus-episodic-scratchpad
> scaffold over 10 models and 23,392 episodes and find the scaffold **never**
> improves long-horizon performance: 6 models hurt, 4 neutral within ±0.03,
> largest penalties −0.14 and −0.13, concentrated in the mid-capability tier
> "capable enough to use the scratchpad but not capable enough to absorb its
> overhead efficiently". Their reading is that per-turn scratchpad overhead
> consumes step budget and context that pays off at short horizons and becomes
> load-bearing cost at long ones, and they recommend against episodic memory as a
> default reliability intervention. Note the settings differ — Reflexion's buffer
> carries lessons *between* episodes on a repeated task, Khanal's scratchpad
> carries notes *within* one episode — so this is a dispute about what "memory
> helps" licenses, not a direct refutation.

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

## The retry assumption now has an alternative

The scope limit above — reflection needs a reset environment — was open in 2023.
Two 2026 mechanisms sidestep it in different ways, and both are worth reading
against Reflexion rather than as successors to it.

**Repair inside the episode.** ReTree keeps an external tree in which "a child is a
search state derived from its ancestor's evidence". On a confirmed contradiction it
backtracks to the node that introduced the refuted fact, repairs it, regenerates
that node's summary, prunes every descendant, and resumes — no reset, no new trial.
Its diagnosis is aimed precisely at what a verbal reflection cannot do: existing
methods often "replace erroneous facts without repairing downstream reasoning
derived from them". Fixing the belief is not fixing the trajectory.

**Retries moved out of deployment.** WER puts the repeated execution into
*optimizer training*: a Skill Optimizer proposes skills, a frozen executor runs
each repeatedly under a programmatic verifier, and the deployed executor stays
single-pass. Reflexion's retry budget is spent at training time instead of
inference time.

Both are covered in [Trajectory Repair and Recovery](trajectory-repair.md).

## Self-critique without grounding still does not raise accuracy

The 2023 caveat that reflection "may still succumb to non-optimal local minima
solutions" has hardened into a measured pattern.

A 2026 training-free protocol iterating generate → self-critique → revise on a
frozen backbone reports plainly that on its primary benchmark it "does not raise
accuracy beyond the 95% Wilson interval". Its value is repositioned as cost
control — an early-stop sentinel terminating 82-88% of items at equal accuracy,
about 2.1 generations per question. A useful negative result, and the cheap
baseline that trained methods rarely compare against.

Worse for the long run, self-correction may not be a capability that scale fixes.
Decomposing it into detection, localization and correction yields an
**accuracy-correction paradox**: the weaker of three models (66% base accuracy)
corrects its own errors intrinsically at 26.8%, the strongest (94% base accuracy)
at 16.7%, and detection rate does not predict correction success. The proposed
Error Depth Hypothesis — stronger models make fewer but structurally deeper errors
that intrinsic correction cannot reach — implies this "could get worse, not better,
as models improve". n = 3 models, arriving as a secondary citation, so it is a lead;
but it argues external grounding is structural rather than temporary.

## What accumulated reflection costs

Reflexion's memory is three entries and its risk is entrenching a wrong diagnosis.
When the same idea is scaled into persistent skill and workflow stores, the risk
becomes measurable: audited self-evolution methods raise benign utility (0.741 →
0.837) while raising exposure to injected content (0.820 → 0.943) and overall
attack success (0.496 → 0.530). The agent gets individually more robust per
encounter and more successfully attacked overall, because it reaches more.

Accumulation is not free, and accuracy-only evaluation cannot see the bill. See
[Self-Evolution and Skill Accumulation](self-evolution.md).

## See Also

- [The Reason-Act Loop](reason-act-loop.md)
- [Agent Reliability and How to Measure It](agent-reliability-evaluation.md)
- [Trajectory Repair and Recovery](trajectory-repair.md)
- [Self-Evolution and Skill Accumulation](self-evolution.md)
- [Open Problems in Agentic Systems](open-problems.md)
