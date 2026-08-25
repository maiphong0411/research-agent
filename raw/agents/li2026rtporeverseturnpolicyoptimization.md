> Source: Li, Cao, Qiao, Hu, arXiv preprint 2026
> URL: https://arxiv.org/abs/2608.18682
> Collected: 2026-08-24
> Published: 2026-08-19
> Bibkey: li2026rtporeverseturnpolicyoptimization
> Read: abstract-only

## Problem

"multi-turn RL training remains highly unstable, often causing severe performance
degradation as the number of turns increases." Three named sources, claimed to be
identified "Through theoretical analysis":

1. "rollout-training context mismatch",
2. "weak turn-level credit assignment under sparse terminal rewards",
3. "asynchronous policy drift when short and long trajectories are optimized under
   different policy versions."

"these issues share a common structural origin in flattened trajectory
optimization".

## Method

**RTPO** (Reverse-Turn Policy Optimization): "organizes multi-turn rollouts as
sparse reverse trees and performs turn-level policy updates in **temporal reverse
order**, aligning each decision with its downstream continuation." Claimed to
enable "causally consistent turn-level credit assignment and on-policy
continuation to control asynchronous drift."

"We provide theoretical guarantees showing that RTPO eliminates context mismatch
and asynchronous drift under the proposed turn-level formulation, reduces credit
bias, and converges to recursive optimality."

## Results

"Experiments on multi-turn agentic RL benchmarks show that RTPO improves upon
trajectory- and turn-level baselines by **21.50%** and **10.76%**, respectively."
Benchmarks are not named in the abstract.

## Failure modes

Abstract-only — inferences from the abstract.

- `[observed]` **The benchmarks are not named and the improvements are relative
  percentages, not points.** "21.50%" and "10.76%" against unnamed baselines on
  unnamed benchmarks is the least checkable form a result can take: a 21.50%
  relative gain could be 2 points on a 10% baseline. Two-decimal precision on an
  unspecified quantity is a presentation smell.

- `[observed]` **"Eliminates" is doing a lot of work.** The guarantees hold "under
  the proposed turn-level formulation" — i.e. the theorems are about the idealized
  objective, not the implemented algorithm with clipping, finite groups, and a
  truncated tree. This is the same gap [[yuan2026verifiableprocessrewardsagentic]]
  is explicit about ("first-order, idealized analyses of an unclipped turn-level
  objective"); whether this paper is equally explicit is the thing to check.

- `[observed]` **Reverse-order updates require the full trajectory before any
  update, which reintroduces the cost the method is meant to save.** "sparse
  reverse trees" suggests pruning, so the sparsity pattern is a hyperparameter that
  decides both compute and which turns get credit — and it is unnamed in the
  abstract.

- `[observed]` **"Asynchronous policy drift when short and long trajectories are
  optimized under different policy versions" is a real and under-discussed
  problem**, and it interacts with the turn-index grouping used by
  [[zhao2026betteragentsmultiturnuser]]: if long trajectories arrive late, the
  advantage normalization group at high turn indices mixes policy versions. That
  connection is worth checking against both papers.

## Relevance

Names a failure mode absent from the wiki: multi-turn RL is *itself* unstable as
turns grow, independently of whether the agent behaves well. That reframes open
problem 5 — some measured inconsistency may be a training artifact rather than an
agent property, which is the hypothesis
`wiki/agents/open-problems.md` entry 5 already floats about domain-tuned constants,
extended to the optimizer. Low confidence pending real numbers; keep as a pointer,
not a citation.
