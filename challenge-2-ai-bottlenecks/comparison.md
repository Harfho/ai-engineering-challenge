# Comparison — Which bottleneck matters most

| Dimension | 1 · Rented cognition (dependency asymmetry) | 2 · Rights wall | 3 · Effective-context collapse |
|---|---|---|---|
| Who pays today | every team in production (revalidation tax: ~2–5 eng-days per model update [S4]) | labs (deals + settlements) and, downstream, customers via pricing | anyone stuffing context (3–6× token spend vs retrieval [S14]) |
| Evidence quality | primary vendor logs [S1–S3] | court records + SEC filings [S7–S9] | peer-reviewed benchmarks [S11–S13] |
| Getting worse? | yes — cadence accelerating through 2026 [S1] | yes — price floors ratchet up per ruling | slowly improving per model generation; gap persists [S12] |
| Fixable by a startup? | partially (routing/calendars — already a product category) | no (needs courts or collectives) | partially (measurement tooling exists) |
| Fixable by the Big Players themselves? | only by accepting slower iteration | only by funding collective licensing | only by publishing curves that reset their own marketing |

## Ranking by leverage

**1st — Rented cognition.** Highest evidence certainty (the vendors' own
policy pages), broadest blast radius (every production team, every
procurement negotiation), and the cheapest unshipped fix in the industry
(a machine-readable deprecation feed). The gap between how cheap the fix
is and how absent it remains is itself evidence of the incentive.

**2nd — Rights wall.** Largest absolute stakes ($1.5B settlement as one
data point) and the hardest structural constraint — but an individual team
can do nothing about it, which lowers its practical leverage even though
its industry leverage is enormous.

**3rd — Effective-context collapse.** Most quantified (benchmarks exist)
and most survivable (RAG workarounds are known), so it burns steadily
rather than acutely — but it is the one where buyers can act *this week*:
measure effective context on your own tasks before trusting any spec sheet.

## How they compound

Rented cognition is the umbrella: vendors control lifecycle, pricing, and
serving behavior unilaterally. The rights wall shapes what those few
controllers can train on, pushing them toward proprietary flywheels that
raise switching costs — deepening the dependence. Context collapse
shapes how much of what customers pay for actually reasons, and since
serving behavior is vendor-controlled, buyers often can't even measure
it without building the tooling themselves. One ecosystem, three tax
lines, one payer: the independent builder.

Ranking orders them by *leverage*, not severity. Full reasoning per
bottleneck in [`analysis.md`](analysis.md).
