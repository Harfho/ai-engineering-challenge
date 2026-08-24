# Architecture overview

Per the assessment brief, detailed architecture lives with its challenge:

- **Challenge 3 (reminder system)**: [`challenge-3-reminder-system/docs/architecture.md`](../challenge-3-reminder-system/docs/architecture.md)
  — status: **implemented and tested** (21/21 offline tests; the document
  reflects the system as built, including design pivots and their reasons).
  Runnable prototype: see that challenge's `README.md` quick start.

Challenges 1 and 2 are analysis deliverables; their "architecture" is the
methodology in [`docs/methodology.md`](./methodology.md) plus per-challenge
plans in their `README.md` files.

## Repository-wide conventions

- Language: Python 3.12 (Challenge 3 implementation); Markdown everywhere else
- Evidence-first writing; speculation labeled as such
- Generated artifacts (DBs, caches, scan raw output containing sensitive data)
  are gitignored or redacted before commit
- Every phase ends with a commit whose message names the phase
