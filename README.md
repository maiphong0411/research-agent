# research-agent

A research workspace for ML/AI/NLP, aimed at a future CS master's: literature
review, LaTeX papers, Beamer slides, and the experiments behind them.

There is no agent framework here to build. Claude Code *is* the agent; this repo
is its workspace plus the config that specializes it. Missing capability gets
fixed with a skill, a hook, a `settings.json` entry, or a small script in
`bin/` — not a new abstraction layer.

`CLAUDE.md` is the agent's instruction file and is the authoritative spec. This
README is the human orientation.

---

## Setup

```bash
brew install tectonic    # LaTeX engine
brew install poppler     # pdftotext + pdftoppm
```

`poppler` is not optional: reading a paper requires it, and `Read` on a PDF
fails without `pdftoppm`.

`bin/*.py` are stdlib-only. No venv, no `pip install`, no lockfile.

Optional: `export S2_API_KEY=...` (free) restores Semantic Scholar citation
counts. Without it, paper search degrades to arXiv-only and says so on stderr.

---

## The idea

Three tiers, three owners. The middle tier is the point — reading a pile of
papers without it stops scaling around 50 papers.

```
arXiv / Semantic Scholar
        │
        ├── papers.py bib ──► refs.bib          one shared bibliography
        │                     (bibkey becomes the note filename)
        │
        └── papers.py pdf ──► .cache/pdf/*.pdf
                                   │
                          read the paper
                                   ▼
                     raw/<topic>/<bibkey>.md     one note per paper
                     verbatim numbers            IMMUTABLE once written
                                   │
                          triage, then compile
                                   ▼
                     wiki/<topic>/<name>.md      synthesis across papers
                                   │
                                   ├──► wiki/index.md
                                   └──► projects/<name>/main.tex
```

`check_evidence.py` greps numbers in `wiki/` against the `raw/` files each
article links. That is the only mechanical check in the chain — the PDF → note
step is verified by nothing but whoever writes the note.

**What the pipeline is for:** not storage. Finding an attackable weakness in a
specific existing method. So the load-bearing section of every note is
`Failure modes`, not `Method`, with each entry tagged `[stated]`
(author-admitted, discount it) or `[observed]` (you inferred it, worth more).

A weakness in one paper is an anecdote. The same weakness across four is an
unsolved problem in the field, and that is a thesis topic — which is what
`wiki/<topic>/open-problems.md` accumulates.

---

## Common tasks

Ask Claude in plain language; the skills below fire automatically. The commands
are what runs underneath.

**Find and note a paper** → the `lit-review` skill

```bash
python3 bin/papers.py search "<query>" -n 15    # arXiv + Semantic Scholar, deduped
python3 bin/papers.py search "<query>" --recent # newest-first instead of by relevance
python3 bin/papers.py bib 2005.11401            # append BibTeX to refs.bib (idempotent)
python3 bin/papers.py pdf 2005.11401            # -> .cache/pdf/<id>.pdf
pdftotext .cache/pdf/2005.11401.pdf -           # cheaper than Read; exact, greppable
```

**Synthesize across papers** → the `karpathy-llm-wiki` skill

Anything spanning papers: "what do I know about X", compiling an article,
updating the index, linting.

**Write a paper or deck** → the `latex` skill

```bash
cd projects/<name> && tectonic main.tex
```

**Bulk triage with a cheap model** (non-Claude only — scoring 200 abstracts)

```bash
python3 bin/llm.py -m deepseek-chat "Rate 0-5 relevance to <topic>: <abstract>"
```

Providers: `deepseek`, `openai`, `openrouter`, `groq`, `ollama`. Anthropic's API
is not OpenAI-compatible; don't add Claude here — Claude is already the agent.

**Health check**

```bash
python3 bin/papers.py selftest      # parser + bibkey assertions
python3 bin/llm.py --selftest       # provider resolution assertions
python3 .agents/skills/karpathy-llm-wiki/scripts/check_evidence.py .
```

There is no test framework. Each script carries a `selftest` covering its
non-trivial logic; extend that rather than adding pytest.

