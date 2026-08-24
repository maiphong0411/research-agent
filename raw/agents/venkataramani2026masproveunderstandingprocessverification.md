> Source: Venkataramani et al. (Rutgers / Salesforce AI Research), arXiv preprint 2026
> URL: https://arxiv.org/abs/2602.03053
> Collected: 2026-08-24
> Published: 2026-02-03
> Bibkey: venkataramani2026masproveunderstandingprocessverification
> Read: abstract-only

## Problem

"Multi-Agent Systems (MAS) built on Large Language Models (LLMs) often exhibit
high variance in their reasoning trajectories. Process verification … has shown
promise in general reasoning settings, and has been suggested as a potential tool
for guiding coordination of MAS; however, its actual effectiveness in MAS remains
unclear."

## Method

A systematic empirical study rather than a new method. Spans:

- three verification paradigms — "LLM-as-a-Judge, reward models, and process
  reward models";
- two granularities — "agent-level and iteration-level";
- "five representative verifiers and four context management strategies";
- "six diverse MAS frameworks on multiple reasoning benchmarks".

## Results

- **"process-level verification does not consistently improve performance and
  frequently exhibits high variance, highlighting the difficulty of reliably
  evaluating partial multi-agent trajectories."**
- "LLM-as-a-Judge generally outperforms reward-based approaches, with trained
  judges surpassing general-purpose LLMs."
- "a small performance gap between LLMs acting as judges and as single agents".
- "a context-length-performance trade-off in verification".
- Conclusion: "effective and robust process verification for MAS remains an open
  challenge, requiring further advances beyond current paradigms."

## Failure modes

Abstract-only. Note this paper is itself a negative result, so the entries below
are about the strength of that negative claim.

- `[observed]` **A null result over a 3 × 2 × 5 × 4 × 6 grid is hard to attribute.**
  With that many crossed factors and no per-cell numbers in the abstract, "does not
  consistently improve" could mean process verification never helps, or that it
  helps in specific cells the aggregation washes out. The distinction matters
  enormously for whether the direction is dead or just under-specified, and it is
  not resolvable from the abstract.

- `[observed]` **"High variance" is reported as a property of process verification
  but is also the stated property of the systems being verified.** The opening
  premise is that MAS "often exhibit high variance in their reasoning
  trajectories"; the finding is that verification of those trajectories is
  high-variance. Separating verifier variance from system variance requires the
  same repeated-run design that
  [[khanal2026pass1reliabilityscienceframework]] argues nobody does — and the
  abstract does not say how many runs per cell were used.

- `[observed]` **"A small performance gap between LLMs acting as judges and as
  single agents" is the most consequential line and the least explained.** If a
  judge is no better at evaluating a trajectory than it would be at producing one,
  process verification collapses into an ensemble trick, and the whole
  process-reward research programme is resting on an assumption this sentence
  undercuts. Worth a full read on that line alone.

## Relevance

The counterweight the wiki needs. Every other process-reward paper in this batch
argues denser step-level signal is the answer to open problem 3; this one runs the
comparison across six MAS frameworks and reports that it does not reliably work.
Together with [[yuan2026verifiableprocessrewardsagentic]]'s finding that a weak
oracle is worse than no training, this establishes that "add process supervision"
is not a safe default — it is a bet on verifier quality, and in the multi-agent
setting the bet currently loses. This belongs in a `Status: Disputed` block against
any wiki article that presents process rewards as the fix.
