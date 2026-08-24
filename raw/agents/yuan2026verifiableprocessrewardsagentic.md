> Source: Yuan, Xu et al., arXiv preprint 2026 (under review)
> URL: https://arxiv.org/abs/2605.10325
> Collected: 2026-08-24
> Published: 2026-05-27
> Bibkey: yuan2026verifiableprocessrewardsagentic
> Read: full

## Problem

RLVR "rely on sparse outcome-level feedback. This sparsity creates a credit
assignment challenge in long-horizon agentic reasoning: a trajectory may fail
despite containing many correct intermediate decisions, or succeed despite
containing flawed ones."

Existing PRMs are rejected on reliability grounds, not density: "Learned or
generative process rewards may be noisy, biased, or vulnerable to reward hacking,
while rollout-based estimates can be computationally expensive and high-variance."
Hence: "dense feedback alone is not sufficient: for process rewards to improve
long-horizon reasoning, they must also be reliable and objectively grounded."

## Method

Restrict to "densely-verifiable agentic reasoning problems, where every
intermediate action can be checked by a task-specific verifier
`V : S × A → {0, 1}`", and set `r_t^VPR = V(s_t, a_t)` instead of the sparse
`r_t^OR = 0 (t < T), r_T^OR = I(success)`.

Three instantiations:
- **Search-based** (Tic-Tac-Toe): `A_V(s) = argmax_a Q_MCTS(s, a)`,
  `r_t = I(a_t ∈ A_V(s_t))`. Default **N = 10,000 MCTS simulations per move**.
- **Constraint-based** (Sudoku): for a puzzle with unique solution grid `G*`,
  `V(s_t, a_t) = I(G*[i, j] = d)`.
- **Posterior-based** (Minesweeper): `V = 1` if the action "reveals an unrevealed
  cell with minimum posterior mine probability … or flags a cell with posterior
  mine probability 1, with ties treated as oracle-valid".

Turn-level GRPO: advantages normalized *within a turn index* across the group,
`A_i,t = (r_i,t − μ_t)/(σ_t + δ)` where `I_t = {i : t ≤ T_i}` is the set of
trajectories still active at turn `t`, then plugged into the PPO clipped
surrogate.

Theory (idealized, unclipped): Prop 1 — VPR is first-order equivalent to
"on-policy filtered imitation". Prop 2 — with verifier disagreement rate `ε̄`,
gradient bias `‖ĝ − g*‖ ≤ G·ε̄`, i.e. "oracle error propagates one-to-one into
the gradient, with no horizon-dependent amplification". Prop 3 — in "a controlled
one-parameter Bernoulli regime with coherent (shared-logit) per-step gradients"
where each step is correct independently with probability `p`,
`E[ĝ^VPR] = Θ(T)` but `E[ĝ^OR] = Θ(T p^T) → 0`.

Setup: Qwen3-4B with thinking mode on, all experiments; 100 update steps, group
size 128 trajectories per step. Sudoku is 9×9 with 40 blanks; Minesweeper is 5×5
with 5 mines. Baselines: **OR** (sparse terminal), **MC-PR** ("100 lightweight
Monte Carlo rollouts with the policy model under non-thinking mode", process
reward = TD between consecutive state values).

## Results

In-domain, mean ± std over 5 evaluation runs of 1024 games each. Tic-Tac-Toe is
average return (optimum 0) as 1st / 2nd mover vs a strong MCTS opponent; Sudoku
and Minesweeper are success rate (SR) / completion rate (CR):

| Method | TTT 1st | TTT 2nd | Sudoku SR | Sudoku CR | Mine SR | Mine CR |
|---|---|---|---|---|---|---|
| Optimal | 0.00 | 0.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| Base | −0.31 ± 0.04 | −0.35 ± 0.05 | 3.91 ± 1.35 | 63.24 ± 1.72 | 0.78 ± 0.78 | 73.71 ± 1.46 |
| OR | −0.18 ± 0.03 | −0.21 ± 0.04 | 48.44 ± 2.61 | 82.80 ± 1.18 | 3.91 ± 1.52 | 77.26 ± 1.31 |
| MC-PR | −0.11 ± 0.04 | −0.20 ± 0.05 | 34.73 ± 2.35 | 77.39 ± 1.47 | 2.34 ± 1.11 | 78.67 ± 1.22 |
| VPR | −0.09 ± 0.03 | −0.11 ± 0.03 | 56.25 ± 2.28 | 85.13 ± 0.96 | 10.39 ± 1.86 | 80.27 ± 1.08 |

