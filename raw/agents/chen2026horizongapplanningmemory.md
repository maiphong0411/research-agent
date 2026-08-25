> Source: Chen, Wang, Qu (DeepGrounding / AlphaAvatar), arXiv preprint 2026 — survey
> URL: https://arxiv.org/abs/2608.06663
> Collected: 2026-08-24
> Published: 2026-08-07
> Bibkey: chen2026horizongapplanningmemory
> Read: full
>
> NOTE ON PROVENANCE: this is a survey, so every empirical number below is a
> secondary citation — verbatim from *this paper*, not from the primary source.
> Any figure here must be re-checked against its original paper before it is used
> in a claim, a wiki article, or a `\cite`.

## Problem

"Frontier language models solve, in a single forward pass, reasoning problems
that would have been research contributions a few years ago — yet the same models,
embedded in an agent loop and asked to complete a task spanning hours rather than
seconds, fail in ways no single-step benchmark reveals: losing track of an earlier
decision, declaring a half-finished job done, or quietly drifting from the goal
they were given."

The **horizon gap**: "the distance between what a model can do in one step and
what a system built around it can reliably finish over many".

The most useful contribution for this repo is a disambiguation the field
routinely botches — three *logically independent* axes:

- **long-context** — property of the model/serving stack: tokens per forward pass.
- **long-horizon** — property of the **task**: sequential decisions required.
- **long-term memory** — property of the **system**: whether info at step `t`
  survives to `t + k`.

"a harness can carry a long-horizon task through a short context via aggressive
summarization, and a system can have a huge context window and no persistent
memory at all… imprecision here is not merely stylistic: it is the reason a
'memory' paper and a 'long-context' paper are so often cited as if they addressed
the same problem when they do not."

Also fixes **agent** (the policy) vs **harness**/scaffold (control loop, sandbox,
memory layer, retry logic, sub-agent orchestration), **episode** vs **session**,
**coherence**, and **autonomy time**.

## Method

Corpus: arXiv API across **eight threads** (long-horizon agents; planning &
decomposition; memory & context; agentic RL & credit assignment; benchmarks &
evaluation; multi-agent orchestration & scaffolding; error accumulation &
reliability; self-correction & recovery), restricted to cs.AI/CL/LG/SE/MA/HC +
stat.ML, window 2024-01 to 2026-07, "Each thread was capped at 250 results (a
disclosed depth limit) and sorted by relevance."

Pipeline: 2,000 raw hits → 1,939 unique after dedup (61 duplicates) →
harvest-time topic-signal filter drops **176 (9.1%)** → 1,763 seed candidates →
"TF-IDF + truncated-SVD + k-means clustering (k = 18)" used "purely as scaffolding
for taxonomy design", then reclassification with "an explicit LLM/agent-signal
gate" drops **344 further (19.5%)** → **1,419 seed**. Combined bleed: "**520** of
the 1,939 raw unique hits (**26.8%**) were judged off-topic".

Then a targeted supplement, because "foundations … held only 10 papers": 19
queries → 321 candidates → a stricter filter drops **193 (60.1%)** → **128
supplement** papers. Total **1,547**.

Two axes. **Axis 1** (category): planning, memory, execution, training,
evaluation, foundations. **Axis 2** (where the horizon is carried): within-context,
within-task-beyond-context, cross-task-persistent — with distinct failure modes
per column: "within-context methods fail by attention/utilization degradation …
within-task-beyond-context methods fail by information loss at the harness
boundary; and cross-task-persistent methods fail by interference or staleness in
what was retained."

Explicit language calibration: "we avoid unmeasured strong language — 'proves,'
'monotone,' 'law,' 'first' — in favor of 'observed,' 'measured and reported,' or
'tracks'".

## Results

Corpus composition (1,547 papers):

| Category | Subcategory tags (n) | Papers | Suppl. | % 2026 |
|---|---|---|---|---|
| Planning & decomposition | decompose 162 · worldmodel 11 · search 9 | 182 | 0 | 27% |
| Memory & context | external 294 · context 103 | 397 | 21 | 72% |
| Execution control & recovery | orchestration 338 · recovery 245 · **loop 1** | **584** | 0 | 45% |
| Training for long horizons | rl 130 · supervision 37 | 167 | 14 | 62% |
| Evaluation & measurement | benchmark 114 | 114 | 0 | 58% |
| Foundations, limits & safety | not subdivided | 103 | **93** | 77% |

- "Seventeen of the eighteen cells are populated: only the
  foundations/within-context cell is empty".
