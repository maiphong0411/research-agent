# Open Problems in Agentic Systems

> Sources: Yao et al., 2023-03-10; Shinn et al., 2023-03-20; Yao et al. (Sierra), 2024-06-17; Venkataramani et al., 2026-02-03; Tang et al., 2026-02-06; Khanal et al., 2026-03-31; Rosset et al., 2026-04-05; Tang et al., 2026-05-19; Yuan, Xu et al., 2026-05-27; Fan et al., 2026-06-01; Yang et al., 2026-07-21; Wu et al., 2026-07-30; Fan et al., 2026-08-04; Chen et al., 2026-08-07; Yang et al., 2026-08-11; Wang et al., 2026-08-13; Li, Zhu, 2026-08-18; Peng et al., 2026-08-18; Zhao, Wen, Mao et al., 2026-08-18; Li, Cao, Qiao, Hu, 2026-08-19; Yu et al., 2026-08-19
> Raw: [ReAct](../../raw/agents/yao2023reactsynergizingreasoningacting.md); [Reflexion](../../raw/agents/shinn2023reflexionlanguageagentsverbal.md); [tau-bench](../../raw/agents/yao2024taubenchbenchmarktoolagentuserinteraction.md); [MAS-ProVe](../../raw/agents/venkataramani2026masproveunderstandingprocessverification.md); [The Value of Variance](../../raw/agents/tang2026valuevariancemitigatingdebate.md); [Beyond pass@1](../../raw/agents/khanal2026pass1reliabilityscienceframework.md); [Universal Verifier](../../raw/agents/rosset2026artbuildingverifierscomputer.md); [ReBel](../../raw/agents/tang2026rewardingbeliefsactionsconsistencyguided.md); [VPR](../../raw/agents/yuan2026verifiableprocessrewardsagentic.md); [AgentProcessBench](../../raw/agents/fan2026agentprocessbenchdiagnosingsteplevelprocess.md); [Agents in the Wild](../../raw/agents/yang2026agentswildresearchmeets.md); [ClawTrack](../../raw/agents/wu2026clawtracktracelevelevaluationimprovement.md); [Screenshots or Tools](../../raw/agents/fan2026screenshotstoolselicitingtool.md); [The Horizon Gap](../../raw/agents/chen2026horizongapplanningmemory.md); [ReTree](../../raw/agents/yang2026selfcorrectinglonghorizonsearchagents.md); [CrEST](../../raw/agents/wang2026teachmagnitudedirectionverifierbounded.md); [Auditing Self-Evolution](../../raw/agents/li2026auditingselfevolutionfinancialagents.md); [WER](../../raw/agents/peng2026writeexecuterefineskill.md); [Faca](../../raw/agents/zhao2026betteragentsmultiturnuser.md); [RTPO](../../raw/agents/li2026rtporeverseturnpolicyoptimization.md); [EvoResearcher](../../raw/agents/yu2026trainingfreeinferencetimeselfreflectioncostbounded.md)
> Updated: 2026-08-24

## Overview

Recurring weaknesses, not per-paper limitations. An entry earns a place here only
when it appears in more than one method — a single paper's flaw is an anecdote, the
same flaw across several is a problem the field has not solved. Each entry names
which methods exhibit it and what attacking it would require.

Compiled from 21 papers. The first five entries were written from three papers and
are now revised against eighteen more; where a 2026 paper has
partially answered one, the original framing is kept with a dated Status block
rather than deleted, because how the problem was framed before it was attacked is
itself worth keeping.

Entries 6–9 are new and were only visible once the corpus was large enough.

---

## 1. Load-bearing magic numbers

