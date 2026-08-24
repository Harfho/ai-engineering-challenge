# Architecture — Model-Agnostic Reminder System

> STATUS: final. This document reflects the system as implemented and
> tested (36/36 offline tests, reproducible demo, measured retrieval
> quality). Where a design changed during development, the *reason* is
> recorded — dead ends are evidence.

## 1. Components

| Component | File | Responsibility |
|---|---|---|
| Ingest | `ingest.py` | Load JSONL/JSON logs, validate required fields, coerce bad metadata, report malformed lines without aborting |
| Error identifier | `analysis.py` | Detect failures via deterministic signals; normalize messages (ids/paths/numbers → placeholders); assign category |
| Pattern extractor | `patterns.py` | Cluster error events into recurring patterns; derive trigger tokens; enforce recurrence thresholds |
| Reminder generator | `reminders.py` | Turn patterns into actionable reminders via rule tables; compute confidence; link evidence |
| Store | `store.py` | SQLite persistence: append-only `logs`, derived-and-regenerated `reminders` |
| Retriever / service | `retrieval.py` | Score new task context against reminder library; return top-k above threshold with explanations |
| API | `api.py` | Stdlib HTTP server exposing health / list / query |
| Providers | `providers.py` | The model-agnostic boundary: `LLMProvider`, `EmbeddingProvider` ABCs + offline fallbacks |

## 2. Data flow

```
logs.jsonl ─> ingest ─> LogEntry rows ─> identify_errors ─> ErrorEvents
                 │           (SQLite)         (detectors +        │
                 │                             categories)        ▼
                 │                                        extract_patterns
                 │                                     (category-first groups,
                 │                                      lexical fallback)
                 │                                              │
                 ▼                                              ▼
          raw history                        generate_reminders ─> Reminder rows
                                                                        │
   "add a column to users" ──────> Retriever <──────────────────────────┘
                                    │ TF-IDF + concept expansion
                                    │ + optional embedding cosine
                                    ▼
                     [{reminder, relevance, matched_on}] or silence
```

Batch direction (left) runs once per ingestion/build cycle. Query direction
(right) is per user request and never mutates state.

## 3. Storage

**Decision: single SQLite file** (`store.py`). Tables:

- `logs(row_id PK, session_id, timestamp, agent, user_request, agent_action,
  result, error, metadata JSON)` — append-only ground truth.
- `reminders(reminder_id PK, description, trigger_context JSON,
  recommended_action, evidence_log_ids JSON, confidence, frequency,
  created_at, source_pattern_id)` — fully derived data, replaced atomically
  on every build (`replace_reminders` wraps DELETE+INSERT in one transaction).

Justification: zero-operations, ships in stdlib, trivially resettable in
tests, SQL-inspectable for debugging. Write pattern is batch-insert/read-many.
Rejected: Postgres (ops burden, no benefit at MVP scale), flat files (no
indexed queries, no atomic regeneration).

Errors/patterns are **not** persisted: they are cheap to recompute from logs
and keeping them derived avoids schema drift between pipeline versions.

## 4. Processing pipeline

Stages (orchestrated by `pipeline.Pipeline`):

1. **Ingest** — validation only; one bad line skips that line, not the run.
2. **Identify errors** — deterministic detectors:
   `error_field`, failure vocabulary in result, `metadata.status ≥ 400`,
   nonzero exit codes, combined-keyword fallback. Each event records which
   signals fired (auditable).
3. **Categorize** (deterministic) — keyword rules map messages to issue
   types (`database_migration`, `api_rate_limit`, …). An injected LLM may
   override/refine the category but can *never suppress detection*: if the
   provider throws or returns junk, the deterministic path still produced an
   event. This ordering is the core of "model-agnostic": AI is an enhancer,
   not a dependency.
4. **Cluster patterns** — see §5a below for the algorithm and its evolution.
5. **Generate reminders** — action chosen by majority vote over member
   categories against `CATEGORY_ACTIONS`; confidence = bounded function of
   frequency and session spread (capped at 0.95 — nothing learned from logs
   should ever claim certainty); evidence = member log row ids.