- Title-level multi-category overlap: "**13.8%** of the corpus (**213** papers)
  trips two or more"; commonest are memory+evaluation (29), memory+execution (23),
  training+execution (22).
- Growth: execution is "consistently the plurality leader, fluctuating roughly
  **41-54%** quarter to quarter" through 2024-2025, with memory's share matching
  or exceeding it "from 2026 Q1 onward"; planning's share drifts down.
- OpenAlex metadata needed an arXiv fallback for "**180** rows (**11.6%**)".
  Residual misclassification "on the order of one in twenty", estimated from "A
  random sample of 30 kept papers and 55 excluded papers".

Benchmark-validity findings (all secondary citations):

- SWE-bench+ manual inspection of successful patches: "**32.67%** involve solution
  leakage (the fix was already present in the issue report or comments) and a
  further **31.08%** pass only because the test suite is too weak to verify
  correctness — filtering both out drops one leaderboard-topping system's
  resolution rate from **12.47% to 3.97%**".
- Independent corroboration: "passing patches diverge behaviorally from the
  human-written ground truth in nearly **30%** of cases even when tests pass".
- τ-bench "counts empty responses as successes"; across agentic benchmarks,
  "task-setup and reward-design flaws … can over- or under-estimate reported
  performance by up to **100%** in relative terms, and a resulting checklist
  reduced measured overestimation on one complex benchmark by **33%**".
- AndroidControl-Curated: "top-scoring GUI agents plateau around **60%** …
  because benchmark noise — ambiguities and factual errors in the benchmark itself
  — caps the achievable score".
- TRAJEVAL "coherence collapse": "even where capable models localize the right
  code, they still fail after reaching it … meaning Pass@1 alone actively
  misdiagnoses why the remaining **30–35%** of issues go unsolved"; the diagnostic
  "decomposed **16,758** stored trajectories into aligned stages".
- Human-time reporting: "of the roughly fifteen well-known agentic benchmarks we
  checked against their own papers, only GAIA reports a clean, level-by-level
  human-time-to-complete statistic… SWE-bench itself, WebArena, and OSWorld —
  three of the most widely used agentic benchmarks in this literature — report **no
  human-time baseline at all** in their own papers."

Degradation and recovery findings (secondary):

- Vending-Bench, "runs exceeding **20M** tokens", finds "high variance rather
  than smooth decay: capable models turn a profit in most runs, but every model
  has some runs that derail into a 'meltdown' loop from which they rarely recover;
  notably, **derailment shows no clear correlation with the context window filling
  up**".
- Survey's synthesis: "independent per-step error compounding is a useful null
  model, not an empirically confirmed law, but the alternative it points toward is
  not gentler degradation — it is **bimodal outcomes** (fine, or catastrophically
  derailed) whose trigger the field cannot yet reliably predict."
- **Accuracy-correction paradox**: "the weaker model in a three-model comparison
  (GPT-3.5, **66%** base accuracy) corrects its own errors intrinsically at a
  higher rate (**26.8%**) than the strongest model (**94%** base accuracy,
  **16.7%**), and error-detection rate does not predict correction success
  either." Proposed **Error Depth Hypothesis**: "stronger models make fewer but
  structurally deeper errors that intrinsic self-correction is specifically bad at
  reaching, which would mean [intrinsic self-correction failure] is not a
  capability gap current models simply haven't crossed yet, but a pattern that
  could get worse, not better, as models improve".
- Testing practice across "**39** open-source agent frameworks and **439** agentic
  applications": "tools and workflows absorb over **70%** of testing effort — while
  the model-driven planning component itself receives under **5%** and prompts
  under **1%**".
- "Governance Decay": "context compaction … can silently erase the safety
  constraints an agent was given at the start of a long trajectory, precisely
  because a compression policy optimized for task-relevant information has no
  reason to preserve constraints that never come up again until they are
  violated".
- "Phantom transfer": fine-tuning on synthetic agentic trajectories containing
  adversarial actions "measurably increases misaligned behavior, and … this
  increase **survives removing every adversarial action** from the training
  trajectories before fine-tuning".
- Tiered Agentic Oversight: lower tiers absorb "up to **24%** of individual agent
  errors". Ensemble Monitoring: "a diverse three-monitor ensemble beats a
  homogeneous one built from three copies of the same monitor by **2.4x**, even at
  equal compute".
- PRM800K required "**800,000** step-level human feedback labels" — "dense
  supervision demonstrably helps, at an annotation cost no agentic setting can pay
  per task."
- GRPO "is shown to implicitly perform process-reward-like credit attribution as a
  side effect of its group-relative normalization, suggesting the boundary between
  'outcome' and 'process' supervision is less an architectural choice than a
  question of where in a training pipeline step-level credit ends up being
  computed."
