> Source: Yang, Venkit, Sedghamiz, Santus, Dibia, Baldini (Georgetown / Bayer / Microsoft / IBM), arXiv preprint 2026 — tutorial
> URL: https://arxiv.org/abs/2607.19336
> Collected: 2026-08-24
> Published: 2026-07-21
> Bibkey: yang2026agentswildresearchmeets
> Read: abstract-only

## Problem

"While academic work has emphasized benchmarks and algorithmic innovation,
deployment raises new challenges around robustness, safety, and reliability."

Agentic systems are "rapidly transitioning from research prototypes to production
scale deployments across domains such as software engineering, scientific
discovery, and finance."

## Method

Not a research paper — a **conference tutorial**. Covers "advances in reasoning
and planning, multi agent coordination, and evaluation", with "applied case studies
in pharmaceutical discovery and financial systems", analyzing "common design
patterns that make agentic systems successful", and "practical mitigation
strategies for failure modes, such as **verification pipelines, fallback
mechanisms, and human in the loop supervision**."

Deliverables promised to attendees: "concrete design patterns, evaluation
checklists, and templates for safe and reliable deployment across industries."

## Results

None. A tutorial abstract reports no experiments, no numbers, and no measurements.

## Failure modes

Abstract-only, and the genre is the main caveat.

- `[observed]` **This is not a citable source for any empirical claim.** No
  experiments, no dataset, no measurement. It can be cited for the *existence* of
  a research-versus-deployment gap and for the vocabulary of mitigation patterns,
  nothing more. Flagging this explicitly because the arXiv listing is
  indistinguishable from a research paper at a glance.

- `[observed]` **The case studies are the only potentially novel content and they
  are undescribed.** Pharmaceutical discovery and financial systems deployment
  experience from Bayer and IBM authors is exactly the industrial knowledge that
  [[chen2026horizongapplanningmemory]] identifies its 1,547-paper corpus as
  systematically missing ("under-represents unpublished industrial agent
  engineering that never reaches arXiv"). Whether the tutorial materials contain
  anything measured, or only patterns, decides whether it is worth reading.

- `[observed]` **"Design patterns that make agentic systems successful" is
  survivorship-shaped by construction.** Patterns extracted from deployed systems
  that work cannot distinguish the pattern from the conditions that let the system
  ship. No counterfactual is available in this genre.

## Relevance

Useful for one thing only: it is a direct, citable acknowledgement — from authors
at Bayer, Microsoft, and IBM — that the deployment setting and the benchmark
setting come apart, which is open problem 4 in `wiki/agents/open-problems.md`
("Retry, reset, and oracle assumptions exclude deployment"). Its named mitigation
triad (verification pipelines, fallback mechanisms, human-in-the-loop) is what
industry actually does about the problem the research literature treats as open,
and that contrast is worth a line in the wiki entry.

Do not cite for numbers. Do not promote to a full read unless the tutorial
materials turn out to contain the case-study data.
