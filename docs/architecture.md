# Architecture overview

Per the assessment brief, detailed architecture lives with its challenge:

- **Challenge 3 (reminder system)**: [`challenge-3-reminder-system/docs/architecture.md`](../challenge-3-reminder-system/docs/architecture.md)
  — status: *skeleton, to be finalized in Phase 4 before implementation*.

Challenges 1 and 2 are analysis deliverables; their "architecture" is the
methodology in [`docs/methodology.md`](./methodology.md) plus per-challenge
plans in their `README.md` files.

## Repository-wide conventions

- Language: Python 3.12 (Challenge 3 implementation); Markdown everywhere else
- Evidence-first writing; speculation labeled as such
- Generated artifacts (DBs, caches, scan raw output containing sensitive data)
  are gitignored or redacted before commit
- Every phase ends with a commit whose message names the phase
