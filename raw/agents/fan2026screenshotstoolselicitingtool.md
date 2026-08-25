> Source: Fan et al. (UESTC / RedAI), arXiv preprint 2026
> URL: https://arxiv.org/abs/2608.03327
> Collected: 2026-08-24
> Published: 2026-08-04
> Bibkey: fan2026screenshotstoolselicitingtool
> Read: abstract-only

## Problem

"Hybrid computer-use agents can act through screenshots or call text tools. We find
that **having a tool available does not settle which way the effect goes.**"

## Method

One fixed harness, one benchmark, ablate the model and the observation rule.
"Under one identical GUI-MCP harness on the OSWorld-MCP benchmark (**309** tasks)".
Then multi-turn RL probes at two levels: an action-level dense tool bonus, and a
context-level rule that drops the screenshot following a successful tool call and
halves image history.

## Results

- "the same MCP tools improve a reasoning model by **+4.0pp** and degrade a
  non-reasoning model by **−5.9pp** (**5 runs each, both beyond 2 SE**)".
- Failure taxonomy: "The non-reasoning policy ignores, misnames, or falsely
  terminates around tools."
- **Adoption gap**: the reasoning model "still calls a tool on only **55/309**
  tasks, **23.9%** of the tool-reachable ones".
- Diagnosis: "Both levels of the problem share one cause: the model already has a
  cheaper route and is never trained to take it."
- Action level: "a dense tool bonus raises spreadsheet adoption **0.03 → 0.33** and
  carries into greedy decoding, but **held-out accuracy does not follow. Behavior
  is steerable; competence is not.** The bottleneck lies in tool-call semantics."
- Context level: dropping the redundant screenshot and halving image history "cuts
  input tokens by about a third, at a small accuracy cost. Retraining under the
  same observation rule removes that cost. The compressed agent then reaches
  **37.8%** against **33.0%** for the uncompressed operating point, at **53%** of
  the input cost, and closes the rich-lean gap on a pre-registered degraded subset
  to zero."

## Failure modes

Abstract-only. This abstract is unusually well-instrumented — 5 runs per condition,
significance stated, a pre-registered subset — so most entries here are about scope
rather than rigor.

- `[observed]` **The strongest result is negative and the paper leads with it
  honestly: reward shaping moved behaviour without moving capability.** Tool
  adoption 0.03 → 0.33 with no held-out accuracy gain is a direct demonstration
  that a dense process-style reward can be optimized while the underlying
  competence is unchanged. That is reward hacking with a benign reward, and it is
  the concrete instance of the risk
  [[yuan2026verifiableprocessrewardsagentic]] bounds theoretically and
  [[venkataramani2026masproveunderstandingprocessverification]] finds empirically.
  Anyone proposing dense agent rewards owes a "did competence follow?" check, and
  almost nobody in this batch runs one.

- `[observed]` **One benchmark, 309 tasks, one harness.** The design that makes the
  +4.0/−5.9 contrast credible (identical harness) also means the result is a
  statement about OSWorld-MCP. Whether the adoption gap generalizes to other tool
  surfaces is untested.

- `[observed]` **"Tool-reachable" is a judgement made by the authors** and it sets
  the denominator of the headline 23.9%. How tool-reachability was determined —
  and whether a task the model solved by screenshot was genuinely better solved by
  tool — is the thing to check.

- `[observed]` **The compression win is confounded with retraining.** 37.8% vs
  33.0% at 53% input cost is the *retrained* compressed agent against the
  uncompressed operating point. The abstract states the untrained compressed agent
  pays "a small accuracy cost", so part of the +4.8pp is the extra training, not
  the observation rule. The clean comparison — retrained uncompressed vs retrained
  compressed — is not reported here.

- `[observed]` **Reasoning vs non-reasoning is a two-model comparison** carrying a
  claim about a class distinction. The mechanism offered (tool-decision behaviour)
  is plausible and the failure taxonomy is specific, but n = 2.

## Relevance

Two things the wiki does not have. First, a measured case where **the same
capability addition helps one model and hurts another under an identical harness**
— which is direct evidence for the harness-versus-model attribution problem
[[chen2026horizongapplanningmemory]] calls "the single most consequential open
measurement problem", and shows the answer is not model-independent.

Second, "behavior is steerable; competence is not" is the cleanest one-line
statement of a failure mode that should become its own open-problems entry:
optimizing an agent against a process signal can move the measured behaviour while
leaving the capability untouched. Combined with
[[li2026auditingselfevolutionfinancialagents]] (capability up, safety down) and
[[peng2026writeexecuterefineskill]] (self-authored skills worse than none), the
pattern across three independent papers is that agent interventions move the thing
being measured more reliably than the thing being wanted.
