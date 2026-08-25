> Source: Zhao, Wen, Mao et al. (Fudan University / Ant International), arXiv preprint 2026
> URL: https://arxiv.org/abs/2608.17499
> Collected: 2026-08-24
> Published: 2026-08-18
> Bibkey: zhao2026betteragentsmultiturnuser
> Read: full

## Problem

"interactive reinforcement learning typically reduces each rollout to a terminal
reward, assigning the same credit to effective elicitation, errors, and later
repair." Terminal credit "accommodates many valid trajectories, but collapses
their internal structure… The reward says whether a trajectory succeeded, but not
where it changed course."

The claimed free lunch: the next user turn is already inside the rollout, so it is
"noisy, temporally local evidence about the preceding user-to-user segment" and
needs no critic and no extra rollouts.

## Method

A **U2U segment** `a_{k,q}` is everything the agent does — messages, tool calls,
tool results — between two adjacent user turns.

The frozen simulator emits, in one call, a visible utterance `u_{k,q+1}` and a
**private behavioural strategy** `z_{k,q+1}`. Only the utterance enters the agent
context. Interactive GRPO discards `z`; Faca reads it after rollout construction
and maps it to ternary evidence `f_{k,q} ∈ {−1, 0, +1}` (Table 1):

| Strategy event | Interpretation | f |
|---|---|---|
| confirm / close / reveal-piece | progress / completion / requested state elicited | +1 |
| be-vague / invalid | ambiguous / malformed | 0 |
| ask-clarification / challenge-solution / change-mind | local interaction friction / proposal challenged / "goal friction; possibly exogenous" | −1 |

Advantages: outcome branch `A^o_k = (R_k − μ_R)/(σ_R + ε)` from verified terminal
reward `R_k ∈ {0, 1}`; process branch `A^p_{k,q} = (f_{k,q} − μ_f(x,q))/(σ_f(x,q) + ε)`
normalized within the group of rollouts that reach U2U index `q`. Every trainable
token in `a_{k,q}` gets `A_{k,q} = A^o_k + λ A^p_{k,q}`.

`λ` is capped: "We cap its positive value at 0.5 so that reaction credit remains
optimization-relevant while A^o stays dominant in aggregate, reducing, but not
eliminating, reward-hacking risk from simulator bias or misclassified feedback."
Anchoring is by "ordinal U2U index q as the default anchor because exact dialogue
states rarely repeat"; singleton or constant anchors get zero.

Setup: Qwen3-8B and Qwen3-14B, SFT-initialized from the public MUA-RL release,
frozen **DeepSeek-V4-Flash** simulator, three independent training seeds per
method per scale, step-120 checkpoints. The two RL arms share "the frozen
simulator and prompt, agent-visible utterances, SFT initialization, training data,
rollout construction, optimizer, and horizon". **RL training uses only the Airline
and Retail training splits from τ-bench; "neither Telecom nor Bank appears in RL
training."**

## Results

Strict pass@1 (%) over nine τ-family domains, averaged over three step-120 runs:

| Model | τ Air. | τ Ret. | τ² Air. | τ² Ret. | τ² Tel. | τ³ Air. | τ³ Ret. | τ³ Tel. | τ³ Ban. | Avg. |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B | 20.0 | 47.0 | 14.0 | 40.4 | 4.4 | 14.0 | 36.0 | 21.1 | 3.1 | 22.2 |
| + SFT | 14.0 | 39.1 | 24.0 | 36.0 | 2.6 | 16.0 | 40.4 | 28.9 | 3.1 | 22.7 |
| + Interactive GRPO | 28.0 | 52.2 | 32.0 | 46.5 | 30.7 | 39.3 | 50.0 | 29.8 | 3.4 | 34.7 |
| + Faca | 37.3 | 43.8 | 38.0 | 54.4 | 41.2 | 40.0 | 53.5 | 53.5 | 3.4 | 40.6 |
| Qwen3-14B | 12.0 | 59.1 | 26.0 | 49.1 | 2.6 | 14.0 | 50.0 | 23.7 | 3.1 | 26.6 |
| + SFT | 14.0 | 49.6 | 30.0 | 47.4 | 1.8 | 22.0 | 43.0 | 16.7 | 4.1 | 25.4 |
| + Interactive GRPO | 36.0 | 58.3 | 34.0 | 69.0 | 26.3 | 40.0 | 64.6 | 50.6 | 3.8 | 42.5 |
| + Faca | 38.0 | 56.5 | 38.0 | 62.3 | **83.6** | 40.7 | 65.5 | **82.7** | 7.2 | 52.7 |

- 8B: **34.66 ± 0.25 → 40.57 ± 1.04**, "a 5.91-point gain from unrounded domain
  means". 14B: **42.51 ± 0.12 → 52.73 ± 1.53**, a **10.22**-point gain. Per-seed:
  "4.67/6.33/6.75 points at 8B and 8.62/10.14/11.91 points at 14B".