- In Sudoku "MC-PR even underperforms OR, indicating that noisy step-level
  estimates can be worse than sparse outcome supervision".
- General-reasoning transfer (7-benchmark average, pass@1): Base **60.92**;
  best-per-environment VPR **62.17 (+1.25)** Tic-Tac-Toe, **62.35 (+1.43)**
  Sudoku, **62.59 (+1.67)** Minesweeper.
- Largest single-benchmark gain: GPQA-Diamond, Sudoku-trained VPR **50.20 ± 3.29**
  vs Base **43.13 ± 3.04**. AIME24 best **33.33 ± 4.97** vs Base **30.00 ± 7.20**;
  AIME25 best **21.33 ± 5.26** vs Base **18.33 ± 3.93**.
- MATH-500: Base **84.40 ± 1.83**; Tic-Tac-Toe VPR **83.80 ± 0.35**, Sudoku VPR
  **83.54 ± 0.61** — both below Base.
- Agentic transfer (n = 3): ALFWorld SR Base **24.13 ± 2.40** → Minesweeper VPR
  **28.61 ± 2.28 (+4.48)**. WebShop score Base **27.42 ± 1.00** → Sudoku VPR
  **34.29 ± 1.86 (+6.87)**; WebShop SR Base **1.40 ± 0.20** → Sudoku VPR
  **2.20 ± 0.40 (+0.80)**.
- Oracle-quality ablation on Tic-Tac-Toe: N = 100 gives **−0.48 ± 0.06 /
  −0.52 ± 0.07**, i.e. worse than Base (−0.31 / −0.35); N = 1000 gives
  −0.13 / −0.15; N = 10,000 gives −0.09 / −0.11. OOD average: N = 100 →
  **58.47**, below Base's 60.92; N = 1000 → 61.86; N = 10,000 → 62.17.

## Failure modes

- `[observed]` **The comparison against MC-PR is not budget-matched, and the
  imbalance is roughly two orders of magnitude.** VPR's Tic-Tac-Toe oracle runs
  **10,000 MCTS simulations per move**, on every turn of every one of 128
  trajectories per update, for 100 updates. MC-PR is given **100** rollouts per
  state, and the paper itself names compute as MC-PR's binding constraint ("its
  signal can be noisy as the computational cost of MC rollouts limits the number
  of simulations"). No verifier-compute accounting appears anywhere. Since the
  ablation shows VPR's own quality is monotone in oracle compute (N = 100 is worse
  than no training), the natural reading of Table 1 is partly "more search wins",
  not "verification beats estimation". Giving MC-PR 10,000 rollouts is the
  experiment that would settle it and it is absent.

- `[observed]` **The Sudoku verifier is the answer key, so that instantiation is
  filtered imitation on labelled solutions, not process verification.**
  `V(s_t, a_t) = I(G*[i, j] = d)` reads the unique solution grid. Prop 1 states
  this outright — VPR "admits a first-order interpretation as on-policy filtered
  imitation" — but the framing throughout is that VPR extracts supervision from
  *task structure*. A constraint solver checking consistency with the remaining
  solution space (what Figure 2 depicts) is a materially weaker oracle than the
  solution itself, and the paper reports only the latter. Sudoku is also the
  environment with the largest in-domain jump (3.91 → 56.25 SR), so the headline
  in-domain result leans on the least generalizable of the three verifiers.