---

## What's in here (2026-08-24)

| | |
|---|---|
| Topics | `agents` |
| Source notes | 21 in `raw/agents/` — 10 read in full, 11 abstract-only |
| Wiki articles | 9 in `wiki/agents/` |
| Bibliography | 22 entries in `refs.bib` |
| Projects | `projects/agents-litreview/` — 8-page review + slides |

Start reading at [`wiki/index.md`](wiki/index.md). The two entry points worth
knowing:

- [`wiki/agents/open-problems.md`](wiki/agents/open-problems.md) — nine recurring
  failure modes across 21 papers, each with what attacking it would require. This
  is where thesis topics come from.
- [`wiki/agents/long-horizon-vocabulary.md`](wiki/agents/long-horizon-vocabulary.md)
  — long-horizon vs long-context vs long-term memory as independent axes. Load-
  bearing for reading anything else in the topic.

---

## Layout

```
raw/<topic>/<bibkey>.md   one source note per paper — IMMUTABLE once written
wiki/<topic>/<name>.md    cross-paper synthesis, compiled from raw/
wiki/index.md             global table of contents
wiki/log.md               append-only operation log
refs.bib                  single bibliography for every project
projects/<name>/          main.tex, slides.tex, figures/, experiments/
bin/                      stdlib-only helpers
.claude/skills/           lit-review, latex, karpathy-llm-wiki (symlink)
.claude/hooks/            tex-check.sh — compiles after every .tex edit
```

Topic directories in `raw/` and `wiki/` mirror each other. `wiki/` supports one
level of topic subdirectory only.

Not tracked: `.cache/` (re-fetchable PDFs), `.agents/` and the wiki skill symlink
(restore with `npx add-skill Astro-Han/karpathy-llm-wiki`), `*.pdf` build output
(`git add -f` to archive a submitted version).

---

## The rules that matter

**`raw/` is immutable.** Once a note is written it is evidence, not a draft. New
understanding goes into `wiki/`, not back into the note. This is what makes the
mechanical fact-check possible: a verified article stays verified.

**Numbers in `raw/` are verbatim.** If the paper says 42K, write 42K, not 42,000.
`check_evidence.py` can grep `wiki/` against `raw/`, but nothing can grep `raw/`
against a PDF. Round a figure there and the error is undetectable from then on.

**Never invent a citation.** Every `\cite` key must exist in `refs.bib`, put
there by `papers.py bib`. A plausible-looking fabricated entry is the worst
failure mode in this repo — it survives review and ends up in a submission.

**Never invent a number.** Every figure and table value traces to a script in the
relevant `experiments/`. If you can't point at what produced it, it doesn't go in
the paper.

**The evaluation harness is frozen.** Split each experiment in two: the metric
(read-only once a baseline exists) and the thing you are changing. Never edit the
metric to improve a result. This is not bureaucracy —
`wiki/agents/open-problems.md` entry 3 documents a field-wide pattern of
evaluations that flatter their own method, and a read-only harness is the
structural fix.

**The discards are the point.** Every run appends one row to
`projects/<name>/experiments/results.tsv` with status `keep`, `discard`, or
`crash`. A recorded negative result is the difference between "this does not
work" and "nobody checked". Don't delete a row because the idea failed.

---

## Things that will bite you

Short list; `CLAUDE.md` has the full version with reasons.

- **Tectonic can't run `biber`**, so biblatex is unavailable. Use `natbib` +
  `bibtex`.
- **The first `tectonic` run takes ~3 minutes** while it downloads its package
  bundle. It has not hung. Warm builds are ~0.7s.
- **Hooks load at session start.** Editing `.claude/settings.json` mid-session
  does nothing until you restart.
- **arXiv BibTeX carries the last-revision year, not the venue year.** The 2017
  Transformer paper cites as (2023). Correct for a preprint, wrong for the
  published version — replace with the venue's BibTeX before submitting.
- **Semantic Scholar 429s without a key**, and search silently degrades to
  arXiv-only.