- "Faca leads Interactive GRPO on seven of nine domains at each scale, with its
  largest gain in all four Telecom scale–benchmark cells. It ties one and trails
  one domain at 8B, and trails two Retail domains at 14B."
- Zero-shot Pare-Bench (143 scenarios): strict Pass@1 **6.29% → 10.49%** at 8B and
  **10.49% → 13.29%** at 14B; Pass@4 18.9% → 24.5% and 30.1% → 32.9%.
- Zero-shot Co-Gym (0–100): Faca leads **13 of 16** cells; Travel Delivery Rate
  falls at both scales (83.3 → 82.4 at 8B, 79.4 → 77.5 at 14B). Overall CS
  37.6 → 40.9 (8B), 36.9 → 40.6 (14B).
- Ablation, **single run** from the 8B s1 family (Avg. = nine-domain, Tel.² = τ²
  and τ³ Telecom averaged):

| Condition | λ | Avg. | Tel.² |
|---|---|---|---|
| Aligned | 0.50 | 39.37 | 47.37 |
| Aligned | 0.10 | 36.78 | 45.61 |
| Aligned | −0.50 | 15.08 | 17.11 |
| Shifted one U2U | 0.50 | 33.92 | 29.39 |
| Randomized polarity | 0.50 | 32.66 | 26.32 |
| Outcome-only | 0.00 | 34.70 | 30.26 |

- Telemetry over **154,219** U2U segments: positive reactions rise "from 69.95% to
  82.51%" between the first and last 40 steps, while "nonzero normalized
  process-advantage coverage decreases from 86.16% to 82.50%".
- Of 1,920 group-steps per scale at step 120, **39.27% at 8B and 31.04% at 14B**
  "are all-correct or all-wrong and consequently have zero group-normalized
  outcome advantage".
- Process branch magnitude: "36.00% and 33.79% of a pre-optimization L1
  advantage-magnitude proxy at 8B and 14B, and its weighted magnitude exceeds the
  outcome component in only 6/120 and 1/120 steps".
- Paired 14B s1 checkpoints, τ² Telecom: Faca **96/114** vs Interactive GRPO
  **30/114** (23 both-success, 73 Faca-only, 7 outcome-only, 11 both-fail); τ³:
  **95/114** vs **58/114** (47, 48, 11, 8). But "Faca trails 20/29 versus 24/29 on
  τ³ Service".
- "Across FACA-only wins, error-budget exhaustion accounts for **68/73**
  outcome-only failures on τ² and **28/48** on τ³".
- One matched Hard mobile-data trace: Faca 48 stored events vs 54; 18 vs 21
  assistant messages; 15 vs 17 tool calls; Faca "recovers from two rejected calls"
  and the user completes "four required state changes and a 275 Mbps test", while
  Interactive GRPO "accumulates five such rejections".

## Failure modes

- `[observed]` **The reward is read out of the simulator's private state, so the
  method as evaluated cannot be deployed.** `f` is derived from `z`, a strategy
  label the simulator emits alongside its utterance. Real users do not emit
  `confirm` / `be-vague` / `change-mind` tags. The paper names the missing piece in
  one sentence — "An utterance-only extractor could remove reliance on private
  reaction metadata and extend Faca beyond the instrumented setting toward
  deployment in less controlled environments" — and does not build it. Every
  number here is from the instrumented setting. Building that extractor, measuring
  its agreement with `z`, and re-running is the obvious attack: if agreement is
  0.8, Prop-2-style reasoning from
  [[yuan2026verifiableprocessrewardsagentic]] says the gradient bias is
  proportional to the disagreement, and 5.91 points may not survive it.

