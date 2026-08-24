# Challenge 2 — AI Development Bottlenecks

**Objective:** Identify and defend the three biggest bottlenecks in AI
development that major companies have incentives **not** to emphasize publicly.
**Status:** Not started — Phase 3.

## Plan

1. **Hypothesis generation** — list candidate bottlenecks from engineering
   knowledge; explicitly labeled hypotheses, not conclusions.
2. **Research pass** — for each candidate: academic papers, technical reports,
   engineering blogs/primary docs. Recorded in `sources.md` with full references.
3. **Selection** — pick three by criteria: (a) structural (not a tooling gap),
   (b) economically rooted (why incentives suppress discussion),
   (c) evidence available from primary sources.
4. **Adversarial pass** — write the strongest counterargument to each selection;
   keep it in `analysis.md` §Counterarguments.
5. **Write-up** — `analysis.md` (exec summary + deep dives), `comparison.md`
   (comparison table), `sources.md`.

## Candidate hypotheses (to be validated or discarded in Phase 3)

> These are starting points recorded deliberately as **hypotheses**.
> Research may replace any of them.

- H1: Evaluation is the actual bottleneck (benchmarks saturate/mislead;
  capability claims rest on weak measurement).
- H2: Data exhaustion — high-quality human-generated training data is running
  out faster than compute scaling remains useful; synthetic data has known
  degradation risks.
- H3: Inference economics — cost/latency/energy of serving frontier models
  constrains product design more than model quality does.
- H4: Alignment/reliability gap — non-determinism and unverifiable reasoning
  block deployment in high-stakes domains regardless of raw capability.
- H5: Organizational debt — human review, liability, and process constraints,
  not model capability, gate real-world automation.

## Deliverables

- `analysis.md` — exec summary, per-bottleneck analysis (10 required elements each), counterarguments, conclusion
- `comparison.md` — cross-bottleneck comparison table
- `sources.md` — full reference list with source-quality annotations
