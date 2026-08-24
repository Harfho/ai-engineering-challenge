# EXPLAINER — How the Reminder System Works

> Written for presenting/defending the project: plain language first,
> then depth, then likely questions with short answers.
> Read time: ~6 minutes.

---

## 1. The one-paragraph version

AI agents repeat the same mistakes across sessions — and nobody remembers
at the moment it matters. This system reads **historical interaction logs**,
finds failures that happened **again and again**, turns each recurring
failure into an **actionable reminder** stored in a machine-queryable
database, and later — when a new task starts — returns **only the reminder
that applies** to that task, ranked by relevance, with evidence. It runs on
pure Python (zero installs) and never *requires* any AI provider; AI models
are optional plug-ins that improve it, not enable it.

## 2. Why it doesn't exist off-the-shelf

Generic tools do pieces of this: log aggregators store events; RAG systems
retrieve documents; linters enforce static rules. None connect the loop:
*logs → discovered failure patterns → just-in-time contextual warnings*.
Existing "agent memory" products remember facts and preferences — they don't
learn **discipline** (recurring mistakes) automatically from history. That
gap is the whole point of the prototype.

## 3. The diagram

```
                ┌─────────────────────────────────────────────────┐
                │              OFFLINE LEARNING PATH               │
                │                                                  │
  logs.jsonl    │   ┌────────┐   ┌──────────────┐   ┌──────────┐   │
  (past agent ──┼──>│ INGEST │──>│ IDENTIFY     │──>│ CLUSTER  │   │
   sessions)    │   │ validate│  │ ERRORS       │   │ PATTERNS │   │
                │   │ per line│  │ deterministic│   │ ≥2x in   │   │
                │   └────────┘   │ detectors +  │   │ ≥2       │   │
                │                │ categories   │   │ sessions │   │
                │                └──────────────┘   └────┬─────┘   │
                │                                        ▼         │
                │                                   ┌───────────┐  │
                │                                   │ GENERATE  │  │
                │                                   │ REMINDERS │  │
                │                                   │ rule-table│  │
                │                                   │ actions + │  │
                │                                   │ evidence  │  │
                │                                   └─────┬─────┘  │
                ▼                                         ▼        │
        ┌──────────────┐   replace atomically     ┌─────────────┐  │
        │  raw LOGS    │<-------------------------| REMINDERS   |  │
        │  (append-only│                          │ (derived)   |  │
        └──────┬───────┘                          └──────┬──────┘  │
               │                                          │        │
               └───────────────┐          ┌───────────────┘        │
                               ▼          ▼                        │
                ┌─────────────────────────────────────────────────┐
                │              ONLINE QUERY PATH                   │
                │                                                  │
  new user ──>  │   "add a column to users table"                  │
  request      │          │                                       │
                │          ▼                                       │
                │   ┌──────────────────┐                           │
                │   │ RETRIEVE         │  tokenize → expand        │
                │   │ score vs every   │  (column→schema/migration)│
                │   │ reminder: TF-IDF │  → score → tanh → rank    │
                │   └────────┬─────────┘                           │
                │            ▼                                     │
                │   above threshold? ──no──> SILENCE (by design)   │
                │            │yes                                  │
                │            ▼                                     │
                │   top-k reminders + relevance + matched_on       │
                │   + recommended action + evidence log rows       │
                └─────────────────────────────────────────────────┘
```

## 4. A concrete walkthrough (the demo story)

