# Sources

> Accessed: 2026-08-24 (UTC). All URLs retrieved and excerpted via live
> search during this assessment. Quality tiers: **[P]** primary research /
> technical report, **[R]** reputable industry analysis or established
> trade press, **[S]** secondary commentary (used only to corroborate).

## Bottleneck A — Evaluation & verification

- [A1] Stanford HAI. "AI Index Report 2026, Chapter 2: Technical Performance." 2026.
  <https://hai.stanford.edu/assets/files/ai_index_report_2026_chapter_2_technical.pdf> [P]
  Key evidence: evaluations "being outpaced by the progress they were built
  to measure"; benchmarks saturate in months; top-6 labs within ~25 Elo
  points; AI agents "still fail roughly one in three attempts"; competitive
  pressure shifting toward cost/reliability.

- [A2] "When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation."
  arXiv:2602.16763, 2026. <https://arxiv.org/html/2602.16763v1> [P]
  Key evidence: of 60 LLM benchmarks from major developers, nearly half are
  saturated; private (hidden) test data shows *no* protective effect;
  expert-curated benchmarks resist saturation better than crowdsourced.

- [A3] "Measuring Five-Nines Reliability: Sample-Efficient LLM Evaluation in
  Saturated Benchmarks." arXiv:2605.11209, May 2026.
  <https://arxiv.org/pdf/2605.11209v1> [P]
  Key evidence: models all exceeding 99.9% benchmark accuracy differ by up to
  2.4× in measured failure rates; distinguishing 99.9% vs 99.999% reliability
  requires prohibitively large samples — statistical floor under headline metrics.

- [A4] Wall, A. "The Evaluation Crisis: Why AI Benchmarks Are the New
  Bottleneck (and How to Solve It)." INFORMS Analytics Magazine, Apr 2025.
  <https://pubsonline.informs.org/do/10.1287/LYTX.2025.04.03/full/> [R]
  Key evidence: Informatica survey — ~two-thirds of companies still in GenAI
  pilots; 97% struggle to show business value; evaluation named the adoption
  blocker by Databricks CEO.

- [A5] EvalEval Coalition. "When AI Benchmarks Stop Measuring Progress." Jun 2026.
  <https://evalevalai.com/2026/06/30/saturation-blog/> [R]
  Key evidence: saturation = score gaps smaller than measurement uncertainty;
  independent saturation index across 60 benchmarks.

## Bottleneck B — High-quality training data exhaustion

- [B1] Villalobos, P., Ho, A., Besiroglu, T., Hobbhahn, M., Sevilla, J.
  "Will we run out of data? Limits of LLM scaling based on human-generated
  data." Epoch AI, 2024. <https://epoch.ai/blog/will-we-run-out-of-data-> 
  `limits-of-llm-scaling-based-on-human-generated-data` [P]
  Key evidence: effective stock of public human text ≈300T tokens (90% CI
  100T–1000T); fully utilized between 2026–2032; compute-optimal scaling hits
  the wall at ~5e28 FLOP ≈ 2028; overtraining pulls dates earlier (5× → 2027,
  100× → 2025); revision history documented (2022 estimate said before 2026).

- [B2] Villalobos et al. "Will we run out of ML data? Evidence from projecting
  dataset size trends." Epoch AI / arXiv:2211.04325, Nov 2022.
  <https://arxiv.org/abs/2211.04325> [P]
  Key evidence: original tiered exhaustion estimates — high-quality language
  before ~2026; low-quality language 2030–2050; image 2030–2060.

- [B3] "The AI revolution is running out of data. What can researchers do?"
  Nature news feature, Dec 2024. <https://www.nature.com/articles/d41586-024-03990-2> [R]
  Key evidence: mainstream scientific coverage legitimizing the data-wall
  projection; surveys researcher responses (synthetic data, efficiency).

## Bottleneck C — Inference economics

- [C1] Zylos Research. "Inference Economics: AI Agent Compute Markets in 2026."
  Apr 2026. <https://zylos.ai/en/research/2026-04-13-inference-economics-ai-agent-compute-markets/> [R]
  Key evidence: inference ≈85% of enterprise AI budget and ≈2/3 of global AI
  compute spend; the "Inference Flip" (cumulative inference spend passing
  training) occurred early 2026; API prices fell ~80% YoY while total spend
  rose (Jevons dynamics); Gartner warns per-token deflation ≠ total-bill
  deflation; IDC: orgs underestimate AI infra cost by up to 30%.

- [C2] Vista Equity Partners. "Understanding Inference and the Economics of
  Enterprise AI." Jul 2026. <https://www.vistaequitypartners.com/insights/inference-economics-enterprise-ai> [R]
  Key evidence: Deloitte survey — many enterprises exceed 10B tokens/month;
  share expecting >100B projected to triple by 2028; average enterprise model-
  usage spend ≈$7M in 2025 (~3× prior year); agentic tasks consume 5–30× more
  tokens than single-shot requests; frontier pricing spans $1–75 per M tokens.

- [C3] TechAhead. "Inference Cost Explosion: Why AI Agent Economics Break At
  Scale." Aug 2026. <https://www.techaheadcorp.com/blog/inference-cost-explosion/> [S]
  Key evidence (corroborating): unit economics invert at 500–5K users;
  loops/retries multiply token consumption 3–7× ("token tsunamis"); Deloitte
  Q4 2025: enterprise AI gross margins 40%→33%; inference = 80–90% of agentic
  system spend.

- [C4] AI Automation Global. "AI Inference Cost Crisis 2026: Why OpenAI Loses
  $1.35 Per Dollar Earned." Mar 2026.
  <https://aiautomationglobal.com/blog/ai-inference-cost-crisis-openai-economics-2026> [S]
  Key evidence (corroborating, unverified figures): OpenAI ≈$3.7B revenue vs
  ≈$5B losses in 2025 attributed largely to inference costs.

## Cross-cutting

- [X1] Epoch AI. "The Rising Costs of Training Frontier AI Models." updated
  Oct 2025 (cited via C2). Training-cost growth context. [P]

## Source-quality notes & conflicts

- B1 revises B2 upward (better filtering + multi-epoch use expanded effective
  stock 2–5×). We treat B1 as current best estimate and note the revision as
  evidence the field's own uncertainty is high — not as grounds for dismissal.
- C4's OpenAI loss figures are journalistic estimates without filings; used
  only directionally.
- Amodei's stated ~10% probability that data scarcity materially stalls
  progress (reported in secondary coverage of B1) is recorded as a
  dissenting expert judgment, addressed in analysis.md §B.