**Exhibited by:** ReAct — backoff at 7 steps (HotpotQA) and 5 (FEVER), switch to
ReAct when majority vote falls below n/2. Reflexion — reflect after "more than 3
cycles" of repetition or "exceeds 30" actions. Khanal et al. — a meltdown detector
whose calibrated spike threshold comes back as **δ* = 0.000**, plus a loop-detection
circuit breaker at "3 repeated (tool, args) pairs within 6 steps", plus
**temperature 0.7** chosen "to induce the stochasticity required to estimate
reliability". Faca — a process-credit weight capped at λ = 0.5 by hand "so that
reaction credit remains optimization-relevant". Universal Verifier — process labels
"binarized at a ≥ 0.8 threshold", unstated top-k, unstated ensemble size. ReTree —
140-word summaries, top-5 lexical evidence, at most six atomic facts per step, eight
searches.

Three years on, this has gone from a pattern to the norm, and two 2026 instances
show the constants are not merely untuned but sometimes *self-defeating*:

- Khanal et al. argue their meltdown metric's second condition — an entropy *spike*
  rather than sustained high entropy — is what "distinguishes meltdown from
  legitimate task exploration". Calibration returns that threshold as zero, so the
  condition is vacuous and every meltdown number, including the headline 19%, is a
  sustained-high-entropy detector.
- The same study's loop-detection breaker aborts exactly the low-entropy repetition
  that ReAct-lineage work calls loop entrapment — so the metric can only fire on
  high-entropy spirals, which is consistent with its counter-intuitive finding that
  frontier models melt down most.

Faca is the honest counter-example worth naming: its λ is a hand-set cap, but the
paper ablates it (λ = 0.50 → 39.37 overall; λ = 0.10 → 36.78; λ = −0.50 → 15.08),
which is what the rest of this list does not do.

**What an attack requires:** unchanged from the original framing — show whether reported gains
survive when the agent decides for itself. But there is now a cheaper and more
damaging version: **re-run one published result with a load-bearing constant forced
to a different value and show the finding inverts.** The δ* = 0.000 case is
available immediately, needs no new model, and the paper's own text supplies the
argument for why it should matter.

---

## 2. Nothing recovers within a trajectory

**Exhibited by:** ReAct — loop entrapment, where "the model repetitively generates
the previous thoughts and actions", and non-informative search at 23% of errors,
which gives the model "a hard time to recover". Reflexion — recovery is achieved
only by abandoning the episode and restarting from a reset environment.

The field had two options for a derailed trajectory: continue and fail, or throw it
away and start over. Mid-trajectory repair — backtracking to a decision point,
retracting a bad thought, re-planning from partial progress — was absent from all
three papers this file was first compiled from.

> **Status: Outdated** (2026-08-24)
> A mechanism now exists. ReTree (Yang et al., 2026) treats retrieval-induced error
> cascade as a *structural state-repair* problem: an evidence tree where an edge
> means "derived from parent's evidence", and on a confirmed contradiction it
> returns to the node that introduced the refuted fact, repairs it, regenerates that
> node's summary, prunes dependent descendants and resumes — Doyle's 1979
> truth-maintenance principle inside an LLM loop. It names the exact gap this entry
> described: existing methods often "replace erroneous facts without repairing
> downstream reasoning derived from them". Against Full-Trajectory ReAct across
> 2,149 questions it gains 8.3–25.6 points per dataset, 13.9 pp pooled.
>
> The problem is not closed. The repair fires in only **9.6–17.5% of runs**, the
> paper never reports accuracy conditioned on whether it fired, there is one seed
> (seed 0) and no confidence intervals — so the 2.2–4.7 pp gap over a
> mechanism-matched flat-memory control is not yet attributable to the repair. And
> the horizon is eight searches with peak baseline context of **1,920 characters**,
> far below any context limit, so this is not yet a long-horizon result.

Two adjacent 2026 results reframe what recovery should even target:

- **The compounding model that motivates repair is wrong.** Degradation is bimodal,
  not smooth — Vending-Bench, on runs exceeding 20M tokens, finds most runs profit
  and some derail into meltdown loops "from which they rarely recover", with
  "no clear correlation with the context window filling up". So the quantity to
  attack is not per-step accuracy. Khanal et al. make this precise: with positive
  inter-step error correlation ρ, failure scales as `Ω(ϵ · e^{ρT})`, making
  "Reducing ρ … is therefore a higher-priority training objective than reducing ϵ alone".
