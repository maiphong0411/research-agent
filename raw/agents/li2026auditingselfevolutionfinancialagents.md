> Source: Li, Zhu, arXiv preprint 2026
> URL: https://arxiv.org/abs/2608.17684
> Collected: 2026-08-24
> Published: 2026-08-18
> Bibkey: li2026auditingselfevolutionfinancialagents
> Read: abstract-only

## Problem

"Self-evolving agents turn experience into reusable skills, workflows, or memories,
but **post-evolution accuracy alone does not show whether learned behavior
preserves previously correct behavior or security**."

## Method

Audits three published self-evolution methods — **SkillOpt**, **Agent Workflow
Memory (AWM)**, and **ReasoningBank** — in simulated e-banking, using "matched
benign acquisition trajectories, sealed evaluation endpoints, execution-grounded
checks, and independent state replay."

Backbone: Qwen 3.7 Flash. Measures four things rather than accuracy alone:
regressions, "attack-surface contact", "unauthorized financial-state change", and
"artifact-executor compatibility".

## Results

**SkillOpt** — capability up, exposure up:

- benign utility **0.741 → 0.837**
- exposure to injected content **0.820 → 0.943**
- conditional attack success after exposure **0.605 → 0.562** (down)
- but overall attack success rate **0.496 → 0.530** (up)
- unauthorized financial state changes rise to **0.685**
- "Across three independently evolved lineages, capability, exposure, and
  unauthorized-state changes increase in all three, whereas ASR increases in only
  two."

**ReasoningBank** — "raises utility to **0.859** without increasing aggregate ASR,
although unauthorized state changes remain slightly above Static."

**AWM** — an evaluation artifact rather than a security finding: "a literal
WebArena text-action envelope disrupts tool execution in our native
function-calling executor. In a post-hoc sensitivity test, removing only that
envelope restores utility from **0.319 to 0.756**, while exposure rises from
**0.299 to 0.909** and ASR from **0.195 to 0.575**."

## Failure modes

Abstract-only — inferences from the abstract.

- `[observed]` **The AWM result is the most important line and it is a warning about
  everyone's numbers, including these.** A prompt-format mismatch — a WebArena
  text-action envelope meeting a function-calling executor — held utility at 0.319
  instead of 0.756. That is a 43-point swing caused by an artifact-compatibility
  bug, larger than any security effect in the paper. Two consequences: any
  published comparison of these methods across harnesses may be measuring envelope
  compatibility, and the low ASR (0.195) that AWM would have appeared to have was
  an artifact of a broken executor, not a safety property. "artifact-executor
  compatibility" belongs on every agent-evaluation checklist.

- `[observed]` **Conditional attack success falls while overall ASR rises — the
  mechanism is exposure, not vulnerability.** 0.605 → 0.562 conditional against
  0.496 → 0.530 overall means the evolved agent is individually *more* robust per
  encounter and *more* attacked overall, because it reaches more injected content
  (0.820 → 0.943). A paper reporting only conditional robustness would show a
  safety improvement. This is a clean, generalizable measurement trap.

- `[observed]` **n = 3 lineages, one backbone, one simulated domain.** "ASR
  increases in only two" of three lineages is the paper's own admission that the
  headline direction is not consistent. With one model (Qwen 3.7 Flash) and one
  simulated e-banking environment, nothing establishes whether the exposure
  mechanism is general or specific to this setup.

- `[observed]` **Simulated e-banking, so the unauthorized-state-change rate is not
  a loss estimate.** 0.685 unauthorized financial state changes is alarming as a
  rate but the abstract gives no severity distribution — a balance query and a wire
  transfer presumably both count.

- `[observed]` **Attacks are injected content, i.e. one threat model.** Whether
  self-evolution also degrades under benign distribution shift, which is the more
  common deployment failure, is not addressed.

## Relevance

The sharpest instance in this batch of a pattern the wiki should name: **capability
gains and safety regressions are measured on different axes, so a method can be
reported as an improvement while getting worse in a way its own evaluation cannot
see.** That is open problem 3 generalized beyond accuracy — the evaluation is not
merely permissive, it is aimed at the wrong quantity.

It also supplies hard evidence against the self-evolution premise from the security
side, complementing [[peng2026writeexecuterefineskill]]'s finding that
agent-authored skills score 8–11 points *below* no skill at all. Two independent
lines now say accumulated experience is not free.

The AWM envelope finding is separately worth carrying into the experiments protocol
in `CLAUDE.md`: a 43-point utility swing from a harness-format mismatch is exactly
the kind of thing an unpinned setup hides.