## 5a. Clustering: what we tried and why category-first won

First implementation: pure lexical clustering (weighted token-Jaccard,
single linkage). It failed exactly where it matters: the same root cause
phrased differently ("schema drift detected", "relation does not exist",
"missing migration") scored pairwise similarity 0.08–0.29 — far below any
safe merge threshold, while risking false merges of unrelated failures if
the threshold were simply lowered. Lexical overlap cannot bridge paraphrase.

Second implementation (shipped): **category-first grouping**. Events sharing
a deterministic category form one candidate pattern directly; only
uncategorized events fall back to lexical clustering. Rationale: the
category rules are already the system's semantic prior — using them for
grouping costs nothing extra and produces stable, explainable clusters.
Trade-off accepted: two genuinely distinct issues sharing a category would
merge (mitigation: keep categories narrow; sub-splitting can be added later).

Recurrence gates: ≥ `min_frequency` (2) occurrences across ≥ `min_sessions`
(2) sessions. A single bad afternoon must never become a permanent nag.

Trigger tokens: tokens present in ≥60% of cluster members (after light
plural-stemming), most frequent first — the stable shape of the failure,
later used by retrieval.

## 5b. Retrieval strategy

**Shipped after recalibration: gated evidence matching** (second pivot — see
below for the first):

- Matching evidence comes only from a reminder's triggers + description.
  Action text is excluded: every action contains generic verbs ("retry",
  "check"), which let unrelated queries match any reminder through its
  advice boilerplate.
- A candidate needs an evidence pathway: ≥1 specific token shared with
  triggers/description, OR ≥2 distinct concept-group seeds (column+table ⇒
  schema work). Generic process vocabulary ("retry", "request", "page") can
  seed expansion but never counts as direct evidence.
- Concept-group expansion applies only to approved candidates, capped at two
  tokens by IDF weight — one ambiguous word cannot drag in a whole topic.
- Relevance = `min(cap, M / (M + 1.4))` where M combines direct TF-IDF mass,
  capped expansion mass, and (only for direct matches) optional embedding
  cosine. The ratio form keeps scores separated instead of saturating near
  1.0; expansion-only matches are capped at 0.78 so they can't outrank real
  evidence. Threshold default 0.45.
- Calibrated on a labeled set in `evaluation.py`: 20 reviewer-style
  positive queries (each with an expected-reminder marker) + 20 adversarial
  negatives. Measured at the shipped threshold: precision 1.00, recall
  1.00, FPR 0.00, top-1 accuracy 1.00; the sweep shows the same result
  holds across 0.30–0.55 and degrades only at 0.60 — threshold selection is
  auditable (`examples/retrieval_eval.py`), not asserted. Floors from this
  set are enforced in the test suite so calibration cannot silently regress.

Retrieval **filters, it does not dump**: below-threshold matches return as
silence. A reminder system that interrupts on weak associations trains users
to ignore it — precision matters more than recall here.

*First pivot (history):* best-score normalization was replaced by `tanh`
because long natural-language requests diluted their own topical core
(observed: 8-token perfect match scored 0.13). *Second pivot:* adversarial
review showed `tanh(direct + expansion)` saturates the other way — an
animation question matched a rate-limit reminder at 0.997 through the word
"retry" alone, while score could not separate that from a true hit at 0.778.
The gated model above removes both failure modes rather than re-tuning
constants.

Rejected alternatives: pure embeddings (opaque, needs network/model),
pure keyword without gating (fires on advice boilerplate), LLM reranking per
query (non-deterministic, latency, cost — and unnecessary at library sizes
≤100s).

## 6. Model abstraction

```python
class LLMProvider(ABC):            # optional semantic enrichment
    def analyze_error(raw, context) -> {"category", "summary"}
    def author_lesson(samples) -> {"lesson", "action"} | None   # optional

class EmbeddingProvider(ABC):      # optional retrieval upgrade
    def embed(text) -> vector
```

