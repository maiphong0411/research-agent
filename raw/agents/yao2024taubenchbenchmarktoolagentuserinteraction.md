> Source: Yao et al. (Sierra), arXiv preprint 2024
> URL: https://arxiv.org/abs/2406.12045
> Collected: 2026-08-20
> Published: 2024-06-17
> Bibkey: yao2024taubenchbenchmarktoolagentuserinteraction
> Read: full

## Problem

"Existing benchmarks do not test language agents on their interaction with human
users or ability to follow domain-specific rules, both of which are vital for
deploying them in real world applications." Prior benchmarks "often feature
simplified instruction-following setups… given all the information upfront,
without any human-in-the-loop interaction and without the need to consult any
domain-specific guidelines."

Names three deployment requirements agents must meet: long-horizon interaction
with humans *and* APIs, adherence to domain policy, and "consistency and
reliability at scale, across millions of interactions."

## Method

Two domains (τ-retail, τ-airline), each with JSON databases, Python API tools, and
a **policy document** the agent must follow. The database state `s_db` is hidden
from the agent, reachable only through tools. The user is simulated by an LM and
"cannot see" the agent's tools.

**Reward** `r = r_action × r_output ∈ {0,1}`: the final database must be "identical
to the unique ground truth outcome database", and the agent's replies must contain
required substrings.

**pass^k** ("pass hat k") — "the chance that all k i.i.d. task trials are
successful". Deliberately inverted from pass@k, which is "the chance that at least
one out of k i.i.d. task trials is successful". `pass^1 = pass@1 = E[r]`.

## Results

- gpt-4o with function calling: succeeds on **< 50%** of tasks (pass^1).
- **pass^8 < 25%** on τ-retail — "drops rapidly, to as low as ∼25% for pass^8".
- Stated failure categories: agents "struggle with complex reasoning over
  databases, understanding and following ad-hoc policies, and handling compound
  (more than one) requests."

## Failure modes

- `[observed]` **Reliability, not capability, is the binding constraint.** pass^1
  under 50% falling to pass^8 under 25% means an agent that can do a task often
  cannot do it *eight times running*. Averaged single-run benchmarks hide this
  entirely — the same model looks twice as good under pass@1. This reframes the
  problem: the gap to deployment is variance, not ability. The paper measures the
  collapse but proposes no method to fix it, closing only with "the need for
  methods that can improve the ability of agents to act consistently."

- `[stated]` **The benchmark's own reward can pass a policy-violating trajectory.**
  "r = 1 might be a necessary but not sufficient condition for a successful
  episode e.g., the agent might issue the return without explicit user
  confirmation, which violates the policy." So reported scores are an *upper
  bound* on real compliance — the headline "< 50%" is generous. Attackable
  directly: a reward that checks the trajectory, not just the terminal database
  state, would likely lower every number in the paper.

- `[stated]` **Compound requests break agents.** More than one request in a
  conversation is called out as a distinct failure category, which suggests state
  tracking across sub-goals — not tool use — is the weak point.

- `[stated]` **Ad-hoc policy following is unsolved.** Policies are natural-language
  documents; some restrictions are enforced in code and some are not. Agents fail
  at the natural-language-only rules, which is exactly the class that cannot be
  guarded programmatically.

- `[observed]` **The user is an LM, so measured failures are partly simulator
  artifacts.** Stochasticity comes from "LM sampling of the user and agent
  messages". A simulated user can be inconsistent or unhelpfully terse in ways a
  real user would not, and the paper does not separate agent-caused from
  user-simulator-caused failures. Some of the pass^8 collapse may be user variance
  attributed to the agent.

- `[observed]` **Unique-ground-truth annotation constrains task realism.** Tasks
  are built so the user instruction "leads to a unique database outcome" —
  ambiguity has to be annotated away. Real requests admit several acceptable
  outcomes, so the benchmark systematically excludes the underspecified tasks
  where agents likely fail worst.

- `[observed]` **Two hand-built domains.** Both were manually designed as "the
  simplest possible database schemas, APIs, and policies". Generalization to
  domains with deeper schemas or conflicting policies is untested.

## Relevance

The strongest available evidence that the agent bottleneck is *consistency*, and
the source of the pass^k metric that makes it visible. Its own admission that the
reward can pass policy violations is a clean, concrete opening: a
trajectory-aware reward is a well-scoped contribution that would tighten every
number reported here.
