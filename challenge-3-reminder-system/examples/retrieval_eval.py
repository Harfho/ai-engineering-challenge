"""Retrieval evaluation report: precision / recall / FPR / top-k accuracy
of the reminder service on a labeled query set (evaluation.py).

Run:
    PYTHONPATH=src python3 examples/retrieval_eval.py

The threshold sweep doubles as the audit trail for the shipped default
(0.45): it must sit inside the plateau where recall is high and the
false-positive rate is zero — not on a knife edge.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from reminder_system.evaluation import format_report, sweep  # noqa: E402
from reminder_system.pipeline import Pipeline                # noqa: E402
from reminder_system.store import Store                      # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


def main():
    p = Pipeline(Store(":memory:"))
    p.ingest_logs(os.path.join(ROOT, "data", "sample_logs.jsonl"))
    p.build_reminders()
    print(f"labeled set: {len(p.service.list_reminders())} reminders, "
          f"threshold sweep (default 0.45):\n")
    print(format_report(sweep(p.service)))
    print("\npositive queries are reviewer-style relevance judgments; "
          "negatives are\nadversarial unrelated requests that must fire "
          "nothing.")


if __name__ == "__main__":
    main()
