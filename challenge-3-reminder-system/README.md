# Challenge 3 — Contextual Reminder System (MVP)

Learns recurring failure patterns from past AI-agent session logs and
surfaces only the applicable lessons when a new, similar task begins.

**Model-agnostic by construction**: every vendor-specific capability sits
behind an interface (`LLMProvider`, `EmbeddingProvider`) with deterministic
offline fallbacks — the system runs fully without any AI provider.

## Quick start (zero dependencies)

Requires Python 3.12+ only. From this directory:

```bash
# 1. Run the test suite (stdlib unittest — no installs)
PYTHONPATH=src python3 -m unittest discover tests -v

# 2. Run the end-to-end demo
PYTHONPATH=src python3 examples/run_demo.py

# 3. Start the HTTP API on :8000
PYTHONPATH=src python3 -c "
from reminder_system.store import Store
from reminder_system.pipeline import Pipeline
from reminder_system.api import ApiServer
p = Pipeline(Store('reminders.db'))
p.ingest_logs('data/sample_logs.jsonl')
p.build_reminders()
ApiServer(p.service).serve_forever()
"

# in another terminal:
curl -s localhost:8000/health
curl -s localhost:8000/reminders | head -20
curl -s -X POST localhost:8000/reminders/query \
  -H 'Content-Type: application/json' \
  -d '{"context": "I need to add a column to the users table"}'
```

## Pipeline

```
logs.jsonl ──> ingest ──> identify errors ──> cluster patterns ──> generate reminders ──> SQLite
                 (validated)  (deterministic      (category-first +       (LLM-authored lesson
                               detectors +         lexical fallback)       > curated playbook >
                               optional LLM)                               evidence-derived text)
                                                                       │
new user request ────────────────────────────────────────> retrieval <──┘
                                               (gated TF-IDF + concept bridging
                                                + optional embeddings)
```

Key behaviors:
- **Errors are found by deterministic detectors** (error fields, failure
  vocabulary, HTTP status, exit codes). An LLM may enrich categories, never
  gate detection.
- **Patterns require recurrence**: ≥2 occurrences across ≥2 sessions.
  One bad session never becomes a nagging reminder.
- **Lessons are derived, not pre-written**: a brand-new recurring failure
  with no curated playbook still produces an honest reminder whose text is
  derived from its own evidence (frequency, sessions, most common message
  variants). With a provider attached, `LLMProvider.author_lesson` can write
  the lesson and action for ANY novel failure mode.
- **Retrieval requires evidence**: a candidate must share specific tokens
  with a reminder's triggers/description, or supply two distinct concept
  seeds (e.g. "column" + "table" ⇒ schema work). Generic advice vocabulary
  ("retry", "check") never matches, so unrelated requests get silence;
  matched reminders come ranked with bounded relevance scores and
  `matched_on` provenance. Calibrated against a 20-query adversarial
  battery in the test suite.
- **Every reminder is evidence-linked** to the log rows that justify it,
  and the store is safe under the threaded HTTP server.

## Layout

```
src/reminder_system/
  models.py       dataclasses shared by all stages
  store.py        SQLite persistence (thread-safe; logs append-only,
                  reminders derived)
  providers.py    LLMProvider / EmbeddingProvider + offline fallbacks
  ingest.py       JSONL/JSON loading, validation, malformed-line reporting
  analysis.py     error detection, normalization, categorization
  patterns.py     clustering (category-first; lexical fallback), triggers
  reminders.py    layered content: authored lesson > curated playbook >
                  evidence-derived fallback; confidence scoring
  retrieval.py    gated TF-IDF + concept bridging + optional embedding cosine
  pipeline.py     orchestration facade
  api.py          stdlib HTTP API (health / list / query)
data/sample_logs.jsonl   multi-session history incl. one malformed line and
                         failures outside every built-in category
examples/run_demo.py     reproducible end-to-end demo
tests/                   30 stdlib-unittest cases, fully offline
docs/architecture.md     design decisions & trade-offs (read this second)
```

## Extending

- Plug a real LLM: implement `analyze_error` and optionally
  `author_lesson` on `LLMProvider`, then pass it to `Pipeline(store,
  llm=...)`. See the docstring example in `providers.py`.
- Plug real embeddings: pass an `EmbeddingProvider` to `ReminderService`.
- New issue types: add entries to `analysis.CATEGORIES` +
  `reminders.CATEGORY_ACTIONS` (data, not code) — or attach a provider and
  let it author lessons for categories that don't exist yet.

## Known limits

- Retrieval is lexical + deterministic concept groups. It handles
  paraphrase only where a category rule or two-seed bridge applies;
  arbitrary phrasing needs a real embedding provider.
- The offline embedder (`HashingEmbedder`) captures token overlap, not
  deep semantics — reproducibility over quality.
- Sample history is small on purpose: it demonstrates behavior, it is not
  a benchmark.
