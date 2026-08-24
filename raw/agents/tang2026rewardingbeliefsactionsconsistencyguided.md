> Source: Tang et al., arXiv preprint 2026
> URL: https://arxiv.org/abs/2605.20061
> Collected: 2026-08-24
> Published: 2026-05-19
> Bibkey: tang2026rewardingbeliefsactionsconsistencyguided
> Read: abstract-only

## Problem

"in partially observable environments, incomplete observations cause agent beliefs
to drift over time, while delayed rewards obscure the causal impact of
intermediate decisions, exacerbating temporal credit assignment challenges."

## Method

**ReBel** (Reward Belief), a process-level RL algorithm that "explicitly models
structured belief states to summarize interaction history and guide subsequent
policy learning". Two components:

- **belief-consistency supervision** — "converting discrepancies between predicted
  beliefs and observed feedback into dense self-supervised signals **without
  requiring external step-wise annotations or verifiers**".
- **belief-aware grouping** — "compare trajectories under similar belief states,
  yielding more robust and lower-variance advantage estimates."

## Results

On ALFWorld and WebShop: "improves task success by up to **20.4** percentage
points over the episode-level baseline GRPO and increases sample efficiency by
**2.1×**." Code released.

## Failure modes

Abstract-only — inferences from the abstract.

- `[observed]` **The verifier-free claim is the interesting part and the likely
  weak point.** Belief-consistency supervision rewards the agent for beliefs that
  match subsequent observations, with no external check. That is a
  self-consistency objective, and self-consistency is satisfiable by an agent that
  predicts conservative, easily-confirmed beliefs — or that takes actions whose
  outcomes it can predict rather than actions that make progress. Whether the
  paper tests for this degenerate solution is the first thing to check. If it does
  not, this is a well-scoped attack: construct a task where the belief-consistent
  policy and the task-optimal policy diverge.

- `[observed]` **"Up to 20.4 percentage points" is a maximum, not a mean**, and the
  abstract gives neither the baseline value nor which environment produced it. On
  ALFWorld and WebShop, where absolute success rates in the surrounding literature
  are often low, a 20.4pp move is a very different claim depending on whether the
  base is 10% or 60%.

- `[observed]` **ALFWorld and WebShop are the standard pair and both are 2020–2022
  benchmarks.** They are also the transfer targets used by
  [[yuan2026verifiableprocessrewardsagentic]], where absolute WebShop success rates
  sat around 1–2% — so cross-paper comparison on these two environments is
  currently impossible without matching harnesses.

- `[observed]` **"Structured belief states" implies a hand-designed schema** whose
  form is not given in the abstract. If the belief representation is task-specific,
  the method's portability is bounded by whoever writes the schema — the same
  dependency [[yuan2026verifiableprocessrewardsagentic]] has on a per-environment
  oracle, relocated from the reward to the state representation.

## Relevance

The one paper in this batch that claims dense process credit **without** a verifier
or step-level labels, which if it holds is the way around the dependency that
bounds every other process-reward method here (see
[[yuan2026verifiableprocessrewardsagentic]] on bias scaling with verifier error,
and [[rosset2026artbuildingverifierscomputer]] on how hard a good verifier is to
build). Belief drift under partial observability is also a sharper mechanism for
open problem 2 than "loop entrapment": it names *what* degrades, not just that the
trajectory fails. Candidate for promotion to a full read.
