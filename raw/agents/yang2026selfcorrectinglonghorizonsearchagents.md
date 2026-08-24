> Source: Yang et al. (Shanghai Jiao Tong University), arXiv preprint 2026
> URL: https://arxiv.org/abs/2608.10676
> Collected: 2026-08-24
> Published: 2026-08-11
> Bibkey: yang2026selfcorrectinglonghorizonsearchagents
> Read: full

## Problem

Two hazards that interact. Context: "retaining the complete trajectory makes the
per-step reasoning context grow with the search horizon." Contamination: "an
erroneous premise can steer both what the agent retrieves next and how it
interprets subsequent evidence, creating an error cascade."

The specific gap this paper names, and the reason it matters for
`wiki/agents/open-problems.md` entry 2: "Existing compression methods reduce
context at the cost of important details and often **replace erroneous facts
without repairing downstream reasoning derived from them**." Even a correct fix
leaves the conclusions built on the old value standing.

## Method

**ReTree**: memory is `M_t = (T_t, n_t)`, an external rooted tree plus active
node. Each node `n = (s_n, E_n, H_n, p_n)` holds a bounded task-state summary,
evidence introduced locally at `n`, a revision history, and a parent pointer.
Evidence available at `n` is the union along the root path, `A(n) = ∪_{v ∈
path(r,n)} E_v`. Edges mean derivation, not alternatives: "a child is a search
state derived from its ancestor's evidence" — explicitly *not* Tree-of-Thoughts.

Per-step context: `C_k(M_t, q) = s_{n_t} ‖ TopK_k(A(n_t), q ‖ s_{n_t})` with
`k = 5` and "retrieval uses lexical relevance in the current implementation". The
summary is "at most 140 words" and records "the requested answer slot, resolved
intermediate slots, remaining open slots, and unresolved candidates".

Expansion: up to five passages per search; the extractor "emits at most six
question-relevant atomic facts" and binds each to a source **by passage index** —
"Binding by index avoids asking the language model to reproduce a URL, which can
silently make an otherwise correct citation unverifiable."

Backtracking is two-gated. A first call sees question + top-k existing facts + new
facts but *not* the branch summary, and may propose a conflict "only when a new
fact gives an incompatible value for the same entity and attribute under the same
scope and time". A second call sees the branch summary and the target's change
history and "applies the repair only when the contradiction is same-scope and
better supported, thereby reducing oscillation between previously rejected
values." On confirmation: replace evidence and source at the introducing node
`ι(j)`, append to `H_{ι(j)}`, regenerate `s_{ι(j)}` "solely from corrected
accumulated evidence", **remove all descendants of `ι(j)`**, and set
`n_t = ι(j)`. This is "dependency-directed revision from truth-maintenance
systems [Doyle, 1979]".

Formal requirement: with `Dep_{t−1}(j)` the components derived from `e_j`,
`I_t` those invalidated, and `G_t(e′_j)` those regenerated,
`Dep_{t−1}(j) ⊆ I_t ∪ G_t(e′_j)`.

Setup: Qwen3-8B backbone for every arm, same Google Search API, identical question
ordering, at most **eight searches per question**, at least one retrieval before
answering. FP16 via SGLang on two NVIDIA A40 (48GB). Judge is GPT-5. **"All runs
use seed 0 with fixed hyperparameters across all benchmarks."**

Baselines: **Full-Trajectory ReAct** (complete uncompressed transcript);
**FlatUpdate** (Mem0-style flat record list — shares ReTree's 140-word summary,
top-5 budget, *and conflict detector*, but "replaces the refuted fact without
locating its introducing state, rebuilding dependent summaries, or pruning
downstream reasoning"); **ReportMemory** (ReSum/IterResearch-style single evolving
report capped at 200 words plus an unordered URL bag).

## Results

Judge accuracy / EM (%), and average max per-step policy context in characters:

