> Source: Yao et al., ICLR 2023
> URL: https://arxiv.org/abs/2210.03629
> Collected: 2026-08-20
> Published: 2023-03-10
> Bibkey: yao2023reactsynergizingreasoningacting
> Read: full

## Problem

Chain-of-thought reasoning is "a static black box, in that the model uses its own
internal representations to generate thoughts and is not grounded in the external
world" — leading to "fact hallucination and error propagation". Conversely,
action-generation work "do not employ language models to reason abstractly about
high-level goals or maintain a working memory to support acting."

## Method

Augment the action space to `Â = A ∪ L` where `L` is the space of language. A
"thought" is an action in language space that "does not affect the external
environment, thus leading to no observation feedback" — it only updates context
`c_{t+1} = (c_t, â_t)`.

Frozen PaLM-540B, prompted with 1–6 in-context human trajectories. For reasoning
tasks, thoughts and actions strictly alternate; for decision-making tasks
"thoughts only need to appear sparsely" and the model decides when to emit them.

Wikipedia action space: `search[entity]` (first 5 sentences or top-5 similar
entities), `lookup[string]` (next sentence containing string), `finish[answer]`.

## Results

- HotpotQA EM: ReAct **27.4** vs CoT **29.4** — ReAct *loses*.
- FEVER: ReAct **60.9** vs CoT **56.3**.
- ALFWorld: absolute success-rate improvement of **34%** over imitation/RL.
- WebShop: absolute improvement of **10%**.
- Step budget: **7** steps (HotpotQA), **5** (FEVER). Trajectories using the full
  budget are **0.84%** and **1.33%** of correct answers respectively.
- Finetuning used **3,000** ReAct-generated correct trajectories.

Table 2, hand-labeled over 200 sampled trajectories (50 correct + 50 incorrect
per method):

| Mode | ReAct | CoT |
|---|---|---|
| True positive | 94% | 86% |
| False positive | 6% | 14% |
| Reasoning error | 47% | 16% |
| Search result error | 23% | — |
| Hallucination | 0% | 56% |
| Label ambiguity | 29% | 28% |

## Failure modes

- `[stated]` **Repetitive action loops — the signature ReAct failure.** "the model
  repetitively generates the previous thoughts and actions… the model fails to
  reason about what the proper next action to take and jump out of the loop."
  Folded into the 47% reasoning-error bucket, so its standalone rate is unreported.
  Authors "suspect that this could be due to the sub-optimal greedy decoding
  procedure" and defer beam search to future work — i.e. the mechanism is not
  established, only guessed at. Attacking this needs a loop detector or a
  decoding change; the authors never tested either.

- `[stated]` **Non-informative search derails the trajectory unrecoverably.**
  23% of error cases. Empty or useless search returns give the model "a hard time
  to recover and reformulate thoughts." The failure is not the bad retrieval but
  the *inability to recover from it* — there is no backtracking mechanism.

- `[stated]` **Interleaving costs reasoning flexibility.** Reasoning error 47% vs
  CoT's 16%: "such a structural constraint also reduces its flexibility in
  formulating reasoning steps." The core design choice is itself the regression,
  which is why ReAct loses to CoT on HotpotQA.

- `[observed]` **Thinking longer cannot rescue a bad trajectory.** The step budget
  is hard (7/5), and the authors note "more steps will not improve ReAct
  performance," with full-budget trajectories only 0.84%/1.33% of successes.
  Combined with the loop failure above: once looping, the agent burns its budget
  and cannot escape. Compute is not the bottleneck — trajectory recovery is.

- `[observed]` **Capability-gated: unusable on small models via prompting.** With
  PaLM-8B/62B, "prompting ReAct performs worst among four methods due to the
  difficulty to learn both reasoning and acting from in-context examples." It only
  wins after finetuning on 3,000 trajectories. So the paradigm needs either a
  frontier model or supervised data — a real barrier for cheap-model agents.

- `[observed]` **Benchmark ceiling contaminates the result.** Label ambiguity is
  29% of ReAct's judged cases and "some HotpotQA questions may contain outdated
  answer labels." With EM gaps to CoT of ~2 points, the headline HotpotQA
  comparison sits inside the annotation noise.

- `[observed]` **The best system is a hand-tuned hybrid, not ReAct.** Top results
  come from ReAct→CoT-SC and CoT-SC→ReAct with hand-set backoff heuristics
  (fixed step thresholds, majority-vote below n/2). The switching rule is
  hand-designed per dataset, so the reported best numbers are not from ReAct
  alone and do not transfer without retuning.

## Relevance

The foundational interleaved reason+act paradigm; almost every later agent
framework assumes it. Two of its failure modes — loop entrapment and
unrecoverable bad retrieval — are still live problems in current agent systems,
which makes them the most attackable surface here.