Shipped fallbacks: `NullLLM` (no-op), `ScriptedLLM` (deterministic mock for
demos/tests — proves enrichment end-to-end without network), `HashingEmbedder`
(local, seeded, deterministic), plus `OpenAICompatLLM` (real provider for any
chat-completions endpoint: OpenAI, Ollama, vLLM, LM Studio). Selection is
constructor injection — no config files, no implicit network calls.
Contract: providers may throw; pipeline catches and falls back
deterministically. Swapping in a real model touches one class and one
argument, zero pipeline changes.

Reminder content is layered, most-specific-first: an authored lesson from
`author_lesson` if the provider supports it; otherwise the curated playbook
for known categories; otherwise text DERIVED from the pattern's own evidence
(frequency, sessions, top message variants) — so a novel recurring failure
never gets generic boilerplate. The enrichment seam is demonstrated in
`examples/semantic_demo.py`: with an LLM categorizer active, paraphrased
failures that share no keywords form patterns the rules-only baseline
cannot discover (3 → 4 patterns on the demo corpus).

## 7. API design

Stdlib `http.server` (ThreadingHTTPServer) over a thread-safe store: the
SQLite connection allows cross-thread use and every store operation runs
under a re-entrant lock. Zero-dependency rationale: brief prioritizes simple
reproducible setup; framework swap touches only `api.py`.

| Endpoint | Semantics |
|---|---|
| `GET /health` | liveness, `200 {"status":"ok"}` |
| `GET /reminders` | full current library |
| `POST /reminders/query` | body `{"context": str (required non-empty), "top_k": int 1–10 (default 3)}` |

Error semantics: malformed JSON → `400`; missing/empty `context` or invalid
`top_k` → `422` with explanation; unknown route → `404`. Response adds
per-hit `relevance` and `matched_on` so callers (and humans) can audit *why*
a reminder fired — machine-readable trust.

## 8. Testing strategy

36 tests, stdlib `unittest`, fully offline and deterministic:

- **Per stage**: ingest validation/coercion incl. whole-file JSON arrays,
  empty inputs, whitespace-only files; error identification incl.
  normalization stripping ids and contradictory-outcome resolution (a
  `success` result never becomes an error event, even with residual error
  text); clustering (recurrence gates, session spread, identical-failure
  clustering, near-duplicate wording); reminder field bounds + evidence
  integrity + action routing.
- **Adversarial regressions**: uncategorized events must not corrupt
  category-cluster counts (index-bug regression); a 20-query unrelated-
  request battery must fire nothing; direct matches must outrank expanded
  ones.
- **Measured retrieval quality**: the labeled set in `evaluation.py`
  enforced as floors (precision/recall ≥ 0.95, FPR = 0.00, top-1 ≥ 0.90)
  plus a plateau check that threshold 0.45 is not a knife edge.
- **Integration**: full pipeline on the sample corpus; SQLite persistence
  roundtrip (same reminders after reload).
- **API**: real HTTP over ephemeral port — health, query success, 422
  validation, 404 routing, and concurrent GET /reminders from 8 worker
  threads (thread-safety regression).

Determinism guarantee: no network, no randomness beyond uuid ids (excluded
from assertions), fixed sample data. Tests double as behavioral spec.

## 9. Trade-offs consciously accepted

1. **Batch-only learning** — reminders regenerate per build; no incremental
   streaming updates. Acceptable: learning signal arrives in log batches;
   rebuild is seconds at MVP scale.
2. **Category table maintenance** — coverage grows by editing
   `CATEGORIES`/`CATEGORY_ACTIONS` (data, reviewable in PRs). The LLM
   provider path exists precisely to relax this later without code changes.
3. **Coarse within-category merging** — two distinct issues sharing one
   category merge. Mitigated by narrow category definitions; revisit with
   sub-clustering if real corpora show collisions.
4. **Keyword retrieval ceiling** — concept expansion covers observed
   phrasings, not open-vocabulary paraphrase. The `EmbeddingProvider` seam
   is the designed upgrade path; shipping without it keeps tests offline.
5. **No auth/multi-tenancy** — out of MVP scope; the API layer isolates this
   concern cleanly behind `ReminderService`.
