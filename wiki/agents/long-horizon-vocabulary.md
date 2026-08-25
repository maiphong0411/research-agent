# Long-Horizon, Long-Context, Long-Term Memory: Three Different Things

> Sources: Chen et al., 2026-08-07
> Raw: [The Horizon Gap](../../raw/agents/chen2026horizongapplanningmemory.md)
> Updated: 2026-08-24

## Overview

A survey of 1,547 arXiv papers opens by fixing vocabulary, and the disambiguation
is worth more to this wiki than most of the methods it catalogues. Three
properties the field uses interchangeably are logically independent:

- **long-context** — a property of the **model** / serving stack: how many tokens
  one forward pass can attend to.
- **long-horizon** — a property of the **task**: how many sequential decisions it
  requires, regardless of whether the trace fits in a context window.
- **long-term memory** — a property of the **system**: whether information
  available at step `t` is still available at `t + k`.

The consequence is stated bluntly: "a harness can carry a long-horizon task
through a short context via aggressive summarization, and a system can have a huge
context window and no persistent memory at all". And why it matters: "imprecision
here is not merely stylistic: it is the reason a 'memory' paper and a
'long-context' paper are so often cited as if they addressed the same problem when
they do not."

Two further splits are load-bearing for reading anything in this topic:

- **agent** (the policy — model plus whatever turns its output into actions) vs
  **harness** / scaffold (control loop, tool sandbox, memory layer, retry logic,
  sub-agent orchestration).
- **episode** (one complete attempt at a task) vs **session** (a continuous
  interactive period bounded by the interface, not the task). A session may hold
  many episodes; an episode may span sessions. In the memory literature
  "long-term" sometimes means beyond-episode and sometimes beyond-session.

## The horizon gap

The survey's framing concept is "the distance between what a model can do in one
step and what a system built around it can reliably finish over many". Frontier
models solve single-pass problems that were recent research contributions, and the
same models "fail in ways no single-step benchmark reveals: losing track of an
earlier decision, declaring a half-finished job done, or quietly drifting from the
goal they were given."

This is the same phenomenon [pass^k](agent-reliability-evaluation.md) measures,
named from the capability side rather than the metric side.

## Where the horizon is carried decides the failure mode

The survey's most directly reusable contribution is a second axis — *where the
extra horizon lives* — with a distinct failure mode per position:

| Locus | The task fits… | How it fails |
|---|---|---|
| within-context | inside one forward pass | attention / utilization degradation |
| within-task-beyond-context | one episode, harness carries state | "information loss at the harness boundary" |
| cross-task-persistent | across episodes and sessions | "interference or staleness in what was retained" |

This is a better spine than treating "memory" as one bucket. A summarization
scheme and a persistent skill library are both called memory and fail for
unrelated reasons.

## What the corpus's shape suggests, and why to distrust it

Category counts, from 1,547 papers spanning 2024-01 to 2026-07:

| Category | Papers | Notable split |
|---|---|---|
| Execution control & recovery | 584 | orchestration 338 · recovery 245 · loop 1 |
| Memory & context | 397 | external 294 · context 103 |
| Planning & decomposition | 182 | decompose 162 |
| Training for long horizons | 167 | rl 130 · supervision 37 |
| Evaluation & measurement | 114 | benchmark 114 |
| Foundations, limits & safety | 103 | 93 of them from a targeted supplement |

Execution dominates, and the survey reads this as evidence that the harness rather
than the model is the binding constraint. Treat that inference carefully: the
corpus came from eight relevance-sorted arXiv threads each capped at 250 results,
and three of the eight feed execution-adjacent topics while one feeds evaluation.
The counts partly measure how the queries were allocated.

The `loop = 1` cell is the clearest case. The survey reads a single paper on the
inner control loop as ReAct's absorption into "how agents just work"; the simpler
explanation is that the harvest filter's terms do not select for papers about an
agent's own loop. A subcategory of one cannot support a claim either way.

Also worth knowing before citing any figure from this survey: it is
single-annotator (the author), arXiv-only, has no venue or quality gate, and
explicitly drops citation counts. Category volume measures posting activity. And
it is blind where its own thesis is strongest — it "under-represents unpublished
industrial agent engineering that never reaches arXiv", which is exactly where
harness engineering ships.

## The two open measurement problems it names

1. **Harness vs. model attribution.** How much long-horizon capability is the
   model's and how much is the scaffold's? "the corpus does not yet contain the
   controlled comparison that would answer it." Sharpened by a finding that
   harnesses with more elaborate decomposition are not uniformly better, so
   "harness quality itself has a capability ceiling that a fixed model cannot be
   scaffolded past."
2. **Correlated measurement bias.** The process signals used to *train*
   long-horizon agents and those used to *evaluate* them "rest on overlapping
   assumptions about what counts as progress on a partial trajectory". The test —
   "deliberately constructing process signals from disjoint assumptions and
   comparing them" — is "an experiment the corpus does not currently contain".

The survey is careful that these are unequally supported: of the second it says
"nothing in the corpus demonstrates this bias in a specific benchmark-training
pair". The abstract bills both as the field's most consequential open problems
anyway.

## Degradation is bimodal, not smooth

The textbook model — per-step error `ϵ`, independent compounding, exponential
decay in steps — does not survive contact with the data. The survey's synthesis:
"independent per-step error compounding is a useful null model, not an empirically
confirmed law, but the alternative it points toward is not gentler degradation" —
it is instead "bimodal outcomes" that are "(fine, or catastrophically derailed)
whose trigger the field cannot yet reliably predict".

Vending-Bench, on runs exceeding 20M tokens, finds "capable models turn a profit in
most runs, but every model has some runs that derail into a 'meltdown' loop from
which they rarely recover" — and critically, "derailment shows no clear
correlation with the context window filling up". Whatever causes long-horizon
collapse, running out of context is not it.

This matters for design: step budgets, context-compaction schemes, and
summarization thresholds are usually justified by an exponential-decay mental model
that the measurements do not support. See
[Trajectory Repair and Recovery](trajectory-repair.md).

## Caveat on every number above

This is a survey, so all of its empirical figures are secondary citations. The raw
note carries an explicit provenance warning: nothing sourced from it should reach a
paper without reading the primary source first.

## See Also

- [Agent Reliability and How to Measure It](agent-reliability-evaluation.md)
- [Process Supervision and Verification](process-supervision-and-verification.md)
- [Trajectory Repair and Recovery](trajectory-repair.md)
- [Benchmark Validity](benchmark-validity.md)
- [Open Problems in Agentic Systems](open-problems.md)
