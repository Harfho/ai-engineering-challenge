# Challenge 2 — AI Development Bottlenecks (v2)

**Objective:** the three biggest bottlenecks in AI development that no Big
Player talks about *because none of them want to* — name them, explain why
they exist.

**Status:** Complete. v3 supersedes v2's argument structure (kept in
`archive/v1-first-pass/`): every bottleneck now explicitly answers what /
why it exists / why it worsens at scale / why Big Players stay quiet.
v1→v2 history: the first pass answered with famous problems (benchmark
saturation, data exhaustion, inference costs). Real issues — but findable
on page one of any search, which fails the brief's actual test.

## The selection filter used

A bottleneck qualifies only if: (1) structural, not a tooling gap;
(2) silence is profitable for the big labs; (3) **the keynote test** —
an executive saying it plainly on stage must be unthinkable.

## The three

1. **Rented cognition: the dependency and control asymmetry** — a small
   number of vendors unilaterally control models, interfaces, pricing,
   lifecycle, and serving behavior for every independent AI product.
   Deprecation clocks are just the visible symptom; the structure is
   dependence without infrastructure obligations. Facts sit in vendor
   changelogs; saying "you depend on us beyond what any contract covers"
   is unsayable on stage.
2. **The rights wall arrived before the volume wall** — usable training
   data got a price ($1.5B settlement → ~$3k/work reference floor) and
   expiry dates (licensing deals up for renegotiation mid-2026) before it
   ever ran out. The "running out of internet" debate is the decoy; the
   action is in court dockets and contracts nobody keynotes.
3. **Effective-context collapse** — the industry measures context by
   window size while the operative quantity is how much reasoning survives
   as the window fills (RULER, NoLiMa). Vendors publish the window number,
   never the utilization curve; per-token pricing bills the unusable
   region too.

Each bottleneck in `analysis.md` answers the same four questions
explicitly: what is it · why does it exist · why does it get worse at
scale · why would a major AI company have an incentive not to emphasize
it (labeled as our interpretation).

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
