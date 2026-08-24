# Challenge 2 — AI Development Bottlenecks (v2)

**Objective:** the three biggest bottlenecks in AI development that no Big
Player talks about *because none of them want to* — name them, explain why
they exist.

**Status:** Complete. v2 supersedes `archive/v1-first-pass/` after
reviewer feedback: the first pass answered with famous problems (benchmark
saturation, data exhaustion, inference costs). Real issues — but findable
on page one of any search, which fails the brief's actual test.

## The selection filter used

A bottleneck qualifies only if: (1) structural, not a tooling gap;
(2) silence is profitable for the big labs; (3) **the keynote test** —
an executive saying it plainly on stage must be unthinkable.

## The three

1. **Model churn: AI infrastructure with no stability guarantees** —
   60–62-day deprecation windows, APIs retired within a year of launch,
   parameters that break silently, no LTS tier from anyone. Facts sit in
   vendor changelogs; saying "our models are fashion, not Postgres" is
   unsayable.
2. **The rights wall arrived before the volume wall** — usable training
   data got a price ($1.5B settlement → ~$3k/work reference floor) and
   expiry dates (Reddit's deals up for renegotiation mid-2026) before it
   ever ran out. The public debate about "running out of internet" is the
   decoy; the action is in court dockets and contracts nobody keynotes.
3. **Effective-context collapse** — spec-sheet windows (128K–1M) vs
   measured effective context (often ≤8K once lexical cheating is removed:
   RULER, NoLiMa). Vendors publish the window number and never the
   reliability curve; per-token pricing bills the unusable region too.

## Files

- `analysis.md` — full case per bottleneck: evidence → why structural →
  counterargument + falsifier → why they stay quiet (labeled as our
  interpretation) → what would help
- `comparison.md` — leverage ranking + how the three compound
- `sources.md` — 14 sources, quality-tiered, conflicts noted; primary
  documents (vendor pages, papers, court/SEC reporting) over commentary
- `archive/v1-first-pass/` — the superseded first pass, kept deliberately:
  it documents the re-evaluation rather than hiding it

## Method

Hypotheses generated broadly → filtered by the three-part test above →
research pass privileging primary documents → adversarial pass per
bottleneck (strongest counterargument + explicit falsifier) → incentive
arguments written as labeled interpretation, never as fact.