- **Intrinsic self-correction may worsen with scale.** The accuracy-correction
  paradox: the weaker of three models (66% base accuracy) self-corrects at 26.8%
  while the strongest (94%) manages 16.7%, with detection rate not predicting
  correction success. The Error Depth Hypothesis — stronger models make fewer but
  deeper errors — implies external grounding is structural, not a temporary crutch.

**What an attack requires:** the stratified analysis ReTree omits (accuracy
conditioned on whether a backtrack fired) is the cheapest experiment on this whole
page and needs no new runs. Beyond that: a repair mechanism evaluated at a horizon
where context actually binds, targeting error *persistence* rather than error rate.

---

## 3. Measurement flatters the method

**Exhibited by:** ReAct — label ambiguity is 29% of judged cases against an EM gap
to CoT of 27.4 vs 29.4, so the comparison sits inside annotation noise. Reflexion —
91% vs 80% compares multi-trial-with-feedback against single-shot while keeping the
pass@1 label. τ-bench — terminal-state reward means "r = 1 might be a necessary but
not sufficient condition", so a policy-violating trajectory scores 1.

This was the best-supported entry in the original compile and it is now the
best-*measured*. It
has stopped being an inference and become a quantity.

**The size of the gap.** Re-scoring three computer-use benchmarks with a
purpose-built rubric verifier: WebVoyager's native verifier reports **74.6%** where
the rubric verifier reports **37.9%**; Online-Mind2Web 32.2 vs 15.8; WebTailBench
39.6 vs 23.2. Native-verifier false positive rates exceed 20% on every
benchmark/agent pair. Caveat that keeps this from being a calibrated estimate: "The
UV is treated as the reference label", its own agreement with humans is κ 0.58–0.64,
and its near-zero FPR is an optimization constraint with a corresponding FNR of
0.31–0.32.

**SWE-bench, audited.** 32.67% of successful patches involve solution leakage; a
further 31.08% pass only because the test suite is too weak; filtering both drops
one leaderboard-topping system from **12.47% to 3.97%**. Independently, passing
patches diverge behaviorally from human ground truth in nearly 30% of cases. Across
agentic benchmarks generally, setup and reward-design flaws "can over- or
under-estimate reported performance by up to" 100% "in relative terms".

**New variants of the failure this entry did not anticipate:**

- *Benchmark noise as a ceiling, not a floor.* GUI agents "plateau around" 60% on
  AndroidControl "because benchmark noise — ambiguities and factual errors in the
  benchmark itself — caps the achievable score". Same shape as ReAct's 29% label
  ambiguity, three years later.
- *Harness compatibility swamping the effect.* A prompt-envelope mismatch between a
  WebArena text-action format and a function-calling executor held utility at 0.319
  instead of 0.756 — a 43-point swing larger than any effect the study was measuring.

τ-bench's specific admission also now has a human-labelled remedy: AgentProcessBench
provides 8,509 human step annotations (IAA 89.1%, κ 0.767) over trajectories drawn
partly from τ²-Bench.

**What an attack requires:** the τ-bench-specific fix named originally — a
trajectory-aware reward checking policy compliance along the path — now has its
ground truth available. What is *still* missing, and is the better target: nobody
has calibrated the gap. Every number above is either a disagreement with an
uncalibrated reference verifier or a secondary citation. A study that measures
verifier error against multiple independent human annotators, on one benchmark, and
reports a confidence interval on the overstatement, does not exist.

---

## 4. Retry, reset, and oracle assumptions exclude deployment

**Exhibited by:** Reflexion — requires "reset the environment, and start a new
trial" plus an Evaluator that can judge correctness. τ-bench — measures precisely
the opposite setting, where the first attempt is the only one and pass^8 is the
target. VPR — applicable only where "every intermediate action can be checked by a
task-specific verifier", instantiated on Tic-Tac-Toe, Sudoku and Minesweeper while
motivated by tool use and SWE-bench. Faca — the process signal is *simulator-private
metadata*; real users do not emit strategy labels, and the utterance-only extractor
that would deploy it is future work. WER — needs a programmatic verifier, while its
motivating case is novel software with no reference implementation.

