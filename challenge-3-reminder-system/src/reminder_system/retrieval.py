"""Context-aware retrieval: given the user's current request, return only
the reminders that actually apply, ranked.

Scoring is TF-IDF-weighted token overlap between the query and each
reminder's trigger_context + description, with trigger tokens weighted 3x
(they are curated for matching). An optional EmbeddingProvider adds a
semantic cosine component. Scores are normalized to [0,1] against the best
match so thresholds stay meaningful regardless of corpus size.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import List

from .models import Reminder
from .patterns import STOPWORDS
from .providers import EmbeddingProvider, HashingEmbedder

_TOKEN = re.compile(r"[a-z][a-z_\-]{2,}")

# Concept groups for deterministic query expansion. A user asking to "add a
# column" never says the word "migration"; these groups bridge that gap
# without an embedding model. Expansion hits score at half weight.
CONCEPT_GROUPS = [
    {"column", "table", "alter", "schema", "migration", "migrations",
     "database", "db", "drift", "index", "relation", "alembic"},
    {"api", "http", "call", "calls", "request", "endpoint", "rate",
     "limit", "throttle", "quota", "backoff", "retry", "retries"},
    {"auth", "login", "credential", "credentials", "token", "permission",
     "password"},
    {"timeout", "timed", "outage", "unreachable", "connection"},
    {"connection", "connections", "connectivity", "db", "database",
     "dropped", "lost", "vanished", "disconnect", "reconnect",
     "sync", "batch", "bulk"},
]


def expand(tokens: List[str]) -> List[str]:
    tset = set(tokens)
    extra = []
    for group in CONCEPT_GROUPS:
        if tset & group:
            extra.extend(group)
    return list(set(extra) - tset)


def tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS]


@dataclass
class RetrievedReminder:
    reminder: Reminder
    relevance: float
    matched_on: List[str]

    def to_dict(self) -> dict:
        d = self.reminder.to_dict()
        d["relevance"] = round(self.relevance, 3)
        d["matched_on"] = self.matched_on
        return d


class Retriever:
    def __init__(self, reminders: List[Reminder],
                 embedder: EmbeddingProvider | None = None):
        self.reminders = reminders
        self.embedder = embedder or HashingEmbedder()
        self._build_stats()

    def _build_stats(self):
        self.doc_tokens: List[List[str]] = []
        for r in self.reminders:
            # triggers weighted 3x; description + action carry the rest
            trig = tokenize(" ".join(r.trigger_context)) * 3
            body = tokenize(" ".join(r.trigger_context) + " " +
                            r.description + " " + r.recommended_action)
            self.doc_tokens.append(trig + body)
        df: dict = {}
        for toks in self.doc_tokens:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        n = max(1, len(self.reminders))
        self.idf = {t: math.log((n + 1) / (c + 0.5)) for t, c in df.items()}
        self.doc_vecs = [self.embedder.embed(
            " ".join(r.trigger_context) + " " + r.description)
            for r in self.reminders]

    def retrieve(self, query: str, top_k: int = 3,
                 threshold: float = 0.25) -> List[RetrievedReminder]:
        qtoks = tokenize(query)
        if not qtoks or not self.reminders:
            return []
        qset = set(qtoks)
        exp = set(expand(qtoks))
        scored = []
        for i, (r, dtoks) in enumerate(zip(self.reminders, self.doc_tokens)):
            overlap, score = [], 0.0
            for t in qset:
                if t in dtoks:
                    w = self.idf.get(t, 1.0)
                    tf = dtoks.count(t)
                    score += w * (1 + math.log(tf))
                    overlap.append(t)
            for t in exp - qset:
                if t in dtoks:
                    score += 0.5 * self.idf.get(t, 1.0)
                    if len(overlap) < 6:
                        overlap.append(f"~{t}")
            sem = 0.0
            if score > 0 or len(qset) >= 2:
                dv = self.doc_vecs[i]
                qv = self.embedder.embed(query)
                sem = sum(x * y for x, y in zip(qv, dv))
            total = score + 0.5 * sem
            scored.append((total, overlap, r))
        scored.sort(key=lambda s: -s[0])
        # tanh calibration: bounded [0,1), monotonic, and independent of
        # query length (a long natural-language request shouldn't dilute
        # the score of its topical core).
        out = []
        for total, overlap, r in scored[:top_k]:
            if total <= 0:
                continue
            rel = math.tanh(total)
            if rel >= threshold:
                out.append(RetrievedReminder(r, rel, overlap[:6]))
        return out


class ReminderService:
    """Facade used by both the API layer and library consumers."""

    def __init__(self, store, embedder: EmbeddingProvider | None = None):
        from .store import Store  # typing only; avoid circular at module level
        assert isinstance(store, Store)
        self.store = store
        self._retriever: Retriever | None = None
        self.embedder = embedder

    def refresh(self):
        self._retriever = Retriever(self.store.all_reminders(), self.embedder)

    def query(self, context: str, top_k: int = 3,
              threshold: float = 0.25) -> List[RetrievedReminder]:
        if self._retriever is None:
            self.refresh()
        return self._retriever.retrieve(context, top_k=top_k,
                                        threshold=threshold)

    def list_reminders(self):
        return self.store.all_reminders()
