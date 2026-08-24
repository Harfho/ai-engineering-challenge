#!/usr/bin/env python3
"""Reproducible end-to-end demo of the reminder system.

Run from this directory (or the repo root):
    PYTHONPATH=src python3 examples/run_demo.py

Steps:
 1. Ingest data/sample_logs.jsonl into a fresh in-memory store
    (one malformed line is deliberately included to show robustness).
 2. Identify errors, cluster recurring patterns, generate reminders.
 3. Simulate a NEW user request that resembles past failures and show
    that only the applicable reminder is returned, ranked.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from reminder_system.pipeline import Pipeline          # noqa: E402
from reminder_system.store import Store                # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample_logs.jsonl"


def main() -> None:
    print("=" * 72)
    print("REMINDER SYSTEM DEMO — logs in, contextual reminders out")
    print("=" * 72)

    pipeline = Pipeline(Store(":memory:"))
    stats = pipeline.ingest_logs(SAMPLE)
    print(f"\n[1] Ingested {stats.logs_ingested} log entries "
          f"({len(stats.ingestion_problems)} malformed line(s) skipped)")

    stats = pipeline.build_reminders()
    print(f"[2] Identified {stats.error_events} error events "
          f"-> {stats.patterns_found} recurring patterns "
          f"-> {stats.reminders_built} reminders\n")

    print("[3] Learned reminder library:")
    for r in pipeline.service.list_reminders():
        print(f"    {r.reminder_id}  freq={r.frequency} conf={r.confidence}")
        print(f"      triggers : {', '.join(r.trigger_context)}")
        print(f"      issue    : {r.description}")
        print(f"      action   : {r.recommended_action}")
        print(f"      evidence : log rows {r.evidence_log_ids}")

    queries = [
        "I need to add a new column to the users table for email preferences",
        "call the shipping rates API for all zones in one go",
        "refactor the notification module into smaller classes",
    ]
    print("\n[4] Contextual retrieval on NEW requests:\n")
    for q in queries:
        hits = pipeline.service.query(q)
        print(f"  > \"{q}\"")
        if not hits:
            print("    (no applicable reminder — silence is correct)")
            continue
        top = hits[0]
        print(f"    -> {top.reminder.reminder_id} "
              f"(relevance {top.relevance:.2f}, matched: {top.matched_on})")
        print(f"       ACTION: {top.reminder.recommended_action}")
        if len(hits) > 1:
            print(f"       (+{len(hits)-1} weaker match(es) suppressed below threshold)")
    print("\nDemo complete.")


if __name__ == "__main__":
    main()
