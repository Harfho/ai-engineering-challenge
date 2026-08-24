# Challenge 3 — Model-Agnostic AI Reminder System

**Objective:** working prototype that mines historical AI interaction logs for
recurring errors and serves context-relevant reminders back to agents through a
provider-independent API.
**Status:** Not started — architecture doc due at the start of Phase 4,
implementation after.

## Pipeline (required by brief)

```
logs → error identification → pattern extraction → reminder generation
     → SQLite storage → context matching → agent-facing API
```

## Design commitments (initial; revisited in the architecture doc)

- **Language/stack:** Python 3.12, stdlib-first; heavy dependencies only with a
  concrete justification written down
- **Storage:** SQLite (acceptable per brief for MVP; justified by zero-ops,
  single-file, queryable via SQL)
- **Model independence:** every LLM/embedding call behind an abstract
  `Provider` interface; deterministic local fallback so tests run offline
- **Retrieval:** context matching must filter/rank, not dump all reminders
  (candidate approaches compared in the architecture doc)
- **API:** HTTP JSON endpoint(s) like `POST /reminders/query`
- **Tests:** ingestion, extraction, patterns, persistence, retrieval, API,
  edge cases — runnable offline in CI-style fashion

## Deliverables

- `docs/architecture.md` (components, data flow, trade-offs) — before code
- `src/`, `tests/`, `examples/` (reproducible demo), `data/` (realistic sample logs)
- `requirements.txt`

## Non-goals (MVP)

No k8s/queues/vector DBs unless justified; no multi-user auth; no realtime
streaming ingestion.
