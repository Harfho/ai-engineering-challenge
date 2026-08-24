#!/usr/bin/env python3
"""Demonstrates SEMANTIC ENRICHMENT: the same logs, but with an LLM
provider (deterministic mock) enriching error analysis.

What changes vs. the plain demo:
 - LLM re-categorizes errors, including ones the keyword rules MISSED
   (e.g., a paraphrased failure like 'we lost the database connection
   mid-request' that contains neither 'migration' nor 'timeout').
 - LLM-written summaries make reminders human-readable.
 - A NEW recurring pattern appears that deterministic rules alone
   could not group.

Swap ScriptedLLM for providers.OpenAICompatLLM pointed at any local or
remote model to get the same effect with a real LLM.

Run:  PYTHONPATH=src python3 examples/semantic_demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from reminder_system.pipeline import Pipeline          # noqa: E402
from reminder_system.providers import NullLLM, ScriptedLLM  # noqa: E402
from reminder_system.store import Store                # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Extra log lines whose failures the keyword rules CANNOT categorize:
EXTRA = [
    {"session_id": "s7-2026-08-14", "timestamp": "2026-08-14T09:00:00Z",
     "agent": "claude-code", "user_request": "sync inventory",
     "agent_action": "called warehouse sync job",
     "result": "failure", "error": "we lost the db connection mid-request "
     "and the sync aborted", "metadata": {}},
    {"session_id": "s8-2026-08-15", "timestamp": "2026-08-15T10:30:00Z",
     "agent": "aider", "user_request": "nightly stock update",
     "agent_action": "ran stock updater",
     "result": "failure", "error": "db connection dropped again during the "
     "bulk update; transaction rolled back", "metadata": {}},
    {"session_id": "s9-2026-08-16", "timestamp": "2026-08-16T08:10:00Z",
     "agent": "claude-code", "user_request": "reconcile orders",
     "agent_action": "order reconciliation batch",
     "result": "failure", "error": "connection to the database vanished "
     "halfway through reconciliation", "metadata": {}},
]


def write_extra(tmp):
    import json
    p = tmp / "extra_logs.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in EXTRA), encoding="utf-8")
    return p


def run(label, llm, tmp):
    store = Store(":memory:")
    pipeline = Pipeline(store, llm=llm)
    pipeline.ingest_logs(ROOT / "data" / "sample_logs.jsonl")
    pipeline.ingest_logs(write_extra(tmp))
    stats = pipeline.build_reminders()
    print(f"\n=== {label} ===")
    print(f"error events: {stats.error_events}, patterns: {stats.patterns_found}")
    for r in pipeline.service.list_reminders():
        print(f"  {r.reminder_id} freq={r.frequency} conf={r.confidence} :: {r.description[:90]}")
    return pipeline


def main():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        base = run("BASELINE — deterministic only (NullLLM)", NullLLM(), tmp)

        scripted = ScriptedLLM([
            ("lost the db connection",
             {"category": "database_connection_drop",
              "summary": "DB connection lost mid-operation"}),
            ("connection dropped",
             {"category": "database_connection_drop",
              "summary": "DB connection dropped during bulk update"}),
            ("connection to the database vanished",
             {"category": "database_connection_drop",
              "summary": "DB connection vanished mid-batch"}),
        ])
        enriched = run("ENRICHED — LLM semantic discovery (ScriptedLLM)",
                       scripted, tmp)

        print("\n--- what the LLM changed ---")
        base_ids = {r.source_pattern_id for r in base.service.list_reminders()}
        new = [r for r in enriched.service.list_reminders()
               if r.source_pattern_id not in base_ids]
        if new:
            r = new[0]
            print(f"NEW pattern discovered: {r.description}")
            print(f"  action: {r.recommended_action}")
            print("  (these three paraphrased failures share NO keywords;")
            print("   only semantic categorization could group them)")
        hits = enriched.service.query("sync data between systems overnight")
        print(f"\nretrieval after enrichment: {len(hits)} hit(s) for a "
              f"paraphrased connection-drop query")
        if hits:
            print(f"  -> {hits[0].reminder.reminder_id} "
                  f"rel={hits[0].relevance:.2f}")


if __name__ == "__main__":
    main()