The pattern has sharpened. Methods are still developed where success is
machine-checkable and measured where it is not, but 2026 adds a second form: methods
developed where the *environment explains itself* — emitting strategy labels, oracle
values, or unit-test outcomes — and deployed where it does not.

> **Status: Outdated** (2026-08-24)
> The architectural half of this entry has a partial answer. WER (Peng et al., 2026)
> trains a Skill Optimizer *outside a frozen executor*: repeated execution and
> verifier scoring happen during optimizer training, so the deployed executor is
> single-pass. That is the "transfer lessons learned in a resettable environment into
> a single-pass deployment" framing this entry called closer to a thesis than a
> paper. It is a partial answer because the verifier requirement survives intact, and
> the gain over doing nothing is +7.80 and +3.85 points against a premise that
> agent-authored skills run **8-11 points worse than using no skill**.

Also worth recording: an industry-authored tutorial, Agents in the Wild, names
the same gap from the deployment side and lists what practitioners actually do about
it — verification pipelines, fallback mechanisms, human-in-the-loop supervision. Not
citable for numbers, but it is direct evidence the gap is felt outside the
literature.

**What an attack requires:** unchanged in substance. The most tractable concrete
version is now Faca's own stated future work: build the utterance-only reaction
extractor, measure its agreement against the privileged label, and see how much of
the +5.91/+10.22 survives. Per VPR's bias bound, the loss should be proportional to
the disagreement rate — which makes this a test of that theory as well.

---

## 5. Consistency is named but unaddressed

**Exhibited by:** τ-bench — "pass^8 < 25%", closing on "the need for methods that
can improve the ability of agents to act consistently". Neither ReAct nor Reflexion
reports variance across trials at all.

> **Status: Outdated** (2026-08-24)
> The measurement half is done. Khanal et al. (2026) extend pass^k along a duration
> axis: 396 tasks, four duration buckets, three domains, 10 models, 23,392 episodes.
> Aggregate pass@1 falls 76.3% → 52.1%, a 24.3 pp decline, super-linear against an
> i.i.d. baseline. Domain dominates duration (software-engineering partial credit
> 0.90 → 0.44 while document processing holds 0.74 → 0.71), and capability rank
> diverges from reliability rank enough to reverse a deployment decision.
>
> The finding that changes this entry's framing: **variance amplification is a
> capability signature.** VAF bifurcates at 2.37 and above for the frontier cluster
> versus 1.26 and below for mid-tier models, because weak models "fail uniformly
> rather than variably" — there is no variance to amplify. So some of the pass^8
> collapse is a model that has found strategies and does not always execute them,
> not a model that is broken.

The *method* half remains open, and one 2026 attempt suggests the obvious approach
is wrong. "The Value of Variance" quantifies uncertainty at intra-agent,
inter-agent and system levels — then trains the system to minimize disagreement,
penalizing "self-contradiction, peer conflict, and low-confidence outputs", and
reports "reducing system disagreement" as a benefit. If Khanal et al. are right that
variance marks capability, suppressing disagreement suppresses the marker; and
penalizing low confidence trains miscalibration. Neither paper cites the other.

The precursor this entry originally asked for — an ablation separating agent
variance from user-simulator variance — **still does not exist**, and the problem has
propagated: MAS-ProVe's premise is that multi-agent systems "often exhibit high
variance in their reasoning trajectories" and its finding is that process
verification of those trajectories is itself high-variance. Verifier variance and
system variance are now entangled too.

**What an attack requires:** the agent-versus-simulator variance split, unchanged
and still unclaimed. It is a prerequisite for every method paper on this entry, and
three years of pass^k literature has not produced it.

---

## 6. Interventions move the measured quantity, not the wanted one

