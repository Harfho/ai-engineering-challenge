# Sources — Challenge 2 (v2)

Selection rule: primary documents (vendor policy pages, court reporting,
the original benchmark papers) over commentary; practitioner numbers used
only for direction, never precise magnitudes.

## Primary sources

- **[S1] OpenAI Deprecations page** (developers.openai.com/api/docs/deprecations),
  accessed Aug 2026. Vendor's own log: Assistants API sunset (Aug 26, 2026),
  Evals platform deprecation (announced Jun 3, 2026), Agent Builder
  deprecation, Sora API exit (Sep 24, 2026, no successor listed), GPT Image
  removals. Used for: bottleneck 1 evidence.
- **[S2] "Model Deprecations: An API Sunset Survival Playbook"**, Digital
  Applied, Jul 30, 2026. Normalizes four vendors' notice periods into one
  table from vendor policy pages; documents Anthropic's observed 60–62-day
  windows vs written floor, the temperature/top_p/top_k parameter break on
  Opus 4.7+, the Bedrock/Vertex reseller carve-out, and absence of any
  machine-readable feed. Trade analysis built entirely from primary pages.
- **[S3] Anthropic "Model Deprecations" & "Deprecation Commitments" pages**
  (platform.claude.com / anthropic.com). The written 60-day floor and the
  weights-preservation commitment. Primary policy text.
- **[S11] Hsieh et al., "RULER: What's the Real Context Size of Your
  Long-Context Language Models?"** arXiv:2404.06654, COLM 2024 (NVIDIA).
  17 models, claimed-vs-effective gaps (LWM 1M→<4K; Yi-34B 200K→32K;
  GPT-4 128K→64K). Primary research.
- **[S12] Modarressi et al., "NoLiMa: Long-Context Evaluation Beyond
  Literal Matching"** arXiv:2502.05167, LMU Munich + Adobe Research, Feb
  2025. With lexical overlap removed, most models' effective length drops
  to ≤2K–8K despite 128K+ claims (Llama 3.3 70B: ~8K effective). Primary
  research.
- **[S13] Liu et al., "Lost in the Middle: How Language Models Use Long
  Contexts"** arXiv:2307.03172, TACL 2024. Position-shape of recall.
  Primary research.

## Court/market reporting

- **[S6] "Every AI Content Licensing Deal, Mapped (2023–2026)"**, LLM Pulse,
  Jul 9, 2026 — aggregator of reported deal values (News Corp–OpenAI $250M/5y,
  Meta–News Corp up to $50M/yr, Reddit ~$60M+$70M/yr); figures labeled
  *reported*, not confirmed by parties. Used for magnitude context only.
- **[S7] "AI Content Licensing Deals 2026: Full Tracker"**, The Brief Script,
  Jun 22, 2026 — deal count growth 12 (2023) → ~127 (mid-2026), ~$2B
  disclosed total; Anthropic Sept 2025 settlement (~$1.5B) and its ~$3,000/
  per-work reference-price effect. Aggregator; direction reliable, exact
  totals are floors not ceilings.
- **[S8] "Reddit's AI Data Licensing: Hidden Revenue and Legal Risk"**,
  Metric Duck, Dec 2025 — reads Reddit SEC filings directly: ~$130M/yr
  licensing ≈10% of revenue; litigation table (Reddit v. Anthropic;
  Reddit v. Perplexity; Getty judgment Nov 2025; NYT v. OpenAI active).
- **[S9] "Reddit sues AI giant Anthropic over content use"**, AFP/Straits
  Times, Jun 5, 2025 — alleged 100k+ post-agreement scrapes; dual strategy
  of licensing + suing confirmed by Reddit's own filings coverage.
- **[S10] eMarketer / Market Daily, Jul 23–24, 2026** — Reddit-Google $60M
  deal near expiration; renegotiation and possible access blocking under
  discussion. News reporting of ongoing events.

## Practitioner synthesis

- **[S4] N. Dave, "The True Cost of Running Enterprise LLMs in Production
  (2026 Data)"**, Mar 29, 2026 — prompt-regression cost per model update
  (40–200 prompts, 2–5 engineer-days, $5k–25k/quarter). Single
  practitioner's rates; treat as one data point for order of magnitude.
- **[S5] "LLM API Versioning and Migration"**, zro2.one technical guide —
  silent default-version updates changing output behavior; practitioner
  consensus framing ("every team that's been in production long enough").
- **[S14] "Effective Context Length: Why 1M-Token Windows Fall Short"**,
  acingai.com, Jun 21, 2026 — retrieval consumes 17–38% of full-window
  tokens; orders-of-magnitude cost gap at volume. Synthesis of published
  studies; ratios directional.

## Quality tiers and conflicts

| Tier | Sources | Rule applied |
|---|---|---|
| Primary (policy/paper/court) | S1, S3, S11, S12, S13 | facts cited as stated |
| Aggregator/news (reported figures) | S6, S7, S8, S9, S10 | labeled "reported"; direction yes, precision no |
| Practitioner (single-source costs) | S2*, S4, S5, S14 | order-of-magnitude only |

*S2 sits between tiers: trade write-up but computed strictly from primary
vendor pages; we spot-checked its Anthropic window arithmetic against S3.

Conflicts noted: licensing-deal values vary across trackers (e.g., Reddit–
OpenAI reported at "$70M estimated" vs "around $70M"); where trackers
disagree we quote ranges or omit. No source found that contradicts any of
the three bottleneck mechanisms; the closest counter-literature (long-
context capability improving year over year) is addressed in analysis.md's
counterargument sections.

## Deliberately excluded

The v1 first-pass sources (`archive/v1-first-pass/sources.md`) remain valid
for their claims but no longer back the headline selection. They document
that saturation/data-wall/inference-cost material is abundant and easily
found — which is exactly why it fails the brief's test.