| Dataset | n | ReTree | FlatUpdate | ReportMem. | Full ReAct | ctx ReTree | ctx Full ReAct |
|---|---|---|---|---|---|---|---|
| Bamboogle | 125 | **61.6**/47.2 | 58.4/**48.0** | 54.4/37.6 | 36.0/28.0 | 1,116 | 1,474 |
| 2Wiki | 600 | 50.5/**31.3** | 45.8/25.8 | **50.8**/25.8 | 36.5/24.8 | 1,068 | 1,521 |
| HotpotQA | 600 | **50.5**/32.3 | 48.3/**32.5** | 48.8/27.3 | 42.2/29.3 | 1,211 | 1,542 |
| FRAMES | 824 | **31.8**/**19.5** | 27.9/16.7 | 26.0/13.0 | 15.8/10.1 | 1,274 | 1,920 |
| Overall | 2,149 | **44.0**/**28.0** | 40.4/25.5 | 40.9/22.0 | 30.1/20.6 | 1,190 | 1,677 |

- Over Full-Trajectory ReAct: "**8.3–25.6** points" per dataset; pooled
  "**13.9 pp** in judge accuracy and **7.4 pp** in EM".
- Over FlatUpdate: "**2.2–4.7 pp** on every dataset" (judge accuracy).
- Over ReportMemory: "**1.7–7.2 pp**" on Bamboogle, HotpotQA, FRAMES, "while
  remaining within **0.3 pp** on 2Wiki"; **3.0 pp** overall.
- Peak context: "Full-Trajectory ReAct requires **1.27–1.51×** as much peak
  context as ReTree." ReportMemory is smallest at **699–817 characters**.
- Full ReAct growth: "surpassing **2.8K** characters after two retrievals on 2Wiki
  and HotpotQA, and surpassing **5.6K** after four retrievals on FRAMES."
- **"natural backtracking is triggered in 9.6–17.5% of ReTree runs"**.
- Overhead: "ReTree uses **7–11% more model calls and 10–13% more total tokens**
  than FlatUpdate."
- Claim-level attribution, fixed 600-question FRAMES subset, NLI passage
  entailment:

| System | CitePrec ↑ | CiteRec ↑ | CiteF1 ↑ | Uncited ↓ |
|---|---|---|---|---|
| ReTree | **44.5** | **41.3** | **42.8** | 14.8 |
| ReportMem. | 16.8 | 21.4 | 18.8 | **5.9** |
| Full ReAct | 37.7 | 27.1 | 31.5 | 33.1 |

## Failure modes

- `[observed]` **The mechanism fires on at most one run in six, yet is credited
  with the whole gap over FlatUpdate.** Backtracking triggers in "9.6–17.5% of
  ReTree runs", and FlatUpdate shares ReTree's summary budget, evidence budget,
  *and conflict detector*. On the ≥82.5% of runs where no backtrack occurs, the two
  systems should behave near-identically, so the 2.2–4.7 pp gap must be
  concentrated in the minority that backtracked — requiring the repair to flip
  roughly a fifth to a third of those runs. That is possible and would be a strong
  result, but the paper never reports accuracy conditioned on whether a backtrack
  fired. Without that split, the gap is equally consistent with single-seed noise
  plus unreported differences in how the two memories render context. **This is
  the one experiment that would settle whether dependency-directed revision does
  anything, and it is a stratification of data already collected.**

- `[observed]` **Citation precision of 44.5% means most citations do not support
  their claim — on the metric the architecture exists to serve.** Traceability is
  requirement 2 of the paper's own formulation, passage-index binding is a
  contribution, and the result is that 55.5% of cited passages fail to entail their
  claim. ReportMemory, which "discard[s] explicit fact-level dependency lineage",
  nonetheless has a far lower Uncited rate (5.9% vs 14.8%) — so ReTree omits
  citations more often *and* is wrong more than half the time when it does cite.
  The attribution chain `c_i → j → (x_j, u_j) → Passage(u_j)` has two hops and the
  paper localizes the failure to neither: it could be the extractor writing atomic
  facts the passage does not support, or the final generator mis-assigning
  identifiers. Measuring entailment of `x_j` against `Passage(u_j)` separately from
  `c_i` against `x_j` splits it, and needs no new runs.

- `[observed]` **The motivating problem never binds at the scale tested.** Peak
  per-step context for Full-Trajectory ReAct is **1,920 characters** at worst
  (FRAMES) against an 8-search cap, and Figure 3's x-axis reaches 7 completed
  retrieval steps. Roughly 500 tokens is nowhere near Qwen3-8B's window, so
  "unbounded context growth" cannot be what causes Full ReAct's 15.8% on FRAMES.
  Whatever ReTree fixes, it is not a context-limit effect — which makes the framing
  ("long-horizon", "unbounded growth") oversold and leaves the actual mechanism
  (noise reduction? forced slot-tracking in the 140-word summary?) unidentified.
  A run with the search cap raised to 30+ is the test that would make the horizon
  claim real.

- `[observed]` **Single seed, no confidence intervals on any accuracy number.**
  "All runs use seed 0". The 2.2 pp HotpotQA gap over FlatUpdate is on a
  600-question subset with one run per arm; Figure 3 reports 95% CIs for *context
  size* but nothing does for accuracy. Given a live-search environment and an
  LLM-based judge, per-arm variance is plausibly larger than the FlatUpdate gap.

- `[observed]` **The "every dataset" claim holds only for the model-judged
  metric.** On EM, FlatUpdate beats ReTree on Bamboogle (48.0 vs 47.2) and
  HotpotQA (32.5 vs 32.3), and Full ReAct beats it on nothing but comes within
  3.0 EM on HotpotQA. The conclusion states "ReTree also improves accuracy over
  FlatUpdate on every dataset" — true of GPT-5 judge accuracy, false of exact
  match. The metric requiring a frontier model's agreement is the one that favors
  the proposed method, on 2 of 4 datasets, and no judge-agreement or judge-bias
  check is reported.

- `[observed]` **Live web search makes arms non-comparable and the study
  unreproducible.** Arms share "the same Google Search API backend, and identical
  question ordering" but necessarily not the same moment; the paper omits
  wall-clock "due to live-search network variance" and FRAMES is a
  realistic-fact-seeking set where the index moves. With one seed per arm, index
  drift between runs is indistinguishable from method effect, and nobody can rerun
  these numbers.

- `[stated]` **Hard pruning is known to over-invalidate and the cost is never
  quantified.** "Ancestry is a conservative proxy for semantic dependence: a
  descendant can contain facts that are actually independent of the revised
  premise. Hard pruning may therefore over-invalidate useful state." No count of
  discarded-but-valid facts, no ablation on pruning depth, and no comparison
  against the "finer-grained dependency graphs" the limitations section proposes.
  The trade-off is asserted as appropriate rather than measured.

- `[stated]` **The conflict judge is named as the binding constraint and is never
  evaluated.** "correction quality is limited by the conflict judge. A false
  negative preserves contamination, whereas a false positive can over-prune useful
  evidence." Two extra LLM calls (propose, then confirm) decide every repair, and
  no precision or recall for either is reported. The two-gate design and the
  same-entity/attribute/scope/time rule are hand-specified constraints with no
  ablation, so it is unknown whether the second gate does anything.

- `[observed]` **Whether the relevant fact reaches the policy is decided by word
  overlap.** `TopK_k` uses "lexical relevance in the current implementation" with
  `k = 5`, while `A(n)` can accumulate roughly 48 facts (8 searches × up to 6
  facts). A fact that is semantically decisive but lexically distant from the
  question is invisible to the policy no matter how well the tree preserved it —
  which undercuts the claim that the tree "retains the full active evidence path"
  in any operative sense. Swapping to a dense retriever is listed as future work
  and would separate the tree's contribution from the retriever's.

- `[observed]` **The efficiency claim is on peak per-step context, a metric that
  rewards making more calls.** §5.2 lists "total model calls, and token usage" as
  metrics, but the only totals reported are the FlatUpdate deltas (7–11% more
  calls, 10–13% more tokens). No total-token comparison against Full-Trajectory
  ReAct appears anywhere, so "1.27–1.51×" describes the largest single prompt, not
  the cost of answering a question. A method that re-prompts after every repair can
  win on peak while losing on total.

- `[observed]` **One 8B backbone.** Every arm is Qwen3-8B, and FRAMES tops out at
  31.8%. Whether a stronger policy still needs an external revision tree — or
  whether the scaffold's gains shrink as the model gets better at ignoring stale
  context — is untested, and it is the question that decides whether this is a
  contribution or a small-model crutch.

## Relevance

The most direct attack so far on open problem 2 in
`wiki/agents/open-problems.md` — "Nothing recovers within a trajectory". This is
the mid-trajectory repair mechanism that entry asks for: it backtracks to the
decision point where a claim entered, invalidates what depended on it, and resumes
from the repaired state, rather than restarting the episode (Reflexion) or burning
the step budget in place (ReAct). Doyle's truth-maintenance framing is the right
ancestor and is currently absent from the wiki.

Two caveats that keep it a lead rather than a solution. The repair fires on
9.6–17.5% of runs and the paper never isolates its effect, so the entry should
record the *mechanism* as prior art and the *evidence* as unresolved. And the
horizon is eight searches with peak contexts under 2K characters, so this is not
yet a long-horizon result — which is exactly the regime
[[khanal2026pass1reliabilityscienceframework]] shows matters, and where that paper
found memory scaffolds universally *hurt*. Those two findings are in tension and
belong in a Disputed block.
