> Source: Khanal et al., arXiv preprint 2026
> URL: https://arxiv.org/abs/2603.29231
> Collected: 2026-08-24
> Published: 2026-03-31
> Bibkey: khanal2026pass1reliabilityscienceframework
> Read: full

## Problem

Benchmarks measure capability — "whether a model succeeds on a single attempt" —
while "production deployments require reliability — whether a model consistently
succeeds across repeated invocations on tasks of varying duration." Existing
benchmarks are "structurally blind to this divergence because they report only
pass@1 on short, atomic tasks."

Directly picks up τ-bench's thread and names its limit: τ-bench introduced pass^k
and showed "GPT-4o achieves 61% pass@1 but 25% pass@8 on retail agent tasks",
but "τ -bench tasks are short (minutes to complete) and the study does not treat
task duration as an independent variable."

## Method

Four metrics over a duration axis:

- **RDC** (Reliability Decay Curve): `d ↦ pass^k(M, d)` across duration buckets.
  Summarized by **RDS**, "the slope of a linear regression of GDS on bucket index
  b ∈ {0, 1, 2, 3}".
- **VAF** (Variance Amplification Factor): Definition 4 is
  `σ²[pass@1 | d = long] / σ²[pass@1 | d = short]`.
- **GDS** (Graceful Degradation Score): `Σ wi · 1[subtask si completed correctly]`
  over 3–6 hand-weighted subtasks per task, weights summing to 1.
- **MOP** (Meltdown Onset Point): first step `t*` where sliding-window tool-call
  entropy `H(t*) > θH` **and** `H(t*) − H(t* − w) > δ`. The second condition is
  claimed to "distinguish meltdown from legitimate task exploration".

Benchmark: 396 tasks, four duration buckets (≤ 5 min, 5–30 min, 30–120 min,
≥ 120 min human time) × three domains (SE, Web Research, Doc Processing), 33
tasks per cell. Two scaffolds: ReAct, and ReAct plus an `add_to_memory(note)`
episodic scratchpad injected into the system prompt every turn.

Hyperparameters: "Temperature: 0.7; maximum steps: 70 …; maximum output tokens
per step: 2,048; maximum tool result characters: 4,000; maximum nudges: 3; MOP
window size: 5; per-episode input token budget: 120,000; loop detection
threshold: 3 repeated (tool, args) pairs within 6 steps."

## Results

Scale: "396 tasks × 10 models × k = 3 × 2 scaffolds = 23,760 planned episodes;
23,392 completed after deduplication." Validation run: 19 tasks, 12 models,
1,368 episodes, total cost **$4.26** (≈ **$0.0032** per episode); 46
quota-failure episodes excluded leaving 1,322 over 9 paid models. Full study
"approximately $40.83 for short+medium", total estimated **$80–120**.

- Aggregate pass@1: **76.3%** (short) → **59.8%** (medium) → **50.5%** (long) →
  **52.1%** (very long) — "a 24.3 percentage-point decline".
- Domain: SE aggregate GDS **0.90 → 0.44** (drop −0.46); WR 0.80 → 0.63 (−0.17);
  DP **0.74 → 0.71** (−0.03).
- VAF: MiniMax M2.5 **2.60**, DeepSeek V3 **2.49**, Kimi K2.5 **2.48**, GLM-4.5
  Air **2.37**, Qwen3 32B **1.26**, Mistral 24B 1.02, Llama 3.3 70B 0.98, Qwen3
  30B 0.71, Mistral Nemo 0.42, Llama 3.1 8B **0.26**.
- Super-linearity vs i.i.d. Bernoulli: Qwen3 30B geometric prediction
  `0.758⁴ ≈ 33.0%` vs observed **22.2%** ("1.5× below baseline"); Mistral Nemo
  `0.535² ≈ 28.6%` vs observed **12.1%** ("2.4× below baseline").
- Early-failure rate (episodes terminating before the first subtask): GLM-4.5 Air
  **1% → 25%** short to very long; DeepSeek V3 **2% → 11%**.
- MOP: thresholds "H* = 1.711 bits, δ* = 0.000, calibrated from 1,590
  short-horizon baseline episodes; window w = 5". Very-long meltdown rate
  DeepSeek V3 **19%** (median step 17), MiniMax M2.5 **13%** (step 24), Kimi K2.5
  4%; "All other models have meltdown rates of 0–4% across all buckets."
- Memory scaffold on long+very-long GDS: "6 models are hurt, 4 are neutral
  (within ±0.03 GDS)", largest penalties Kimi K2.5 **−0.14**, Mistral 24B
  **−0.13**. "The memory scaffold never helps."
- Rank inversion: GLM-4.5 Air 94.9% short → **66.7%** very long; Llama 3.3 70B
  74.7% short → **54.5%** very long while Qwen3 30B 75.8% short → **34.3%**.
- Per-domain long+very-long pass@1: GLM-4.5 Air SE 77.3%, DP 90.9%, but WR
  **50.0%**; Llama 3.3 70B WR 68.2% vs SE **12.1%**. SE spread 0.5% (Llama 3.1
  8B) to 82.3% (Kimi K2.5), "an 82-point gap".
- Theory claim: with positive inter-step error correlation ρ, task failure is
  `Ω(ϵ · e^{ρT})`, so "Reducing ρ … is therefore a higher-priority training
  objective than reducing ϵ alone".

## Failure modes

