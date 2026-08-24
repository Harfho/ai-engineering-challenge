# Challenge 2 — AI Development Bottlenecks

**Objective:** Identify and defend the three biggest bottlenecks in AI
development that major companies have incentives **not** to emphasize publicly.
**Status:** Complete — see `analysis.md`, `comparison.md`, `sources.md`.

## Selected bottlenecks

1. **The evaluation & verification gap** — measurement infrastructure is
   shrinking relative to capability; benchmarks saturate below noise; the
   statistical floor on reliability measurement blocks certification.
   (Validates H1; absorbs part of H4 — non-determinism matters because it
   cannot yet be *measured* at deployment tolerances.)
2. **High-quality training data exhaustion** — ~300T effective tokens of
   public human text vs superlinear demand; wall window 2026–2032, pulled
   earlier by inference-driven overtraining. (H2, with the inference
   coupling made explicit.)
3. **Inference economics** — serving passed training as the cost center
   ("Inference Flip", early 2026); agentic token multiplication inverts unit
   economics before PMF. (H3.)

H4 and H5 were not discarded so much as distributed: H4's measurable core
folds into #1, its governance half into organizational practice beyond this
brief's scope; H5 (organizational debt) was ranked fourth — real, but better
documented elsewhere and less suppressed by corporate incentives than the
three selected.

## Method

1. **Hypothesis generation** — five candidates listed up front as hypotheses.
2. **Research pass** — primary research (Epoch AI, arXiv saturation/reliability
   studies), established analysis (Stanford AI Index 2026, Nature, Deloitte/
   Vista survey data), corroborating trade press. Full annotated list with
   quality tiers and conflict notes: `sources.md`.
3. **Selection criteria** — structural (not a tooling gap), economically
   rooted (incentives suppress discussion), evidence available from primary
   sources.
4. **Adversarial pass** — strongest counterargument + explicit falsifier per
   bottleneck in `analysis.md` §Counterarguments.

## Deliverables

- `analysis.md` — exec summary, per-bottleneck analysis (10 required elements each), counterarguments, conclusion
- `comparison.md` — cross-bottleneck comparison table + ranking rationale
- `sources.md` — full reference list with source-quality annotations
