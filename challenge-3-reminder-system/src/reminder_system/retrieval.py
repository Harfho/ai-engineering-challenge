"""Context-aware retrieval: given the user's current request, return only
the reminders that actually apply, ranked.

Design notes (calibrated against an adversarial query battery):

* Matching evidence comes ONLY from trigger_context + description. The
  recommended_action text is excluded: every action mentions generic verbs
  ("retry", "check"), which used to let unrelated queries match any
  reminder through its advice boilerplate.
* A candidate is considered only if the query supplies real evidence:
  at least one specific (non-generic) token shared with the reminder's
  triggers/description, OR at least two distinct concept-group seeds
  (e.g. "column" + "table" together imply schema work even though neither
  word appears in the reminder).
* Concept groups expand ONLY approved candidates and contribute a capped
  boost, so a single ambiguous word ("retry") can never drag a whole
  topic group in with it.
* Relevance is a bounded ratio M / (M + K), not a saturating transform of
  raw overlap: scores stay separated instead of piling up near 1.0, which
  makes the threshold meaningful.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import List

from .models import Reminder
from .patterns import STOPWORDS, _stem
from .providers import EmbeddingProvider, HashingEmbedder

_TOKEN = re.compile(r"[a-z][a-z_\-]{2,}")

# Generic process vocabulary: legitimate expansion seeds, but never counted
# as direct matching evidence (any reminder's advice could contain these).
GENERIC_TOKENS = {
    "retry", "retries", "retrying", "call", "calls", "called",
    "request", "requests", "requested", "check", "checks", "verify",
    "ensure", "make", "set", "run", "runs", "update", "updated",
    "change", "changes", "work", "works", "try", "tried", "handle",
    "handles", "process", "processes", "issue", "issues", "problem",
    "problems", "fix", "fixes", "operation", "operations",
    "page", "pages", "screen", "screen", "view", "component",
}

# Concept groups for deterministic query bridging. A user asking to "add a
# column" never says the word "migration"; these groups bridge that gap,
# but only when >= 2 distinct seeds point at the same group.
CONCEPT_GROUPS = [
    {"column", "columns", "table", "tables", "alter", "schema",
     "migration", "migrations", "database", "db", "drift", "index",
     "relation", "alembic"},
    {"api", "http", "endpoint", "rate", "rates", "limit", "limited",
     "throttle", "throttled", "throttling", "quota", "backoff", "429"},
    {"auth", "login", "credential", "credentials", "token", "permission",
     "password", "unauthorized", "401"},
    {"timeout", "timed", "outage", "unreachable"},
    {"connection", "connections", "connectivity", "db", "database",
     "dropped", "lost", "vanished", "disconnect", "reconnect"},
]

DEFAULT_THRESHOLD = 0.45


def approved_groups(tokens: List[str]) -> List[int]:
    """Indices of concept groups seeded by >= 2 distinct query tokens."""
    tset = set(tokens)
    return [gi for gi, group in enumerate(CONCEPT_GROUPS)
            if len(tset & group) >= 2]


def tokenize(text: str) -> List[str]:
    return [_stem(t) for t in _TOKEN.findall(text.lower())
            if t not in STOPWORDS]


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
        # Gate documents: triggers weighted 3x + description. Action text is
        # deliberately excluded from matching (see module docstring).
        self.gate_docs: List[List[str]] = []
        for r in self.reminders:
            trig = tokenize(" ".join(r.trigger_context)) * 3
            body = tokenize(" ".join(r.trigger_context) + " " + r.description)
            self.gate_docs.append(trig + body)
        df: dict = {}
        for toks in self.gate_docs:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        n = max(1, len(self.reminders))
        self.idf = {t: math.log((n + 1) / (c + 0.5)) for t, c in df.items()}
        self.doc_vecs = [self.embedder.embed(
            " ".join(r.trigger_context) + " " + r.description)
            for r in self.reminders]

    def retrieve(self, query: str, top_k: int = 3,
                 threshold: float = DEFAULT_THRESHOLD
                 ) -> List[RetrievedReminder]:
        qtoks = tokenize(query)
        if not qtoks or not self.reminders:
            return []
        qset = set(qtoks)
        groups = approved_groups(qtoks)
        scored = []
        for i, (r, dtoks) in enumerate(zip(self.reminders, self.gate_docs)):
            direct = []
            direct_mass = 0.0
            for t in qset:
                if t in GENERIC_TOKENS or t not in dtoks:
                    continue
                w = self.idf.get(t, 1.0)
                tf = dtoks.count(t)
                direct_mass += w * (1 + math.log(tf))
                direct.append(t)
            if not direct and not groups:
                continue  # no evidence pathway -> never a candidate
            exp_mass = 0.0
            expanded = []
            if groups:
                exp_pool = [(self.idf.get(t, 1.0), t)
                            for t in set(dtoks)
                            if t not in qset and t not in GENERIC_TOKENS
                            and any(t in CONCEPT_GROUPS[g] for g in groups)]
                exp_pool.sort(reverse=True)
                for w, t in exp_pool[:2]:
                    exp_mass += 0.9 * w
                    expanded.append(t)
            sem = 0.0
            if direct:
                dv = self.doc_vecs[i]
                qv = self.embedder.embed(query)
                cos = sum(x * y for x, y in zip(qv, dv))
                sem = max(0.0, cos) * 0.15
            m = direct_mass + exp_mass + sem
            if m <= 0:
                continue
            cap = 0.97 if direct else 0.78  # expansion-only can't outrank evidence
            rel = min(cap, m / (m + 1.4))
            matched_on = sorted(direct)[:4] + [f"~{t}" for t in expanded[:2]]
            scored.append((rel, matched_on, r))
        scored.sort(key=lambda s: -s[0])
        return [RetrievedReminder(r, rel, mo[:6])
                for rel, mo, r in scored[:top_k] if rel >= threshold]


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
              threshold: float = DEFAULT_THRESHOLD) -> List[RetrievedReminder]:
        if self._retriever is None:
            self.refresh()
        return self._retriever.retrieve(context, top_k=top_k,
                                        threshold=threshold)

    def list_reminders(self):
        return self.store.all_reminders()