- `[observed]` **The MOP spike condition is inert — δ* = 0.000 deletes the
  mechanism the paper credits for the metric's validity.** Section 3.5 argues the
  secondary condition `ΔH > δ` "requires a spike in entropy, not just sustained
  high entropy, which distinguishes meltdown from legitimate task exploration."
  Calibration then returns `δ* = 0.000`, so any non-decreasing entropy satisfies
  it and MOP collapses to the single threshold `H(t) > 1.711`. Every meltdown
  number, including the headline 19%, is therefore a sustained-high-entropy
  detector, and the exploration/meltdown distinction the paper claims is
  unsupported by its own calibration. Attacking this needs only a re-run with
  δ forced positive; if the 19% survives, the paper's own framing was wrong.

- `[observed]` **The loop-detection circuit breaker censors the failure mode MOP
  is supposed to measure.** Runs abort on "3 repeated (tool, args) pairs within 6
  steps" — which is precisely the *low*-entropy repetition that ReAct-lineage
  work calls loop entrapment. MOP can then only ever fire on high-entropy
  spirals, because the low-entropy ones were terminated before they could be
  scored. The "MOP paradox" (frontier models melt down most) is consistent with
  an artifact of this asymmetry: rote low-entropy models get cut by the breaker
  and never register a meltdown. Untangling this needs the meltdown rates
  recomputed with loop detection disabled.

- `[observed]` **Measured variance is a chosen hyperparameter.** "Episodes use
  temperature 0.7 to induce the stochasticity required to estimate reliability."
  VAF, pass^k, and the entire variance story are conditional on that constant,
  which is never ablated. A deployment running at temperature 0 has a different
  reliability profile than any number in this paper, so the practitioner advice
  ("prefer models with … high VAF") is not transferable as stated.

- `[observed]` **VAF is defined one way and computed another.** Definition 4 is
  `σ²[long] / σ²[short]`; Sections 5.3 and 6.2 and Table 10 all report
  `σ²(pass@1 | long+vlong) / σ²(pass@1 | short+medium)`. Similarly RDS is defined
  in §3.2 as the regression slope of **GDS** on bucket index, while Table 5's
  caption calls it the "linear regression slope of **pass@1** vs. integer bucket
  index". Two of four headline metrics have drifting definitions, so external
  replication would not reproduce the published values.

- `[observed]` **The step budget is stated twice with different values.** §4.4:
  "Each episode runs until the agent calls finish() or reaches a 50-step limit."
  §5.1 hyperparameters: "maximum steps: 70 (headroom above the 60-step estimate
  for very-long tasks)". Since very-long tasks are estimated at ~60 steps, the
  choice between 50 and 70 decides whether the hardest bucket was even runnable —
  it is not a cosmetic discrepancy.

- `[observed]` **k = 3 cannot support a pass^k claim at the strength τ-bench
  made.** The paper positions itself as extending τ-bench's pass^8 analysis
  across duration, but runs only 3 repeats, with per-cell 95% CIs of "±4–10%".
  Several headline gaps (VAF CIs such as [1.53, 5.24] for MiniMax M2.5) are wide
  enough that the frontier/mid-tier bifurcation rests on 3 samples per task.

- `[observed]` **GDS smuggles in hand-assigned criticality weights.** Every task
  is decomposed into "3–6 subtasks with assigned criticality weights", ordered
  "from simplest to hardest (reflecting likely agent progress) to maximize the
  informativeness of GDS". The weights are author-chosen, tuned for
  informativeness, and never ablated; GDS is the primary metric "when pass^k is
  near zero", i.e. exactly where the weights dominate the result. The example
  given (+0.25/+0.35/+0.20/+0.20) has no stated derivation.

- `[stated]` **Human-time duration is the wrong axis and the paper's own data say
  so.** "DP-L tasks classified as 'long' by human-time are tractable for agents
  in 4–8 tool calls", against 15–25 for SE tasks of equivalent human duration.
  The independent variable of the whole study is therefore only loosely coupled
  to agent difficulty, which is why the aggregate RDC is non-monotonic (long
  50.5% < very long 52.1%). The authors carry `n*` (agent step estimate) per task
  but do not use it as the primary axis.

- `[stated]` **No proprietary frontier models.** "We do not evaluate GPT-4o,
  Claude 3.7, Gemini 2.0 Ultra … which are likely more reliable than the models
  studied here." The tier boundary claim ("capability infrastructure required for
  reliable long-horizon completion requires more than the medium-tier models
  examined here provide") is thus about the open-weight frontier only.

- `[observed]` **368 episodes disappear without explanation.** 23,760 planned vs
  "23,392 completed after deduplication". What was deduplicated, and whether it
  was distributed evenly across buckets, is never stated — and the paper's own
  §7.3 argues completion rate should be "a first-class validity metric".

- `[observed]` **The decomposition recommendation assumes away the thing being
  measured.** "decomposing into n independent short segments improves expected
  completion from p_VL toward p_S (assuming subtask independence)" — but §6.1's
  central empirical finding is that errors are *positively correlated* across
  steps. The 41.5 pp gain quoted for Qwen3 30B is an upper bound derived from an
  assumption the paper refutes two sections earlier, and is untested.

## Relevance

This is the paper open problem 5 (`wiki/agents/open-problems.md`) asked for: it
attacks pass@1 blindness directly and supplies the duration-stratified pass^k
data τ-bench did not. Two findings matter most for the existing wiki: memory
scaffolds *never* help at long horizons across 10 models, which cuts against the
Reflexion-lineage assumption in `self-reflection-and-memory.md`; and the claim
that reducing inter-step error correlation ρ beats reducing per-step error ϵ,
which is a training-objective framing of open problem 2 (nothing recovers within
a trajectory). The δ* = 0.000 and loop-breaker findings above are themselves a
fresh instance of open problem 3 — the evaluation is more permissive than the
claim it supports.