**Exhibited by:** Screenshots-or-Tools — a dense tool-use reward raised adoption
from 0.03 to 0.33 and carried into greedy decoding, but "held-out accuracy does not
follow. Behavior is steerable; competence is not." Auditing Self-Evolution —
SkillOpt raises benign utility 0.741 → 0.837 *and* exposure to injected content
0.820 → 0.943 and overall attack success 0.496 → 0.530, with unauthorized financial
state changes at 0.685; the agent is individually more robust per encounter
(0.605 → 0.562) and more successfully attacked overall. WER — self-authored skills
look like self-improvement and score 8-11 points below using no skill at all.
ClawTrack — outcome-only scoring cannot distinguish reliable reasoning from "lucky
passes".

This is the entry the 2026 corpus made visible. Four papers, four mechanisms, one
shape: an agent optimized against a proxy improves the proxy. The reward in the
first case is entirely benign — nobody was gaming anything — which is what makes it
a structural problem rather than a reward-design mistake.

The self-evolution case is the sharpest instance because the trap is purely one of
*which axis you look at*: a paper reporting conditional robustness would have shown
a safety improvement from the same run that shows overall attack success rising.

**What an attack requires:** almost nothing, and that is the point. **For any paper
proposing a dense agent reward, add the check: did competence follow behaviour?**
Screenshots-or-Tools is the only paper in this corpus that runs it. A survey-style
contribution re-running the held-out check across published process-reward methods
would be cheap and, on this evidence, likely to find several that do not clear it.

The related structural risk, named but unmeasured: the process signals used to
*train* long-horizon agents and those used to *evaluate* them "rest on overlapping
assumptions about what counts as progress on a partial trajectory". The test —
constructing process signals from disjoint assumptions and comparing them — is "an
experiment the corpus does not currently contain".

---

## 7. Verifier quality is the free variable nobody measures

**Exhibited by:** VPR — proves gradient bias scales as `‖ĝ − g*‖ ≤ G·ε̄` in verifier
disagreement rate ε̄, then never measures ε̄ for any oracle. Its own ablation shows a
weak oracle (N = 100 MCTS simulations) is **worse than not training at all**,
in-domain (−0.48 vs base −0.31) and out-of-domain (58.47 vs base 60.92). Universal
Verifier — best-in-class after ~3,000 lines of code and ~2,000 lines of prompts
reaches outcome κ 0.58–0.64 against human inter-annotator agreement of 0.53–0.57;
the prior bound was "no LLM-based judge exceeds 70% precision" against human
agreement of 89.3%. MAS-ProVe — across six frameworks, process verification "does
not consistently improve performance and frequently exhibits high variance".
AgentProcessBench — swapping one annotation protocol moves downstream accuracy by
−13.2 for one evaluator and +3.7 for a variant of the same model, a swing larger
than most model-to-model gaps.

Every method in entries 3, 4 and 6 depends on a verifier, and the literature has
established two things about verifiers: they are the binding constraint, and a bad
one is net-harmful. What it has not established is where any real verifier sits on
that curve.

MAS-ProVe's most consequential observation gets one clause: "a small performance gap
between LLMs acting as judges and as single agents". If a model is no better at
judging a trajectory than at producing one, process verification is an ensemble
trick.

**What an attack requires:** **measure ε̄ for the best obtainable verifier on a real
agentic task, and locate the threshold where process supervision crosses from
helpful to harmful.** Both halves already exist in this corpus — Universal Verifier
supplies a strong verifier plus human labels, VPR supplies the theory and a
demonstration of the harmful regime — and nobody has joined them. This is the
best-scoped unclaimed experiment on the page.

---

## 8. Irreversibility is motivated everywhere and encoded nowhere

