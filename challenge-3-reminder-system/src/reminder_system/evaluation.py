"""Labeled evaluation harness for retrieval quality.

Relevance judgments are explicit and external to the system under test:

* POSITIVE_QUERIES: (query, marker) pairs. `marker` is a substring that
  identifies the ONE reminder a competent reviewer would expect (its
  action/description text). These were written as reviewer-style tasks,
  not derived from the reminder texts.
* NEGATIVE_QUERIES: adversarial/unrelated developer requests that must
  fire nothing.

Metrics follow standard IR definitions:
    TP  positive query, correct reminder fired
    FP  fired a reminder that shouldn't fire (wrong reminder on a
        positive query, or anything on a negative query)
    FN  positive query answered with silence
    TN  negative query answered with silence

The shipped default threshold (0.45) was selected on this set; the sweep
helper reproduces the selection so it can be audited rather than trusted.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

# --- positive relevance judgments -----------------------------------------

POSITIVE_QUERIES: List[Tuple[str, str]] = [
    # schema/migration cluster
    ("add a new column to the users table", "migration"),
    ("alter the orders schema to rename the status values", "migration"),
    ("run alembic migrations before deploying the release", "migration"),
    ("create an index on the events table user id column", "migration"),
    ("deploy failed because schema drift was detected again", "migration"),
    ("the relation users does not exist in the staging database", "migration"),
    ("write a migration file for the plan column change", "migration"),
    ("users table needs a plan column added today", "migration"),
    ("database schema changed outside the migrations directory", "migration"),
    ("staging deploy broke because a pending migration wasn't applied",
     "migration"),
    # rate-limit cluster
    ("call the shipping rates API for all zones", "backoff"),
    ("hit the payments API endpoint until the quota ran out", "backoff"),
    ("the http client got too many requests responses from the quotes api",
     "backoff"),
    ("fetch exchange rates in a tight loop for many currencies", "backoff"),
    ("quota exceeded while syncing the product catalog", "backoff"),
    ("throttled by the api after six rapid requests", "backoff"),
    ("the api returned http 429 and we kept hammering it", "backoff"),
    # derived (no curated playbook) cluster
    ("render the monthly billing statement as a pdf", "subsetted"),
    ("export the q2 invoices into a pdf document", "subsetted"),
    ("attach receipts to the expense report pdf", "subsetted"),
]

# --- adversarial negatives --------------------------------------------------

NEGATIVE_QUERIES: List[str] = [
    "retry the flaky ui animation assertion",
    "refactor module structure into smaller files",
    "rename variables for readability",
    "add a dark mode toggle to the settings page",
    "write docstrings for public functions",
    "upgrade eslint config to the flat format",
    "remove console log statements from the frontend",
    "split this component into two files",
    "translate the onboarding copy to german",
    "set up prettier formatting rules",
    "fix typo in contributing guide",
    "benchmark sorting algorithm implementations",
    "clean up unused imports across the project",
    "add keyboard shortcuts for undo redo",
    "update copyright year in footer",
    "configure git aliases for common commands",
    "write release notes for version two point one",
    "mock the file system in unit tests",
    "compress screenshots before uploading assets",
    "document environment variables in readme",
]


def _marker_in(hit, marker: str) -> bool:
    r = hit.reminder
    return (marker in r.recommended_action.lower()
            or marker in r.description.lower())


def evaluate(service, threshold: float, top_k: int = 3) -> Dict[str, float]:
    """Score `service` against the labeled set at a given threshold."""
    tp = fp = fn = 0
    top1_correct = 0
    for query, marker in POSITIVE_QUERIES:
        hits = service.query(query, top_k=top_k, threshold=threshold)
        correct = [h for h in hits if _marker_in(h, marker)]
        if correct:
            tp += 1
            if hits and hits[0] is correct[0]:
                top1_correct += 1
        elif hits:
            fp += 1          # answered, but with the wrong reminder
            fn += 1          # ...so the right one was effectively missed
        else:
            fn += 1          # silence on a relevant query
    neg_fp = 0
    for query in NEGATIVE_QUERIES:
        if service.query(query, top_k=top_k, threshold=threshold):
            neg_fp += 1
    fp += neg_fp
    tn = len(NEGATIVE_QUERIES) - neg_fp
    total_pos = len(POSITIVE_QUERIES)
    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / total_pos,
        "false_positive_rate": neg_fp / max(1, len(NEGATIVE_QUERIES)),
        "top1_accuracy": top1_correct / total_pos,
    }


def sweep(service, thresholds=None, top_k: int = 3) -> List[Dict[str, float]]:
    """Threshold selection over the labeled set (audit trail for 0.45)."""
    thresholds = thresholds or [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    return [evaluate(service, t, top_k=top_k) for t in thresholds]


def format_report(rows: List[Dict[str, float]]) -> str:
    head = (f"{'thresh':>6} {'P':>6} {'R':>6} {'FPR':>6} {'top1':>6} "
            f"{'TP':>3} {'FP':>3} {'FN':>3}")
    lines = [head, "-" * len(head)]
    for r in rows:
        lines.append(
            f"{r['threshold']:>6.2f} {r['precision']:>6.2f} "
            f"{r['recall']:>6.2f} {r['false_positive_rate']:>6.2f} "
            f"{r['top1_accuracy']:>6.2f} "
            f"{r['tp']:>3} {r['fp']:>3} {r['fn']:>3}")
    return "\n".join(lines)