- One study finds "full-horizon planning with on-demand replanning matches
  step-by-step accuracy across the depths, breadths, and robustness levels tested
  — at **2-3x fewer tokens**", against the interleaved default.

## Failure modes

Both kinds are listed: weaknesses of the survey as evidence, and the field-level
weaknesses it documents (the latter marked *field*).

- `[stated]` **Single annotator, who is the author.** "Both stages, and the
  classification step between them, were carried out by a single annotator (the
  author)". No inter-annotator agreement exists for any label, and the residual
  error estimate ("on the order of one in twenty") comes from re-checking 30 kept
  and 55 excluded papers — n = 85 against a corpus of 1,547, checked by the same
  person who assigned the labels.

- `[observed]` **The corpus counts are the survey's main quantitative evidence and
  they are largely artifacts of the query design.** Eight threads, each hard-capped
  at 250 and relevance-sorted, sets a per-thread quota before any paper is read.
  Three of the eight threads feed execution-adjacent topics (orchestration &
  scaffolding; error accumulation & reliability; self-correction & recovery) and
  one feeds evaluation — and execution comes out largest at 584 while evaluation is
  114. The survey's headline attribution argument rests partly on "§5's
  orchestration-to-recovery ratio" being 1.4:1, a ratio between two subcategories
  fed by different query strings. The survey names one confound ("harness
  engineering is cheaper to iterate on than retraining a model, so the corpus
  reflects research cost structure") but not the query-allocation one, which is
  larger and mechanical.

- `[observed]` **`loop = 1` is a filter artifact presented as a field finding.**
  The execution category splits 338 / 245 / **1**, and the survey reads the single
  loop paper as ReAct's "near-total absorption into 'how agents just work'". The
  simpler explanation is that the harvest-time filter's topic-signal terms
  (long-horizon, multi-step, trajector-, planning, memory, orchestrat-, scaffold-,
  replan-, reflection, credit assignment) do not select for papers about an agent's
  inner control loop. A subcategory with n = 1 cannot support prose either way, and
  the survey builds a paragraph on it.

- `[observed]` **Single-label assignment, with the overlap statistic deliberately
  measured only on titles.** 13.8% of papers trip ≥2 category signals from the
  *title alone*; the survey declines to extend the count to abstracts because "we
  evaluate" fires the evaluation signal "in nearly every machine-learning abstract",
  making the number "uninformative rather than merely noisy". That is a sound
  reason not to report it and also an admission that the true multi-topic fraction
  is unmeasured. Every per-category count — and therefore every
  shape-of-the-field hypothesis in §9 — is computed on labels the survey itself
  calls "the primary contribution … not an exclusive membership claim".

- `[observed]` **The most hedged section rests on the noisiest harvest.**
  Foundations is 103 papers of which **93 are supplement**, gathered by 19 queries
  that discarded 60.1% of their hits — a bleed rate six times the seed harvest's —
  and the supplement is "recency-biased by construction". So "no general,
  empirically validated theory of long-horizon degradation currently unifies this
  section's findings" is a conclusion about a sub-corpus assembled with the least
  reliable instrument in the paper, and the 77%-posted-in-2026 figure for that
  category is not interpretable as a trend.

- `[observed]` **No quality gate anywhere in the corpus.** arXiv-only,
  relevance-sorted, no venue filter, and citation counts explicitly dropped
  ("citation counts would be near zero for the majority of entries and are not a
  meaningful signal here"). Category volume therefore measures *posting activity*,
  and §9's hypotheses about "where the field is actually spending its effort"
  infer research effort from preprint volume with no weighting for review, and no
  way to distinguish a field's centre of gravity from a burst of near-duplicate
  papers on a fashionable topic.

- `[observed]` **The abstract promotes a hypothesis the discussion demotes.** Both
  "harness vs. model" and "correlated measurement bias" are billed in the abstract
  as "the field's most consequential open measurement problems". §9 then says of
  the second: "nothing in the corpus demonstrates this bias in a specific
  benchmark-training pair", "We flag this as a structural-analogy hypothesis rather
  than a finding", and "it carries less evidentiary weight than the
  harness-versus-model question". The paper is unusually honest about this; a
  reader who stops at the abstract gets the wrong impression anyway.

- `[stated]` **Systematically blind to the literature its own thesis says matters
  most.** "It under-represents unpublished industrial agent engineering that never
  reaches arXiv, non-English-language work, and any system described only in a blog
  post or technical report rather than a paper." The survey's central claim is that
  the *harness* — orchestration, recovery, context management — is where
  long-horizon capability lives. Harness engineering is exactly the thing that
  ships as a product or a blog post rather than a paper, so the corpus is weakest
  precisely where the argument is strongest.

- `[observed]` **A survey cannot verify what it repeats, and this one is
  number-dense.** The SWE-bench+ figures, the "up to 100% in relative terms" claim,
  the accuracy-correction paradox rates, and the Vending-Bench meltdown finding all
  arrive at one remove. Under this repo's rule that `raw/` numbers are verbatim
  from the source actually read, they are verbatim from *this survey* — which is
  why the header carries an explicit provenance warning. Anything from this note
  that reaches `wiki/` or a `.tex` file needs the primary paper read first.

- `[observed]` *field* **The training signal and the evaluation signal are being
  built from the same intuitions.** "the tools used to validate whether
  long-horizon training works (§7's process-aware benchmarks) and the tools used to
  build long-horizon training in the first place (§6's process reward models) rest
  on overlapping assumptions about what counts as progress on a partial
  trajectory." The proposed test — "deliberately constructing process signals from
  disjoint assumptions and comparing them" — is "an experiment the corpus does not
  currently contain". This is a concrete, well-scoped, unclaimed experiment.

- `[observed]` *field* **Nobody has separated the model's long-horizon competence
  from the harness compensating for its absence.** "the corpus does not yet contain
  the controlled comparison that would answer it", and the question "bears directly
  on whether long-horizon capability should be pursued by training better models or
  building better harnesses". Sharpened by §3's finding that "harnesses with more
  elaborate decomposition are not uniformly better", so "harness quality itself has
  a capability ceiling that a fixed model cannot be scaffolded past."

- `[observed]` *field* **Self-correction may get worse as models improve.** The
  Error Depth Hypothesis, if it holds, inverts the usual assumption that intrinsic
  self-correction is a capability that scaling will fix: the 94%-accuracy model
  self-corrects at 16.7% against the 66%-accuracy model's 26.8%. n = 3 models, so
  this is a lead rather than a result — but it is a lead nobody in the corpus has
  tested at scale, and it predicts a specific measurable trend across model
  generations.

- `[observed]` *field* **Degradation is bimodal, not smooth, and the trigger is
  unknown.** Vending-Bench's meltdowns show "no clear correlation with the context
  window filling up", and Strained Coherence finds a pre-failure signal, so "the
  error process is not memoryless the way the simple model assumes". Everything
  built on an exponential-decay mental model of long-horizon failure — including
  step-budget choices and context-management designs — is fitted to a curve the
  data does not support.

- `[observed]` *field* **The least deterministic part of every agent system is the
  least tested part.** Across 39 frameworks and 439 applications: >70% of testing
  effort on tools and workflows, <5% on the model-driven planning component, <1% on
  prompts.

## Relevance

Best available field-level frame for `wiki/agents/`, and it validates the existing
open-problems file from the outside: the survey's own cross-cutting synthesis is
that "outcome-only signals — a single reward, a single pass/fail check — grow
uninformative as horizon grows", which is entry 3 restated as the organizing
observation of a 1,547-paper corpus. Entry 2 ("Nothing recovers within a
trajectory") is corroborated structurally — recovery is 245 papers against
orchestration's 338, and the survey's own assessment is that the field "has
invested far more engineering effort in scaling out … than in hardening any one
agent's own error-correction — even though the self-correction evidence above
suggests hardening is where the harder unsolved problem sits."

Three things to import into the wiki that are not there yet:

1. **The long-horizon / long-context / long-term-memory disambiguation.** Cheap to
   adopt, and it immediately separates papers the current wiki would treat as
   addressing the same problem. Same for agent-vs-harness and episode-vs-session.
2. **The Axis-2 failure-mode split** — within-context fails by attention
   degradation, beyond-context fails at the harness boundary, cross-task fails by
   interference or staleness. This is a better organizing spine for an
   open-problems entry than "memory" as one bucket.
3. **Two named unclaimed experiments**: the disjoint-process-signal comparison for
   correlated measurement bias, and the controlled harness-vs-model attribution.
   Both are measurement problems, both are stated as absent from a 1,547-paper
   corpus, and both are the right size for a thesis.

Also resolves a tension in the reading so far: this survey's account of bimodal,
trigger-unknown derailment is what
[[khanal2026pass1reliabilityscienceframework]]'s "MOP paradox" is measuring, and
Vending-Bench's finding that derailment does *not* track context filling up cuts
against the premise of
[[yang2026selfcorrectinglonghorizonsearchagents]]'s context-bounding motivation.
