"""Recurring-pattern detection: cluster similar ErrorEvents.

Algorithm (deterministic, explainable):
1. Tokenize normalized messages (drop stopwords).
2. Greedy clustering: each event joins the first cluster whose representative
   it is similar to; otherwise starts a new cluster. Similarity = weighted
   Jaccard on token sets.
3. A cluster becomes a pattern when frequency >= min_frequency AND it spans
   >= min_sessions distinct sessions (single bad session != recurring issue).

Trigger tokens for a cluster are the tokens shared by a plurality of its
members — the stable "shape" of the failure.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

from .models import ErrorEvent, ErrorPattern

STOPWORDS = set("""
a an the this that these those with without from into onto for to of in on at
by is are was were be been being do does did done not no nor but and or if as
it its we you they he she i our your their my me him her them us out up down
over under again further then once here there all any both each few more most
other some such only own same so than too very can will just should now has
have had having would could may might must shall about after before between
during through above below because while until against also error errors
failed failure result message agent action user request session timestamp
""".split())

_TOKEN = re.compile(r"[a-z][a-z_\-]{2,}")


def _stem(tok: str) -> str:
    """Very light stemming: collapse simple plurals so 'migrations' ==
    'migration'. Deliberately not PorterStemmer — determinism and
    explainability beat linguistic correctness here."""
    if len(tok) > 4 and tok.endswith("s") and not tok.endswith("ss"):
        return tok[:-1]
    return tok


def tokenize(msg: str) -> List[str]:
    return [_stem(t) for t in _TOKEN.findall(msg.lower())
            if t not in STOPWORDS]


def _similarity(a: Counter, b: Counter) -> float:
    """Weighted Jaccard: shared mass over total mass."""
    keys = set(a) | set(b)
    inter = sum(min(a[k], b[k]) for k in keys)
    union = sum(max(a[k], b[k]) for k in keys)
    return inter / union if union else 0.0


def _trigger_tokens(members: List[ErrorEvent]) -> List[str]:
    """Tokens present in >= 60% of members, most frequent first."""
    n = len(members)
    counts: Counter = Counter()
    per_member = []
    for m in members:
        toks = set(tokenize(m.normalized_message))
        counts.update(toks)
        per_member.append(toks)
    thresh = max(2, int(n * 0.6))
    shared = [t for t, c in counts.items() if c >= thresh]
    return sorted(shared, key=lambda t: (-counts[t], t))[:8]


def extract_patterns(events: List[ErrorEvent],
                     min_frequency: int = 2,
                     min_sessions: int = 2,
                     similarity_threshold: float = 0.40,
                     ) -> List[ErrorPattern]:
    """Two-tier clustering:

    Tier 1 (semantic, deterministic): events sharing a category are one
    candidate group. The category keyword rules are the system's only
    semantic knowledge; trusting them for grouping is more robust than
    lexical similarity, which fails on paraphrase ("schema drift" vs
    "relation does not exist").

    Tier 2 (lexical fallback): uncategorized events use single-linkage
    token-Jaccard clustering at `similarity_threshold`.
    """
    by_cat: Dict[str, List[ErrorEvent]] = {}
    for ev in events:
        by_cat.setdefault(ev.category or "__uncategorized__", []).append(ev)

    # Uncategorized events are clustered in their own index space so their
    # positions can never collide with the pre-seeded category clusters.
    uncat_clusters: List[List[ErrorEvent]] = []
    uncat_bags: List[List[Counter]] = []
    for ev in by_cat.get("__uncategorized__", []):
        bag = Counter(tokenize(ev.normalized_message))
        best_ci, best_sim = -1, 0.0
        for ci, cbags in enumerate(uncat_bags):
            sim = max(_similarity(b, bag) for b in cbags)
            if sim > best_sim:
                best_ci, best_sim = ci, sim
        if best_ci >= 0 and best_sim >= similarity_threshold:
            uncat_clusters[best_ci].append(ev)
            uncat_bags[best_ci].append(bag)
        else:
            uncat_clusters.append([ev])
            uncat_bags.append([bag])

    clusters = [members
                for cat, members in by_cat.items()
                if cat != "__uncategorized__"]
    clusters.extend(uncat_clusters)

    patterns: List[ErrorPattern] = []
    for members in clusters:
        sessions = {m.session_id for m in members}
        if len(members) < min_frequency or len(sessions) < min_sessions:
            continue
        times = sorted(m.timestamp for m in members)
        pid = f"PAT-{abs(hash(tuple(sorted(m.normalized_message[:40] for m in members)))) % 100000:05d}"
        patterns.append(ErrorPattern(
            pattern_id=pid,
            members=members,
            label_tokens=_trigger_tokens(members),
            sessions=len(sessions),
            first_seen=times[0],
            last_seen=times[-1],
        ))
    patterns.sort(key=lambda p: (-p.frequency, p.pattern_id))
    return patterns
