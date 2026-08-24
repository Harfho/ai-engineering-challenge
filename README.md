# ai-engineering-challenge

Solutions to a three-part technical hiring assessment: an authorized
security investigation, a research-backed analysis of AI development
bottlenecks, and a working reminder-system prototype.

| Challenge | Entry point | Status |
|-----------|-------------|--------|
| 1 — Server investigation (`185.146.233.222`, authorized) | [`challenge-1-server/ANSWERS.md`](challenge-1-server/ANSWERS.md) → `report.md` | Complete |
| 2 — Three under-emphasized AI development bottlenecks | [`challenge-2-ai-bottlenecks/analysis.md`](challenge-2-ai-bottlenecks/analysis.md) | Complete |
| 3 — Model-agnostic AI reminder system prototype | [`challenge-3-reminder-system/README.md`](challenge-3-reminder-system/README.md) | Complete (21/21 tests) |

## Structure

```
├── README.md            this file
├── LICENSE              MIT
├── docs/
│   ├── methodology.md   evidence rules, recording format, redaction policy
│   └── architecture.md  pointers + repo conventions
├── challenge-1-server/          authorized security assessment (report + evidence)
├── challenge-2-ai-bottlenecks/  researched analysis of three structural bottlenecks
└── challenge-3-reminder-system/ working prototype + tests + reproducible demos
```

## How to read this repository

- Start with `docs/methodology.md` — it defines how claims are supported.
- Each challenge directory is self-contained with its own README.
- Claims in reports are separated from evidence; speculation is labeled.

## Reproducibility

- Challenge 1: every command is recorded with rationale and output excerpts;
  committed artifacts are redacted per policy but preserve reasoning chains.
- Challenge 2: sources are listed with full references in `sources.md`;
  primary sources preferred over press coverage.
- Challenge 3, no installs needed:
  ```bash
  cd challenge-3-reminder-system
  PYTHONPATH=src python3 -m unittest discover tests    # expect: OK (21 tests)
  PYTHONPATH=src python3 examples/run_demo.py          # deterministic demo
  PYTHONPATH=src python3 examples/semantic_demo.py     # LLM-enrichment demo
  ```

## Status

All three challenges complete. Summary of headline results on the
submission cover page (`assessment-submission/README.md`).
