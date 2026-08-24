# Architecture — Model-Agnostic Reminder System

> STATUS: skeleton. To be **finalized before implementation** (Phase 4).
> Decisions below marked CANDIDATE until written up with trade-offs.

## 1. Components

> TODO: log ingester, error identifier, pattern extractor, reminder generator,
> reminder store, context retriever, API server — with responsibilities.

## 2. Data flow

> TODO: end-to-end diagram (text) from raw logs to served reminders.

## 3. Storage

CANDIDATE: single SQLite DB, tables: `logs`, `errors`, `patterns`,
`reminders`. Justification + schema to be written.

## 4. Processing pipeline

> TODO: batch pipeline stages; where LLM is optional vs deterministic.

## 5. Retrieval strategy

CANDIDATES to compare: keyword/BM25-style scoring over triggers; embedding
similarity behind provider interface; hybrid. Decision + trade-offs TODO.

## 6. Model abstraction

> TODO: `LLMProvider` / `EmbeddingProvider` interfaces; deterministic local
> fallback implementations; how provider selection is configured.

## 7. API design

> TODO: endpoints (`POST /reminders/query`, health), request/response schemas,
> error semantics.

## 8. Testing strategy

> TODO: unit tests per component + integration test of full pipeline +
> offline determinism guarantees.

## 9. Trade-offs

> TODO: what we accept by keeping the MVP simple (e.g., no incremental
> re-learning, coarse retrieval) and why that's acceptable for the brief.
