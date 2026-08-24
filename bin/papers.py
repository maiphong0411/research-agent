#!/usr/bin/env python3
"""Paper search / BibTeX / PDF fetch across arXiv + Semantic Scholar.

stdlib only, so there is no install step and no venv to keep alive.

    python3 bin/papers.py search "retrieval augmented generation" -n 10
    python3 bin/papers.py bib 2005.11401          # arXiv id
    python3 bin/papers.py bib 10.1145/3477495     # DOI
    python3 bin/papers.py pdf 2005.11401          # -> .cache/pdf/2005.11401.pdf
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "refs.bib"
PDF_CACHE = ROOT / ".cache" / "pdf"
UA = {"User-Agent": "research-agent (https://github.com/; mailto:none)"}
ATOM = {"a": "http://www.w3.org/2005/Atom"}
ARXIV_ID = re.compile(r"(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?)$", re.I)


def get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_arxiv(xml_bytes):
    out = []
    for e in ET.fromstring(xml_bytes).findall("a:entry", ATOM):
        aid = (e.findtext("a:id", "", ATOM)).rsplit("/", 1)[-1]
        out.append({
            "source": "arxiv",
            "id": aid,
            "title": " ".join(e.findtext("a:title", "", ATOM).split()),
            "authors": [a.findtext("a:name", "", ATOM) for a in e.findall("a:author", ATOM)],
            "year": e.findtext("a:published", "", ATOM)[:4],
            "abstract": " ".join(e.findtext("a:summary", "", ATOM).split()),
            "citations": None,
            "url": f"https://arxiv.org/abs/{aid}",
        })
    return out


def arxiv_query(query):
    """Build an arXiv search_query expression.

    Bare space-separated terms match far too loosely (a query for retrieval
    augmented generation returns anything about "augmentation"), but forcing the
    whole string into one quoted phrase is too strict — nobody writes the literal
    phrase "agentic systems tool use language models". So: explicit AND across
    terms, and an exact phrase only when the caller asks for one with quotes.
    """
    q = query.strip()
    if q.startswith('"') and q.endswith('"') and len(q) > 2:
        return f"all:{q}"
    return " AND ".join(f"all:{t}" for t in q.split())


def arxiv_search(query, limit, recent=False):
    q = urllib.parse.urlencode({"search_query": arxiv_query(query), "start": 0,
                                "max_results": limit,
                                "sortBy": "submittedDate" if recent else "relevance"})
    return parse_arxiv(get(f"http://export.arxiv.org/api/query?{q}"))


# ponytail: `recent` is accepted and ignored — this S2 endpoint has no date sort.
# Keeps search()'s dispatch loop a single uniform call.
def s2_search(query, limit, recent=False):
    q = urllib.parse.urlencode({
        "query": query, "limit": limit,
        "fields": "title,authors,year,abstract,citationCount,externalIds,url",
    })
    # Unauthenticated S2 shares a global rate limit and 429s often. A free key
    # (https://www.semanticscholar.org/product/api) removes that; without one
    # search still works, just arXiv-only, with a note on stderr.
    key = os.environ.get("S2_API_KEY")
    data = json.loads(get(f"https://api.semanticscholar.org/graph/v1/paper/search?{q}",
                          {"x-api-key": key} if key else None))
    out = []
    for p in data.get("data") or []:
        ext = p.get("externalIds") or {}
        out.append({
            "source": "s2",
            "id": ext.get("ArXiv") or ext.get("DOI") or p.get("paperId"),
            "title": " ".join((p.get("title") or "").split()),
            "authors": [a.get("name") for a in p.get("authors") or []],
            "year": str(p.get("year") or ""),
            "abstract": " ".join((p.get("abstract") or "").split()),
            "citations": p.get("citationCount"),
            "url": p.get("url") or "",
        })
    return out


def norm(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def search(query, limit, recent=False):
    """Merge both sources, preferring whichever record carries a citation count."""
    merged = {}
    for fetch in (arxiv_search, s2_search):
        try:
            hits = fetch(query, limit, recent)
        except Exception as e:  # one dead API must not kill the search
            print(f"# {fetch.__name__} unavailable: {e}", file=sys.stderr)
            continue
        for p in hits:
            k = norm(p["title"])
            if k and (k not in merged or merged[k]["citations"] is None):
                merged[k] = p
    hits = list(merged.values())
    # Citation-count ranking is exactly wrong for a recency search: a paper from
    # last month has no citations yet and would sort to the bottom. arXiv already
    # returned newest-first, and dict insertion preserved it, so leave it alone.
    if not recent:
        hits.sort(key=lambda p: (p["citations"] is None, -(p["citations"] or 0)))
    return hits[:limit]


def fmt(hits):
    for p in hits:
        who = ", ".join(p["authors"][:3]) + (" et al." if len(p["authors"]) > 3 else "")
        cites = "" if p["citations"] is None else f" · {p['citations']} cites"
        print(f"\n## {p['title']}\n{who} ({p['year']}){cites} · {p['id']} · {p['url']}")
        print(f"\n{p['abstract'][:600]}")


def bibtex(ident):
    m = ARXIV_ID.match(ident)
    if m:
        return get(f"https://arxiv.org/bibtex/{m.group(1)}").decode()
    return get(f"https://doi.org/{urllib.parse.quote(ident)}",
               {"Accept": "application/x-bibtex"}).decode()


def bib_key(entry):
    m = re.search(r"@\w+\s*\{\s*([^,\s]+)", entry)
    return m.group(1) if m else ""


def add_bib(entry):
    """Append to refs.bib unless the key is already there. Returns the key."""
    key = bib_key(entry)
    existing = REFS.read_text() if REFS.exists() else ""
    if key and re.search(r"@\w+\s*\{\s*" + re.escape(key) + r"\s*,", existing):
        return key, False
    sep = "\n\n" if existing.strip() else ""   # no leading blank lines in a fresh file
    REFS.write_text(existing.rstrip() + sep + entry.strip() + "\n")
    return key, True


def pdf(ident):
    m = ARXIV_ID.match(ident)
    if not m:
        sys.exit("pdf: arXiv ids only (DOIs are usually paywalled — fetch by hand)")
    aid = m.group(1)
    PDF_CACHE.mkdir(parents=True, exist_ok=True)
    dest = PDF_CACHE / f"{aid}.pdf"
    if not dest.exists():
        dest.write_bytes(get(f"https://arxiv.org/pdf/{aid}", timeout=120))
    return dest


def selftest():
    xml = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry>
      <id>http://arxiv.org/abs/1706.03762v5</id><title>Attention Is
      All You Need</title><published>2017-06-12T00:00:00Z</published>
      <summary>We propose  the Transformer.</summary>
      <author><name>Ashish Vaswani</name></author></entry></feed>"""
    p = parse_arxiv(xml)[0]
    assert p["id"] == "1706.03762v5", p["id"]
    assert p["title"] == "Attention Is All You Need", p["title"]  # newline collapsed
    assert p["abstract"] == "We propose the Transformer."         # double space collapsed
    assert p["year"] == "2017"
    assert bib_key("@article{vaswani2017, title={x}}") == "vaswani2017"
    assert bib_key("no entry here") == ""
    assert ARXIV_ID.match("arXiv:2005.11401").group(1) == "2005.11401"
    assert ARXIV_ID.match("10.1145/3477495") is None
    assert norm("Attention Is All You Need!") == "attentionisallyouneed"
    # multi-term queries must AND, not become one unmatchable exact phrase
    assert arxiv_query("llm agents") == "all:llm AND all:agents"
    assert arxiv_query('"chain of thought"') == 'all:"chain of thought"'
    assert arxiv_query("  spaced   out  ") == "all:spaced AND all:out"
    assert arxiv_query("solo") == "all:solo"
    print("ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("-n", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.add_argument("--recent", action="store_true",
                   help="sort arXiv newest-first instead of by relevance")
    b = sub.add_parser("bib"); b.add_argument("ident")
    b.add_argument("--stdout", action="store_true", help="print instead of appending to refs.bib")
    d = sub.add_parser("pdf"); d.add_argument("ident")
    sub.add_parser("selftest")
    a = ap.parse_args()

    if a.cmd == "search":
        hits = search(a.query, a.n, a.recent)
        print(json.dumps(hits, indent=2)) if a.json else fmt(hits)
    elif a.cmd == "bib":
        entry = bibtex(a.ident)
        if a.stdout:
            print(entry)
        else:
            key, added = add_bib(entry)
            print(f"{key}\t{'added to' if added else 'already in'} {REFS}")
            # arXiv's endpoint dates the entry by its LATEST revision, so a 2017
            # paper revised in 2023 cites as (2023). Fine for a preprint, wrong
            # for the published version — say so rather than fail silently.
            if entry.lstrip().startswith("@misc"):
                print("note: arXiv preprint entry (@misc); its year is the last "
                      "revision, not the venue year. If this paper was published, "
                      "replace it with the venue's BibTeX.", file=sys.stderr)
    elif a.cmd == "pdf":
        print(pdf(a.ident))
    elif a.cmd == "selftest":
        selftest()


if __name__ == "__main__":
    main()
