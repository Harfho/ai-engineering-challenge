# Comparison Table — AI Development Bottlenecks

> Selections: (1) Evaluation & verification gap, (2) High-quality training
> data exhaustion, (3) Inference economics. Evidence and sources in
> `analysis.md` / `sources.md`.

| Dimension | 1. Evaluation & verification gap | 2. Training-data exhaustion | 3. Inference economics |
|-----------|----------------------------------|-----------------------------|------------------------|
| **Category** | Technical + organizational | Technical + economic + legal | Economic |
| **Root cause** | Static benchmarks vs moving targets; statistical floor on measuring rare failures; eval produces no revenue so it's under-funded | Superlinear token demand vs fixed human-text stock; overtraining (driven by inference savings) accelerates depletion | Serving cost scales with every user/action; agentic loops multiply tokens non-linearly; Jevons effect absorbs price declines |
| **Why under-emphasized** | Leaderboards make headlines; measurement failure is invisible until deployment; "harder benchmark" news reads as progress, not as churn | Feels abstract/forecasty; labs downplay input constraints; revision history invites false dismissal | Hidden inside gross margins; unit economics look fine at demo scale; price cuts dominate the narrative |
| **Evidence strength** | Strong — systematic saturation study of 60 benchmarks [A2]; reliability-measurement math [A3]; adoption surveys [A4] | Strong but probabilistic — explicit CIs on stock estimates [B1]; one documented outward revision; expert dissent (Amodei ~10%) recorded | Strong for direction — spend-flip data [C1], Deloitte/Vista survey numbers [C2]; weaker for specific figures (C3/C4 secondary) |
| **Who bears the cost** | Enterprises (stalled pilots), end users (unreliable deployments), science (noisy progress signal) | Frontier labs (licensing bills), open ecosystem (parity loss), knowledge owners (pricing power) | Agent startups (margin inversion), enterprises (budget shocks), providers (negative gross margins at scale) |
| **Time horizon** | Now → continuous: agents already fail ~1-in-3 [A1]; certification need grows with regulation | 2026–2032 window [B1]; overtraining pulls earlier; effects (licensing market) already visible | Already here ("Inference Flip" early 2026 [C1]); worsens with agent adoption |
| **Mitigation feasibility** | High leverage per dollar: reliability-first sampling [A3], domain-embedded evals, benchmark governance — mostly process, not capital | Low–medium: synthetic data works only in verifiable domains; licensing is a transfer, not creation; efficiency gains are incremental | Medium–high: routing/caching/distillation deliver measured 3–10× savings today [C1]; requires FinOps discipline |
| **Strongest counterargument** | Convergence makes fine discrimination unnecessary; eval platformization may commoditize the gap | Amodei: ~10% stall probability; Epoch already revised outward once; algorithmic efficiency may decouple capability from data volume | Per-token deflation trend + hardware learning curves may outrun demand growth; Gartner's own 90%-cheaper forecast |

## Ranking rationale

- **Most under-emphasized relative to impact today:** Evaluation gap. It
  gates everything else — you cannot fix what you cannot measure, and both
  other bottlenecks' mitigations (synthetic-data quality, caching value)
  depend on it.
- **Hardest structural constraint:** Data exhaustion. Least controllable,
  longest lead time, drives consolidation.
- **Fastest-moving operational constraint:** Inference economics. Most
  actionable now; the one individual teams can move this quarter.

The three compound: cheap-looking inference enables agent sprawl → sprawl
burns tokens and generates unverifiable outcomes → evaluation debt hides the
burn until budgets break. The ranking above orders them by *leverage*, not
severity: invest in evaluation first.
