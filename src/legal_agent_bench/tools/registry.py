"""Agent tools: search, retrieve, summarize, citation_check.

Each tool returns a string result and reports a per-call cost in USD. The
costs are illustrative; the harness tracks them faithfully across the run so
the per-task cost metric is comparable across configurations.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

Tool = Callable[[dict[str, str]], tuple[str, float]]


@dataclass
class ToolRegistry:
    """Map of tool name -> tool callable. Tools are stateless."""

    search: Tool
    retrieve: Tool
    summarize: Tool
    citation_check: Tool

    def get(self, name: str) -> Tool:
        if not hasattr(self, name):
            raise KeyError(f"unknown tool {name}")
        attr = getattr(self, name)
        if not callable(attr):
            raise KeyError(f"{name} is not a tool")
        return attr  # type: ignore[no-any-return]


def make_bm25_search(corpus: list[str]) -> Tool:
    """Return a search tool over `corpus`. Per-call cost: $0.0001 (synthetic)."""
    tokenized = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized)

    def search(args: dict[str, str]) -> tuple[str, float]:
        query = args.get("query", "").lower().split()
        if not query:
            return ("no query", 0.0001)
        scores = bm25.get_scores(query)
        idx = sorted(range(len(corpus)), key=lambda i: scores[i], reverse=True)[:3]
        hits = "\n".join(f"[{i}] {corpus[i][:200]}" for i in idx)
        return (hits, 0.0001)

    return search


def make_retrieve(corpus: list[str]) -> Tool:
    """Fetch a document by index."""

    def retrieve(args: dict[str, str]) -> tuple[str, float]:
        try:
            i = int(args.get("idx", "0"))
        except ValueError:
            return ("bad idx", 0.00005)
        if not (0 <= i < len(corpus)):
            return ("out of range", 0.00005)
        return (corpus[i], 0.00005)

    return retrieve


def make_summarize() -> Tool:
    """Return a trivial 1-sentence summary."""

    def summarize(args: dict[str, str]) -> tuple[str, float]:
        text = args.get("text", "")
        first = text.split(".")[0].strip()
        return (first or "(empty)", 0.0002)

    return summarize


def make_citation_check() -> Tool:
    """Return whether a citation string looks well-formed."""

    def citation_check(args: dict[str, str]) -> tuple[str, float]:
        cite = args.get("cite", "")
        well_formed = any(t in cite for t in ("U.S.", "F.", "S.Ct.", "Fed. R.", "FRE", "FRCP", "§"))
        return (str(well_formed), 0.00005)

    return citation_check


def default_registry(corpus: list[str]) -> ToolRegistry:
    return ToolRegistry(
        search=make_bm25_search(corpus),
        retrieve=make_retrieve(corpus),
        summarize=make_summarize(),
        citation_check=make_citation_check(),
    )