The sample logs contain a real pattern: across several sessions, agents
altered database schema directly (`ALTER TABLE`, `CREATE INDEX`) instead of
writing migrations, and deploys kept failing ("schema drift", "missing
migration", "relation does not exist").

1. **Identify**: each failing row fires detectors (non-empty `error` field,
   HTTP status, failure vocabulary) → becomes an ErrorEvent with a cleaned
   message: `"deploy failed: missing migration for schema change <hash>"`.
2. **Categorize**: keyword rules tag it `[database_migration]` — crucial,
   because the same root cause appears as totally different sentences.
3. **Cluster**: all 7 migration-category events merge into ONE pattern
   spanning 6 sessions → passes the recurrence gate (≥2× in ≥2 sessions).
4. **Generate**: rule table maps the category to advice → *"Before altering
   database schema, check for and create a pending migration file…"*,
   confidence 0.95, evidence = the exact log rows.
5. **Retrieve**: weeks later a user types *"I want to add a column to the
   users table"* — no word in common with "migration"! Concept expansion
   bridges it: {column, table} → {schema, migration, database…}. Score 0.78
   after tanh calibration → reminder returned with `matched_on` showing
   exactly which concepts fired.

And the flip side: *"refactor the notification module"* matches nothing
→ empty response. **Silence is a feature**: a reminder system that nags on
weak associations gets ignored within a week.

## 5. Stage-by-stage: what and WHY

### Ingest (`ingest.py`)
Validates each JSONL line (required fields present); malformed lines are
skipped **and reported**, never fatal. *Why:* real logs are dirty; one bad
line shouldn't kill a batch, but you must know it happened.

### Error identification (`analysis.py`)
Deterministic detectors only: error field non-empty · result contains
failure vocabulary · HTTP status ≥ 400 · nonzero exit code. Messages get
normalized (`abc123`→`<hash>`, numbers→`<n>`) so the same failure shape
matches even when IDs differ. Each event records WHICH detector fired.
*Why deterministic:* detection must never depend on a paid API being up;
auditability requires knowing why something counted as an error.

### Categorization (`analysis.py`)
Small keyword-rule table assigns issue types: `database_migration`,
`api_rate_limit`, `authentication`, … An optional LLM may override/refine
the label. *Why rules first:* categories are the semantic backbone that
makes clustering robust (next stage); rules are inspectable and free.

### Clustering (`patterns.py`)
Two tiers: events sharing a category form one candidate group directly;
uncategorized events fall back to token-similarity clustering (weighted
Jaccard, single-linkage). Recurrence gate: frequency ≥ 2 **and**
distinct sessions ≥ 2. *Why category-first:* we tried pure lexical
clustering first — it FAILED: "schema drift detected" vs "relation does
not exist" scored 0.08–0.29 similarity despite being the same mistake.
Categories carry the meaning that word overlap misses. *Why the session
gate:* one bad afternoon must never become a permanent nag.

### Reminder generation (`reminders.py`)
Majority vote on member categories picks the action from a data table
(migration → "create pending migration before deploy"; rate limit →
"exponential backoff with jitter…"). Confidence = bounded function of
frequency and session spread, capped at **0.95** — nothing learned from
logs should claim certainty. Evidence links point at exact log rows.
*Why evidence links:* trust requires receipts; every warning can be traced
to the incidents that justify it.

### Retrieval (`retrieval.py`)
Score = TF-IDF-weighted overlap between query tokens and each reminder's
triggers (3× weight) + description + action text, PLUS concept-group
expansion at half weight (curated synonym sets), PLUS optional embedding
cosine. Final relevance = `tanh(score)` — bounded 0–1 regardless of query
length. Top-k returned above threshold 0.25. *Why expansion:* users say
"add a column", never "check migration discipline" — without the bridge,
the right reminder never fires (we measured 0.13 without it).
*Why tanh:* our first normalization divided by best-score × query length;
long natural requests diluted their own topical core below threshold.
tanh is monotonic, bounded, length-independent.

### Storage (`store.py`)
SQLite: `logs` table append-only (ground truth), `reminders` table fully
derived and regenerated atomically per build. *Why SQLite:* zero-ops,
ships with Python, SQL-inspectable, trivially resettable for tests.
*Why reminders are derived:* avoids stale-schema drift; recompute is cheap.

### API (`api.py`)
Stdlib HTTP server: `GET /health`, `GET /reminders`,
`POST /reminders/query {"context": "...", "top_k": 1–10}`.
Validation errors return 400/422 with explanations; hits include
`relevance` and `matched_on`. *Why stdlib:* brief prioritizes simple
reproducible setup — zero dependencies means `python3 -m` runs anywhere;
swapping to FastAPI touches only this file.

## 6. "Model-agnostic" — concretely

Two interfaces in `providers.py`:

```python
LLMProvider.analyze_error(raw_message, context) -> {"category", "summary"}
EmbeddingProvider.embed(text) -> vector
```

Shipped implementations are offline fallbacks (`NullLLM`, local hashing
embedder). Contract: providers may throw or return junk — the pipeline
catches and continues deterministically. Swapping in OpenAI/Anthropic/
local LLM = implement one class, pass one constructor argument, change
nothing else. AI can only ENRICH results (better categories, semantic
matching); it can never GATE them (detection/retrieval work with none).

## 7. Likely questions — short answers

**"How does it 'learn'?"**
It doesn't train anything. Learning = batch transformation: logs → error
events → clusters → reminder rows. Rebuild anytime; reminders regenerate
atomically.

**"What stops it from nagging about one-off glitches?"**
The recurrence gate: minimum 2 occurrences across minimum 2 distinct
sessions, plus confidence scaled by both.

**"Where is the automatic learning / semantic discovery?"**
Two layers. The shipped default is a **deterministic baseline**: detection,
categorization, clustering, and retrieval all work offline with rules —
this is what makes the MVP testable and reproducible. On top of that, the
system has a real **semantic enrichment seam**: pass any `LLMProvider` and
the LLM re-categorizes errors *including failures the keyword rules cannot
group*. This is demonstrated concretely in `examples/semantic_demo.py`:
with enrichment enabled, three paraphrased connection-drop failures ("lost
the db connection", "connection dropped during bulk update", "database
vanished halfway through") — which share no keywords and never cluster
deterministically — become one discovered pattern with an action rule and
retrievable triggers (0.83 relevance on a paraphrased query). Two provider
implementations ship in `providers.py`: `ScriptedLLM` (deterministic demo/
test mock) and `OpenAICompatLLM` (works with OpenAI, Ollama, vLLM, LM
Studio — any chat-completions endpoint). So: semantic discovery is not
theoretical; it is one constructor argument away, and the deterministic
path guarantees the system degrades gracefully without it.

**"Why not just use embeddings/RAG?"**
RAG retrieves documents; it doesn't discover *that a failure repeats*.
Also pure-embedding retrieval failed our paraphrase test offline and adds
network dependency — embeddings here are an optional quality upgrade, not
a dependency. (Hybrid scoring already includes an embedding cosine slot.)

**"How do you know retrieval works?"**
Tests assert behavior end-to-end: paraphrased queries rank the correct
reminder first; irrelevant queries return empty; top_k respected; results
survive a persistence roundtrip. 19 tests, all offline/deterministic.

**"What are its limits?"** (say these proactively — credibility)
Batch-only learning (no streaming updates) · category table maintenance
grows coverage · two distinct issues sharing one category would merge ·
keyword ceiling on open-vocabulary paraphrase until a real embedder is
plugged in · single-tenant API (no auth) by MVP scope.

**"How would you scale it?"**
Clustering is O(n²) in error count — fine to tens of thousands; beyond
that, pre-bucket by category (already done) or approximate NN. Retrieval
is O(reminders × tokens) — fine to hundreds of reminders; swap TF-IDF for
ANN index if thousands. Ingestion parallelizes trivially.

## 8. 30-second spoken summary

"It mines an agent's past failures for lessons. It detects errors with
deterministic rules, groups repeats of the same mistake even when phrased
differently, requires a mistake to recur across sessions before it earns a
reminder, stores those reminders with evidence links in SQLite, and at
query time returns only the reminder relevant to the current task — ranked,
explained, and silent when nothing applies. It needs no AI provider to
work; providers plug in behind interfaces to make it smarter."