**Exhibited by:** AgentProcessBench — opens on "tool execution frequently entails
irreversible side effects" as the reason step-level verification matters more for
agents than for math, then labels a formatting typo and an irreversible delete
identically as `−1`. τ-bench — terminal-state reward, so an irreversible policy
violation mid-trajectory is invisible if the final database matches. Reflexion —
the entire method assumes the episode can be reset. ReTree — "Ancestry is a conservative proxy for
semantic dependence: a descendant can contain facts that are actually independent of
the revised premise", so hard pruning discards valid state by design, with the cost
never measured. Universal Verifier — the
controllable/uncontrollable taxonomy is the closest anything comes, and it splits on
*blame*, not on *recoverability*.

The field's stated reason for caring about process over outcome is that agent
mistakes cannot be undone. No label schema, reward function, or metric in this
corpus represents that. A process reward model trained on any of them learns
*wrong*, never *unrecoverable* — which is the distinction that would let an agent
know when to stop and ask.

**What an attack requires:** the cheapest version is a reversibility flag added to
AgentProcessBench's existing 8,509 annotations — no new trajectories, no new
environment. The stronger version is a reward that weights errors by recoverability
and a benchmark that credits an agent for *declining* an irreversible action under
uncertainty. Both are unclaimed, and the second is closer to a thesis.

---

## 9. Nobody can separate the model from the harness

**Exhibited by:** The Horizon Gap — bills it among "the field's most consequential
open measurement problems", and reports that "the corpus does not yet contain the
controlled comparison that would answer it". Screenshots-or-Tools —
demonstrates the answer is not model-independent: under one identical harness on 309
tasks, the same tool availability improves a reasoning model by **+4.0pp** and
degrades a non-reasoning model by **−5.9pp**, both beyond 2 SE. ReTree — everything
is one 8B backbone, so whether a stronger policy needs the scaffold is untested.
Khanal et al. — 10 open-weight models, no proprietary frontier models, so the tier
boundary claim is about the open-weight frontier only.

The corpus shape argument cuts both ways. Execution control is the largest category
in a 1,547-paper survey (584 papers, orchestration 338 to recovery 245, and the
single-agent control loop just 1), which the survey reads as the harness carrying
the load — while conceding that "harness engineering is cheaper to iterate on than retraining a
model, so the corpus reflects research cost structure". And a finding that harnesses with more elaborate
decomposition are not uniformly better implies "harness quality itself has a
capability ceiling that a fixed model cannot be scaffolded past".

Corroboration from practice: across 39 open-source agent frameworks and 439 agentic
applications, "tools and workflows absorb over" 70% of testing effort while "the
model-driven planning component itself receives under" 5% and prompts under 1%. The
harness is where the effort goes and the model is where it is not measured.

**What an attack requires:** the controlled 2×2 nobody has run — two model tiers ×
two harness tiers, one task suite, matched budgets. Screenshots-or-Tools shows the
interaction term is significant, which means every single-model scaffold result in
this corpus is uninterpretable as a claim about scaffolds.

---

## Reading this list

Two entries are effectively closed as *problems* and open as *methods* — 2 has a
mechanism whose contribution is unattributed, 5 has a measurement whose method half
is empty. Entry 3 went from inference to measurement without becoming calibrated.
Entries 6–9 are the ones a new reader should start on, because each names an
experiment that is smaller than a paper and currently unclaimed.

Ranked by cheapness against likely value: **7** (measure ε̄, find the harmful
threshold), **6** (add the competence-followed-behaviour check), **2**'s
stratification (split ReTree's runs by whether repair fired), **8** (reversibility
flag on existing annotations).

## See Also

- [The Reason-Act Loop](reason-act-loop.md)
- [Self-Reflection and Episodic Memory](self-reflection-and-memory.md)
- [Agent Reliability and How to Measure It](agent-reliability-evaluation.md)
- [Process Supervision and Verification](process-supervision-and-verification.md)
- [Trajectory Repair and Recovery](trajectory-repair.md)
- [Benchmark Validity](benchmark-validity.md)
- [Self-Evolution and Skill Accumulation](self-evolution.md)
- [Long-Horizon, Long-Context, Long-Term Memory](long-horizon-vocabulary.md)
