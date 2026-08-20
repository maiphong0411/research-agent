> Source: Shinn et al., NeurIPS 2023
> URL: https://arxiv.org/abs/2303.11366
> Collected: 2026-08-20
> Published: 2023-03-20
> Bibkey: shinn2023reflexionlanguageagentsverbal
> Read: full

## Problem

"it remains challenging for these language agents to quickly and efficiently learn
from trial-and-error as traditional reinforcement learning methods require
extensive training samples and expensive model fine-tuning." Directly targets what
ReAct cannot do: carry a lesson from a failed episode into the next one.

## Method

"reinforce language agents not by updating weights, but instead through linguistic
feedback." Three components in a loop: an **Actor**, an **Evaluator**, and a
**Self-Reflection** model. After a trial, the Self-Reflection model turns the
trajectory plus its reward into a verbal summary `sr_t`, appended to an episodic
memory `mem`. The loop runs "until the Evaluator deems τt to be correct."

Memory is bounded: "we bound mem by a maximum number of stored experiences, Ω
(usually set to 1-3) to adhere to max context LLM limitations." For ALFWorld,
"we truncate the agent's memory to the last 3 self-reflections (experiences)."

When to reflect is decided by a **hand-written heuristic**: "if the agent executes
the same action and receives the same response for more than 3 cycles, or if the
number of actions taken in the current environment exceeds 30 (inefficient
planning), we self-reflect."

## Results

- HumanEval pass@1: **91%**, "surpassing the previous state-of-the-art GPT-4 that
  achieves 80%."
- ALFWorld: ReAct + Reflexion completes **130 out of 134** tasks, learning across
  **12** consecutive trials.
- Baseline ReAct-only "performance increase halts between trials 6 and 7" and
  "converging at a hallucination rate of 22% with no signs of long-term recovery."
- Prompting: CoT 6-shot, ReAct 2-shot, self-reflection 2-shot.

## Failure modes

- `[observed]` **The reflection trigger is a hardcoded if-statement.** "the same
  action… more than 3 cycles, or… exceeds 30" actions. This is a loop detector
  written by hand — and loop entrapment is precisely ReAct's signature failure
  (see [[yao2023reactsynergizingreasoningacting]]). So the headline improvement
  rests partly on a domain-tuned constant, not a learned mechanism. Both
  thresholds (3 cycles, 30 actions) are unjustified and unablated. Highly
  attackable: does the gain survive if the agent must *decide for itself* when to
  reflect? The paper never tests this.

- `[stated]` **"Long-term memory" holds three entries.** Ω is "usually set to 1-3",
  truncated to "the last 3 self-reflections", explicitly "to adhere to max context
  LLM limitations." Lessons from trial 1 are gone by trial 5, yet learning is
  reported over 12 trials — so improvement must come from the most recent
  reflections only. Authors "encourage future work to extend the memory component…
  with more advanced structures such as vector embedding databases".

- `[stated]` **Local minima.** "Policy optimization is a powerful approach… but it
  may still succumb to non-optimal local minima solutions." A wrong self-diagnosis
  becomes a memory entry that then steers the next trial — no mechanism detects or
  discards a bad reflection.

- `[observed]` **Requires a resettable environment — excludes most real tasks.**
  The loop is "reset the environment, and start a new trial." Irreversible actions
  (sending a message, a payment, a physical action) admit no retry, so the method
  is silently scoped to simulators and sandboxes. Never stated as a limitation,
  and it rules out the deployment settings agents are actually being built for.

- `[observed]` **Needs an oracle evaluator.** Progress depends on the Evaluator
  deciding correctness — unit tests for HumanEval, environment reward for
  ALFWorld. Tasks whose success is not machine-checkable get no signal, which is
  the majority of useful agent work.

- `[observed]` **91% vs 80% is not a like-for-like comparison.** Reflexion gets
  multiple trials plus test feedback; the GPT-4 pass@1 baseline gets one shot with
  none. The metric name (pass@1) is retained while the budget changes underneath
  it, so the gap conflates method quality with extra attempts.

- `[stated]` **Test-driven reflection breaks on realistic code.** "non-deterministic
  generator functions, impure functions that interact with APIs, functions that
  vary output according to hardware specifications, or functions that invoke
  parallel or concurrent behavior that may be difficult to predict."

## Relevance

The standard answer to "how do agents learn from failure without training." Its
weaknesses are unusually tractable: the hand-tuned trigger, the 3-entry memory,
and the resettable-environment assumption are each a concrete, attackable target,
and the last one blocks the deployment settings that matter most.