- `[observed]` **The simulator supplies the environment, the terminal reward's
  interaction partner, and the process reward — a closed loop.** One frozen
  DeepSeek-V4-Flash both drives the conversation and grades each segment, and the
  agent is optimized to make it emit `confirm`/`close`/`reveal-piece`. `λ ≤ 0.5`
  is an explicit acknowledgement ("reducing, but not eliminating, reward-hacking
  risk from simulator bias"). No second simulator family is tested — "Validation
  across simulator families, architectures, and real users… remains future work" —
  so nothing separates "better agent" from "learned this simulator's tells". The
  positive-reaction rate climbing 69.95% → 82.51% during training is exactly what
  either explanation predicts.

- `[observed]` **Two of nine cells carry the headline number, and both are
  out-of-training-domain in a way that cuts against the paper.** At 14B, τ²
  Telecom moves 26.3 → 83.6 and τ³ Telecom 50.6 → 82.7; those two cells alone
  account for roughly 9.9 of the 10.22-point nine-domain average. Telecom is never
  in RL training, which the paper presents as evidence of transfer, but it also
  means the mechanism account ("Telecom is particularly feedback-rich") is fitted
  to the two cells that produce the result rather than tested against held-out
  domains chosen in advance. Strip Telecom and the remaining seven domains move by
  a few points, with two Retail regressions at 14B.

- `[observed]` **The Faca-only wins are mostly the control running out of a retry
  allowance that is never stated or varied.** "error-budget exhaustion accounts for
  68/73 outcome-only failures on τ²". So the largest single component of the
  headline gap is the interaction between the method and a fixed error budget —
  and the budget's value appears nowhere in the paper. Re-running Interactive GRPO
  with a larger budget is a one-line change that would bound how much of the gain
  is credit assignment versus a hyperparameter. This is the same
  load-bearing-magic-number pattern as open problem 1.

- `[observed]` **Polarity rewards agreeableness, not correctness, and the paper
  says so.** "These labels describe interaction movement rather than user sentiment
  or action correctness." A policy-violating action a satisfied user confirms
  scores +1; a correct refusal the user challenges scores −1. τ-bench's original
  complaint was that terminal reward cannot see policy compliance along the
  trajectory; Faca adds dense credit that is also blind to compliance and is
  positively correlated with pleasing the user. The result is a new reward-hacking
  surface on top of the old one, capped only by `λ`.

- `[observed]` **`change-mind` is punished although the paper concedes it may be
  the user's own doing.** Table 1 annotates it "goal friction; possibly exogenous"
  and still assigns −1. Whenever the simulated user revises its goal for reasons
  unrelated to the preceding segment, that segment is penalized. The frequency of
  `change-mind` among the 154,219 logged segments is not reported, so the size of
  this mislabelled slice is unknown — and it is directly measurable from telemetry
  the authors already have.

- `[observed]` **Every mechanism claim rests on one seed.** Table 4 is "a
  single-run controlled ablation from the 8B s1 experiment family", while the main
  result needed three seeds precisely because run dispersion was ±1.04 at 8B. The
  Randomized-vs-Aligned gap that the paper treats as proof "reaction semantics
  matter" is 39.37 − 32.66 = 6.71 points on n = 1. The λ = −0.5 collapse (15.08)
  is large enough to trust; the Shifted/Randomized ordering is not.

- `[observed]` **Ordinal-index anchoring compares unrelated dialogue states.** The
  normalization group at U2U index `q` is "rollouts that reach q", justified because
  "exact dialogue states rarely repeat" — and the paper admits "This approximation
  can compare different semantic phases after trajectories diverge, especially at
  late singleton turns." Late in an episode `|I(x,q)|` shrinks, so late-turn
  advantages are both noisier and computed across semantically incomparable
  states, while singletons get exactly zero. Long trajectories therefore get the
  weakest process signal — the opposite of what a long-horizon credit method wants.

- `[observed]` **The process signal is decaying, and training stops before that
  matters.** Positive reactions rise to 82.51% while nonzero-advantage coverage
  falls to 82.50%: as the policy converges on eliciting confirmations, within-group
  contrast disappears and `A^p` approaches silence. All results are step-120
  checkpoints; no curve past 120 steps is shown, so whether the gain persists or
  the branch self-extinguishes is untested.

- `[observed]` **No evaluation-noise estimate anywhere.** "Each checkpoint is
  evaluated once, so these standard deviations describe run-level dispersion rather
  than isolating training variation from evaluation stochasticity", and Pare-Bench
  has "no uncertainty interval". With per-domain task sets around 100–114 and
  Telecom swings above 50 points, single-shot evaluation on a stochastic simulator
  is the weakest link in the measurement.

- `[observed]` **τ³ Bank is at the floor for every method and still counts for a
  ninth of the average.** 3.1 / 3.1 / 3.4 / 3.4 at 8B; 3.1 / 4.1 / 3.8 / 7.2 at
  14B. The domain that "additionally requires grounding in an unstructured policy
  collection" is untouched by either credit scheme, so equal-weighting it dilutes
  every reported average while contributing no information about the method.

## Failure modes it fixes

Worth recording separately, because this is the first note here where a paper
*attacks* a listed open problem rather than exhibiting it: the mid-trajectory
recovery story in §6.3 is a direct measurement of within-episode repair. The +1
label explicitly covers "effective elicitation and repair", and the paired
Telecom trace shows the Faca policy recovering from two rejected tool calls where
the control accumulated five and hit the error limit.

## Relevance

The closest thing yet to an attack on open problem 3 in
`wiki/agents/open-problems.md` — it takes exactly the τ-bench terminal-reward
complaint and adds a dense signal, on the τ / τ² / τ³ family, with a properly
matched control (same simulator, same SFT init, same rollout, same optimizer,
credit assignment the only difference). That control design is the standard the
rest of these papers should be held to.

But the signal is simulator-private metadata, so it inherits open problem 4 in a
new form: the improvement mechanism exists only where the environment is
instrumented to explain itself, and the deployment version is unwritten. Note the
pairing with [[fan2026agentprocessbenchdiagnosingsteplevelprocess]] — human step
labels exist for τ²-Bench trajectories, which is one obvious source of ground
truth for the utterance-only extractor this paper leaves as future work.
