---
name: lit-review
description: Find papers and turn each one into a per-paper source note under raw/. Use when searching arXiv or Semantic Scholar, fetching a paper PDF, reading a specific paper, or adding a BibTeX citation. For cross-paper synthesis, "what do I know about X", or anything wiki-related, use karpathy-llm-wiki instead.
---

# Literature review — the fetch-and-note half

This skill ends where the wiki begins. It produces **one source note per paper**
in `raw/`; `karpathy-llm-wiki` compiles those into `wiki/` articles.

**Hand off to `karpathy-llm-wiki` when** the task is synthesis across papers,
answering "what do I know about X", updating `wiki/index.md`, or linting. Do not
write anything under `wiki/` from this skill.

## Loop

1. **Search** — `python3 bin/papers.py search "<query>" -n 15`. Merges arXiv +
   Semantic Scholar, dedups by title, sorts by citation count. Run 2-3 differently
   phrased queries; one phrasing never covers a subfield.
2. **Triage** — from titles/abstracts alone, pick what to actually read. For a
   pile of 50+, bulk-score with a cheap model instead of reading each:
   `python3 bin/llm.py -m deepseek-chat "Rate 0-5 relevance to <topic>: <abstract>"`
3. **Cite** — `python3 bin/papers.py bib <arxiv_id|doi>` appends to `refs.bib`
   (idempotent). **The key it returns is the note's filename.**
4. **Read** — `python3 bin/papers.py pdf <arxiv_id>` prints a path.

   Prefer `pdftotext <path> -` over rendering pages with `Read`: it is far cheaper
   in tokens and gives exact greppable text, which is what the verbatim-number
   requirement needs. Render pages with `Read` only when layout matters — a
   figure, or a table `pdftotext` has mangled.

   **`pdftotext` flattens tables into one column stream.** A multi-column results
   table arrives as a single run of numbers with the row labels above it, so column
   assignment is guesswork. Always cross-check a table figure against the prose
   before recording it; papers almost always restate their headline numbers in
   text. If a number appears only in a flattened table and nowhere in prose,
   render that page with `Read` rather than guessing.

   Read the actual paper before writing a note. Never write a note from the
   abstract and call it read — say `Read: abstract-only` if that is all you saw.
5. **Note** — write `raw/<topic>/<bibkey>.md`, format below.

Reuse an existing `raw/` topic directory if one is close enough; create a new one
only for a genuinely distinct area. Topic directories in `raw/` and `wiki/` mirror
each other.

## Note format

The filename is the BibTeX key, so notes, citations, and wiki articles all line up.

```markdown
> Source: Vaswani et al., NeurIPS 2017
> URL: https://arxiv.org/abs/1706.03762
> Collected: 2026-08-20
> Published: 2017-06-12
> Bibkey: vaswani2017attention
> Read: full            # full | skim | abstract-only

## Problem
What was broken before this paper.

## Method
The actual mechanism, concretely enough to reimplement.

## Results
Numbers **exactly as the paper prints them**, with the dataset and the baseline
they beat. Write 42.1 BLEU, not "about 42" — see Grounding below.

## Failure modes
The conditions under which the method breaks — the point of reading the paper.
Each one concrete enough to construct an input for, and tagged by provenance:

- `[stated]` the authors admit it. Discount it; stated limitations are chosen
  to look survivable.
- `[observed]` you inferred it from the method or the experimental setup. Worth
  more, because it is not in the abstract and most readers will not have it.

Write the trigger, not the regret: "degrades when the retrieval corpus contains
near-duplicate passages, since the reranker sees them as independent evidence",
not "may not generalize to all corpora". If one looks tractable, add a one-line
lead on what attacking it would take. Speculative is fine — it is a lead, not
a claim.

## Relevance
Why this matters to my work. One or two lines.
```

## Grounding — why verbatim matters

`raw/` is immutable and is the evidence layer the wiki is checked against.
`check_evidence.py` greps numbers appearing in `wiki/` articles against the raw
files they link. A number that was rounded, reformatted, or paraphrased on its way
into a note will read as an unverifiable claim later, or worse, silently propagate
a wrong figure into a paper.

So: every number, date, and direct quote in a note is copied from the PDF exactly
as printed. If the paper says 42K, write 42K, not 42,000. If you cannot find a
value in the PDF, do not write its exact form — state it without precision or
leave it out.

The chain is: **PDF → note (you verify at write time) → wiki (script verifies).**
The script cannot read PDFs, so step one is on you. This is the only step in the
repo where a mistake is undetectable later.

## Rules

- **The failure mode is the deliverable.** A summary of what a method does is
  re-derivable from the abstract at any time, so it is nearly worthless output.
  The condition under which the method breaks is only visible to someone who
  read it closely, and it is what a contribution gets built on. Read for that.
  A note whose `Failure modes` section is empty or vague means the paper was
  skimmed, whatever the `Read:` field claims.
- **Recurrence across papers is the finding.** When the same weakness shows up
  in several methods, that pattern is worth more than any single instance — it
  says the field has an unsolved problem, not that one author was sloppy. Notes
  cannot see each other, so this only surfaces in `wiki/`; flag it when you
  notice it so the wiki article can pick it up.
- **Follow citations both ways.** A paper's related-work section finds ancestors;
  Semantic Scholar citation counts find descendants. Seminal papers surface as
  ancestors of many hits.
- **Never invent a citation.** Every key must exist in `refs.bib`, put there by
  `papers.py bib`. A plausible-looking hallucinated BibTeX entry is the single
  worst failure mode in this repo.
- **Note contradictions but do not resolve them here.** A note records what its
  own paper claims. Conflicts between papers are the wiki's job — that is what
  its `Status: Disputed` blocks are for.
- One note per paper. Cross-paper documents belong in `wiki/`.