- `[observed]` **For Sudoku the training reward and the evaluation metric are the
  same function.** CR is "fraction of correctly filled cells"; the per-step reward
  is `I(G*[i, j] = d)` per filled cell. Summing the reward over an episode *is*
  the metric. The Sudoku CR row (85.13 vs OR's 82.80) therefore cannot separate
  "learned to reason" from "optimized the scoreboard directly", and it is the
  frozen-harness violation that `wiki/agents/open-problems.md` entry 3 keeps
  finding. SR (fully solved puzzles) is the only Sudoku number not affected.

- `[stated]` **Inapplicable to the setting the introduction uses as motivation.**
  The problem statement invokes tool use, multi-turn planning, and SWE-bench;
  the experiments are Tic-Tac-Toe, Sudoku, and Minesweeper — no tools, no external
  state, no irreversible actions, and a verifier that must be constructed by hand
  per environment. "extending it to less structured, open-ended environments
  remains an important challenge" is the paper's own summary, and it is the whole
  gap: densely-verifiable is precisely the complement of agentic-in-the-wild.

- `[observed]` **The ablation shows the method is net-harmful under the oracle
  quality a real agentic task would have.** N = 100 is worse than the untrained
  base model both in-domain (−0.48 vs −0.31) and out-of-domain (58.47 vs 60.92),
  "with degradation across every benchmark". Any deployment where the verifier is
  an LLM judge, a partial test suite, or a heuristic sits somewhere on that curve,
  and the paper gives no way to locate it: `ε̄` is the quantity Prop 2 bounds the
  bias by, and no `ε̄` value is measured for any N. Estimating `ε̄` per oracle, and
  finding the threshold where VPR crosses from helpful to harmful, is the missing
  experiment and a well-scoped attack.

- `[observed]` **Prop 3's horizon advantage is derived in the regime the failure
  doesn't occur in.** `E[ĝ^OR] = Θ(T p^T)` assumes "each step is correct
  independently with probability p" plus "coherent (shared-logit) per-step
  gradients". Independence across steps is the assumption long-horizon agent
  measurements keep falsifying — errors are positively correlated, a confused
  agent stays confused. Under correlation the OR signal is not diluted the same
  way, so the analytic case for dense rewards is weakest exactly at the long
  horizons it is invoked for.

- `[observed]` **Transfer gains sit inside their own error bars.** AIME24 moves
  30.00 ± 7.20 → 33.33 ± 4.97 (n = 10); AIME25 18.33 ± 3.93 → 21.33 ± 5.26. The
  7-benchmark averages gain +1.25 to +1.67. WebShop SR goes 1.40% → 2.20% at
  n = 3, an 0.8pp move on a ~1% base where the environment is essentially unsolved
  by every method. The claim that "VPR teaches reasoning skills that are not
  narrowly tied to the training environment" rests on aggregates over benchmarks
  whose individual movements are not separable from noise.

- `[observed]` **Averaging conceals per-benchmark regressions.** MATH-500 drops
  below Base for both Tic-Tac-Toe-trained (83.80) and Sudoku-trained (83.54) VPR,
  and BBH drops for Minesweeper-trained VPR (88.34 vs 88.39). The text reports
  "Every VPR-trained model improves the average score over the base across all 7
  benchmarks" — true of the average, not of all 7.

- `[observed]` **One base model, one scale, no seed reporting.** Everything is
  Qwen3-4B with thinking on. The five "evaluation runs" vary evaluation sampling,
  not training seeds, so the ± values do not cover training variance — which for
  100-step GRPO at group size 128 is the dominant source. Nothing establishes the
  method survives a second family or a larger model.

- `[observed]` **Turn-level group normalization silently reweights late steps.**
  Advantages are normalized over `I_t = {i : t ≤ T_i}`, the trajectories still
  active at turn `t`. Late in an episode `|I_t|` shrinks, so `σ_t` is estimated
  from few samples and late-turn advantages get noisier and larger — in the
  hardest environments (Minesweeper SR 10.39%) most trajectories die early, so the
  surviving-tail steps dominate. No ablation on `δ` or on alternative
  normalizations is reported.

## Relevance

The cleanest available statement of *why* trajectory-aware rewards should beat
terminal-state rewards — open problem 3 in `wiki/agents/open-problems.md` — with a
theoretical bound (bias ∝ verifier error, no horizon amplification) that says
where the idea breaks. It also inverts the entry usefully: the ablation is
evidence that a *bad* process reward is worse than a sparse outcome reward, so
"add step-level supervision to τ-bench" is not automatically an improvement, it is
a bet on verifier quality. Combined with `fan2026agentprocessbench…` (human step
labels on τ²-Bench trajectories, no oracle available), the pair frames the real
question: what is `ε̄` for the best obtainable verifier on a genuinely agentic
task, and is it below the harmful threshold.
