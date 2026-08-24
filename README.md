# ai-engineering-challenge

Solutions to a three-part technical hiring assessment: an authorized
security investigation, a research-backed analysis of AI development
bottlenecks, and a working reminder-system prototype.

| Challenge | Entry point | Status |
|-----------|-------------|--------|
| 1 — Server investigation (`185.146.233.222`, authorized) | [`challenge-1-server/ANSWERS.md`](challenge-1-server/ANSWERS.md) → `report.md` | Complete |
| 2 — Three bottlenecks no Big Player talks about | [`challenge-2-ai-bottlenecks/analysis.md`](challenge-2-ai-bottlenecks/analysis.md) | Complete |
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

## Headline results

**Challenge 1.** The server is a deliberately unbranded private
remote-administration endpoint (MEDIUM-HIGH confidence): exactly one TCP
listener (`22`, OpenSSH appearing current-generation), all other 65,534
ports silently dropped, zero CVEs flagged — independent passive intel
(Shodan InternetDB) agrees with our active scan exactly. No externally
verifiable exploitable vulnerability was identified within the assessment
scope (external, unauthenticated methodology; UDP not assessed). Four
findings recorded; every claim traces to a logged command.

**Challenge 2.** Selection filter: silence must be profitable, and an
executive saying it in a keynote must be unthinkable. The three that pass,
each analyzed against four questions (what · why it exists · why it worsens
at scale · why Big Players stay quiet):
**(1) Rented cognition** — the dependency and control asymmetry: a few
vendors unilaterally control models, interfaces, pricing, lifecycle, and
serving behavior for every independent AI product; 60-day deprecation
clocks and silent behavior changes are symptoms of dependence no contract
covers. **(2) The rights wall before the volume wall** — usable training
data acquired prices ($1.5B settlement → ~$3k/work reference floor) and
expiry dates (licensing deals up for renegotiation mid-2026) before it ever
ran out; the "running out of internet" debate is the decoy. **(3)
Effective-context collapse** — advertised windows of 128K–1M tokens vs
measured effective context of as little as ≤8K once lexical cheating is
removed (RULER, NoLiMa); nobody publishes the utilization curve.
Incentive arguments are labeled as interpretation throughout. First-pass
answer kept in `archive/v1-first-pass/`.

**Challenge 3.** Working prototype, Python stdlib only (zero dependencies):
logs in → failures detected deterministically → recurring patterns clustered
(≥2 occurrences across ≥2 sessions) → reminders generated into SQLite →
context-matched retrieval that stays silent when nothing applies. LLM
providers plug in behind an interface; `semantic_demo.py` proves enrichment
discovers patterns keyword rules cannot group. 21/21 offline tests pass.

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

All three challenges complete.
