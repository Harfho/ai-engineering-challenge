# ai-engineering-challenge

Technical assessment — security investigation, AI systems analysis, and a model-agnostic context reminder prototype.

Solutions to a three-part technical hiring assessment.

| Challenge | Deliverable | Status |
|-----------|-------------|--------|
| 1 — Server investigation (`185.146.233.222`, authorized) | `challenge-1-server/report.md` | Not started (Phase 2) |
| 2 — Three under-emphasized AI development bottlenecks | `challenge-2-ai-bottlenecks/analysis.md` | Not started (Phase 3) |
| 3 — Model-agnostic AI reminder system prototype | `challenge-3-reminder-system/` | Not started (Phase 4) |

## Structure

```
├── README.md            this file
├── LICENSE              MIT
├── docs/
│   ├── methodology.md   evidence rules, recording format, redaction policy
│   └── architecture.md  pointers + repo conventions
├── challenge-1-server/          authorized security assessment (report + evidence)
├── challenge-2-ai-bottlenecks/  researched analysis of three structural bottlenecks
└── challenge-3-reminder-system/ working prototype + tests + reproducible demo
```

## How to read this repository

- Start with `docs/methodology.md` — it defines how claims are supported.
- Each challenge directory is self-contained with its own README.
- Claims in reports are separated from evidence; speculation is labeled.

## Reproducibility

- Challenge 1: every command is recorded with rationale and output excerpts;
  committed artifacts are redacted per policy but preserve reasoning chains.
- Challenge 2: sources are listed with full references; primary sources
  preferred over press coverage.
- Challenge 3: `pip install -r requirements.txt && python -m ...` (exact
  commands finalized in Phase 4); tests runnable offline via deterministic
  local fallbacks.

## Status

Phase 1 (repository setup) complete. Phases 2–5 pending.
See `FINAL_REVIEW.md` (to be produced in Phase 5).
