# Analysis — Three Under-Emphasized AI Development Bottlenecks

> STATUS: final. Selection rationale, evidence chains, and counterarguments
> below. Full source list with quality tiers in `sources.md`; comparative
> ranking in `comparison.md`.

## Executive summary

Public AI discourse concentrates on pre-training scale and benchmark
breakthroughs. We argue the binding constraints on real-world AI progress
lie elsewhere. Three bottlenecks are simultaneously (a) under-emphasized
relative to their impact and (b) structurally hard — not solvable by simply
training larger models:

1. **The evaluation & verification bottleneck** — our ability to measure,
   verify, and trust model behavior is shrinking *relative to* model
   capability. Benchmarks saturate faster than they can be replaced; headline
   accuracy no longer predicts deployment reliability; enterprises cannot
   demonstrate value, so adoption stalls.
2. **High-quality training data exhaustion** — the stock of human-generated
   public text that powers scaling is finite (~300T effective tokens) and is
   being consumed at an accelerating rate; the wall arrives 2026–2032, and
   inference-economics-driven overtraining pulls it earlier.
3. **Inference economics** — the cost center of AI has flipped from training
   to serving. Agentic workloads multiply token consumption non-linearly;
   per-token prices fall while total bills rise; unit economics of agent
   products invert before product-market fit is proven.

These three interlock: data exhaustion raises the value of every token
(inference economics), while unreliable evaluation makes it impossible to
know whether expensive tokens bought anything (evaluation). The reminder
system prototype in Challenge 3 is a direct response to bottleneck 1's
practical face: making verified institutional memory retrievable at the
moment of action.

---

## Bottleneck 1 — The evaluation & verification gap

**Definition.** The widening mismatch between what models can do and what we
can reliably measure, predict, or certify about what they will do — spanning
benchmark saturation, statistical floors on reliability measurement, and the
absence of deployment-relevant evaluation.

**Why it exists.** Benchmarks are static artifacts evaluated against moving
targets. Once a benchmark's top-model score gaps shrink below measurement
uncertainty, it stops differentiating [A5] — and a systematic study of 60
LLM benchmarks found nearly half already saturated, with private test sets
providing *no* protective effect [A2]. Capability grew ~an order of
magnitude faster than evaluation infrastructure; evaluations "are being
outpaced by the progress they were built to measure" [A1].

**Technical/economic roots.**
- *Statistical*: distinguishing 99.9% from 99.999% reliability requires
  sample sizes that grow inversely with failure rate — Monte Carlo evals
  hit a compute wall exactly where safety-critical applications need
  precision [A3].
- *Economic*: evaluation produces no revenue; capability demos do. Labs
  rationally over-invest in capability relative to measurement.
- *Incentive*: developer-reported results increasingly diverge from third-
  party replications, and contamination undermines comparability [A1].

**Why current approaches don't solve it.** Building harder benchmarks
(Humanity's Last Exam etc.) restarts the saturation clock but doesn't fix
the reliability-measurement floor or domain-transfer problem: scoring 90% on
expert questions says little about judgment inside a specific law practice
[A1, A4]. Private/hidden test sets don't help [A2]. LLM-as-judge inherits
the very biases it should measure.

**Why it matters going forward.** With frontier labs within ~25 Elo points
of each other [A1], capability stops being the differentiator; cost,
reliability, and verifiable fit become decisive. Agents that fail roughly
one attempt in three [A1] cannot enter regulated workflows without
certification machinery that does not yet exist. Evaluation is now the rate-
limiter of *adoption*, not just of research: 97% of enterprises report
struggling to show business value from GenAI initiatives [A4].

**Concrete examples.** AIME 2025 near-perfect scores coexisting with 2.4×
differences in true failure rates between "equivalent" models [A3]; a
Microsoft Build coding agent failing to fix build errors after 11 prompts
from four engineers, feeding public ROI skepticism [A4]; GPQA going from
daunting (early 2024) to effectively saturated within ~a year [A2].

**Mitigation paths.** (1) Reliability-first evals: importance-sampling
frameworks estimating five-nines failure rates affordably [A3]. (2)
Dynamic/contamination-resistant benchmarks (LiveCodeBench pattern) plus
governed retirement criteria [A2, A5]. (3) Domain-embedded evaluation —
private, task-realistic suites run continuously against production
distribution shift, treated as part of deployment rather than an
afterthought [A4]. (4) Institutional-memory systems that make past verified
outcomes queryable at decision time (the Challenge 3 prototype is a minimal
instance).

**Limitations & counterarguments.** See "Counterarguments" section.

---

## Bottleneck 2 — High-quality training data exhaustion

**Definition.** The approaching point at which frontier-scale training
consumes essentially all available high-quality human-generated public text,
converting data from a commodity into a scarce production input.

**Why it exists.** Scaling laws reward dataset growth superlinearly relative
to the stock of suitable text. Epoch AI estimates the effective stock of
public human text at ~300 trillion tokens (90% CI: 100T–1000T) and projects
full utilization between 2026 and 2032 under historical growth; if models
train compute-optimally, the wall arrives around a 5e28 FLOP run — expected
~2028 [B1].

**Technical/economic roots.**
- *Chinchilla-optimal* training demands tokens ∝ parameters; the stock grows
  with internet output (slow) while dataset sizes grow exponentially [B1, B2].
- *Inference economics couples in*: labs overtrain models (more tokens per
  parameter) to cut serving costs — Llama-3-70B was ~10× overtrained. Under
  profit-maximizing policies, 5–100× overtraining moves full utilization to
  2027 or even 2025 [B1]. Bottleneck 3 therefore accelerates bottleneck 2.
- *Quality asymmetry*: filtering and multi-epoch reuse expanded the effective
  stock 2–5× (why Epoch revised its own estimate out from "before 2026"),
  but such techniques have diminishing returns and multi-epoch reuse has
  measurable limits [B1, B2].

**Why current approaches don't fully solve it.**
- *Synthetic data* risks distribution collapse without careful verification
  pipelines — which reintroduces the evaluation bottleneck (what verifies
  synthetic quality?); it works today mainly in verifiable domains (math,
  code).
- *Licensing/private data* (e.g., reported ~$60M/yr Google–Reddit deal) is
  real but bounded by what exists and by antitrust/privacy constraints.
- *Efficiency gains* (better architectures) change the exponent, not the
  sign, of the constraint.

**Why it matters going forward.** The marginal resource for capability
growth shifts from compute (elastic) to verified human knowledge (inelastic).
Whoever controls proprietary, high-quality corpora gains a compounding moat;
public-open-model parity becomes harder to sustain; and the economic logic
pushes toward inference-cheap overtrained models — tightening bottleneck 3
in a loop.

**Concrete examples.** Epoch's documented revision history (2022: HQ text
exhausted "before 2026" → 2024: median 2028) shows both the seriousness and
the uncertainty [B1, B2]; Nature gave the projection mainstream scientific
legitimacy in Dec 2024 [B3]; licensing deals and litigation over scraping
(2023–2026 news flow) are the market pricing this scarcity in real time.

**Mitigation paths.** Verification-gated synthetic data generation;
data-efficient training (distillation, curriculum); retrieval-augmented
systems that externalize knowledge instead of parameterizing all of it;
institutional investment in proprietary data flywheels (user interactions →
curated corpus).

**Limitations & counterarguments.** See "Counterarguments" section.

---

## Bottleneck 3 — Inference economics

**Definition.** The structural shift of AI's cost center from training to
serving, combined with agentic workloads' non-linear token consumption —
producing falling per-token prices alongside rising total spend and
inverting unit economics for agent products.

**Why it exists.** Every deployed user, query, and agent step pays inference;
only one training run happens per model. In 2026, cumulative global
inference spending passed training ("the Inference Flip"); inference now
accounts for ~85% of enterprise AI budgets and ~two-thirds of global AI
compute spend [C1].

**Technical/economic roots.**
- *Agentic multiplication*: an insurance-claim agent reasoning through steps,
  calling sub-agents, and reloading context consumes 5–30× the tokens of a
  single-shot request [C2]; loops and retries multiply consumption another
  3–7× before optimization [C3]. Reasoning tiers charge $8–20 per M output
  tokens where buyers pay for hidden thinking too.
- *Jevons dynamics*: API prices fell ~80% from early 2025 to 2026 (GPT-4-class
  capability ≈$0.40/M vs $30/M in March 2023), yet Gartner projects total
  spend rising because cheaper tokens enable disproportionately more
  token-hungry capabilities [C1]. Enterprise model-usage spend tripled to
  ~$7M average in 2025; many orgs exceed 10B tokens/month [C2].
- *Margin math*: enterprise AI gross margins slid 40%→33% (Deloitte Q4 2025);
  documented cases show unit economics inverting at 500–1,000 users, far
  below enterprise scale [C3]. OpenAI's widely reported ~$5B loss on ~$3.7B
  2025 revenue is the frontier-scale version of the same shape [C4].

**Why current approaches don't solve it.** Hardware improves fast (Blackwell:
up to 10× tokens/watt vs Hopper; Gartner forecasts >90% per-token cost
decline by 2030) — but each efficiency wave gets absorbed by demand growth
and new spending axes (test-time compute, long context, multimodality).
Routing/caching (semantic caches save 3–10× on repetitive traffic; memory-
augmented plan reuse cuts latency 100× on hits) helps locally and is exactly
where the industry is now racing [C1].

**Why it matters going forward.** Product strategy inverts: the constraint
is no longer "can the model do it" but "can serving it survive contact with
real usage volumes." This privileges smaller routed models, aggressive
caching, and — notably — *not re-learning what the organization already
knows*: retrieving verified prior solutions instead of paying tokens to
re-derive them. (Again, Challenge 3.)

**Concrete examples.** Fintech fraud-detection agent: $5K/month at 50 users
(Nov 2025) → $15K/month at just 500 users (Jan 2026), losses by ~700–1,000
concurrent users [C3]; demo-day pattern of agents collapsing at turn ~10 as
context reloads compound [C3]; IDC warning that even well-staffed orgs
underestimate AI infrastructure costs by up to 30% [C1].

**Mitigation paths.** Model routing (cheap/fast tier + deep tier — GPT-5's
internal router validates the pattern); semantic caching and plan-reuse
memory; token-budget observability (FinOps for AI); distillation of big-model
behavior into cheap executors; designing agents to *retrieve before they
reason*.

**Limitations & counterarguments.** See "Counterarguments" section.

---

## Counterarguments to our position

**Against #1 (evaluation).** *Falsifier:* if domain-embedded eval suites +
five-nines sampling become routine commodities (as cloud benchmarking
platforms claim), the gap closes commercially and stops being structural.
Also, convergence at the frontier could reduce the *need* for fine-grained
discrimination — "any top model suffices" is itself an answer. Rebuttal:
saturation studies show measurement noise, not equivalence [A5]; and
regulated deployment needs certification, not leaderboards.

**Against #2 (data).** Dario Amodei assigns only ~10% probability to data
scarcity materially stalling progress — efficient algorithms and synthetic
data may substitute. Epoch itself revised exhaustion outward once (2024→2028)
when filtering/multi-epoch techniques improved [B1]. *Falsifier:* continued
capability growth through 2030+ with stable data inputs would falsify the
scarcity framing. Rebuttal: the claim is not "progress stops" but "the
marginal input changes from elastic compute to inelastic verified knowledge"
— which Amodei's own licensing strategy behaviorally confirms.

**Against #3 (inference).** Per-token prices are collapsing on trend lines
(80%/year by some measures); extrapolating current agentic token appetite
ignores both hardware learning curves and algorithmic efficiency (test-time
compute may get 10× cheaper). *Falsifier:* enterprise AI gross margins
recovering toward SaaS norms while agent usage grows would show the crisis
self-resolving. Rebuttal: Gartner's explicit warning — deflation of
commodity tokens ≠ deflation of frontier reasoning [C1] — plus observed
margin compression despite two years of price cuts suggests demand elasticity
keeps winning.

## Conclusion

Evaluation, data, and inference economics form one coupled system: scarce
data raises token values; opaque evaluation prevents verifying what tokens
bought; and unverified agentic loops burn tokens fastest of all. Teams that
treat these as first-class engineering constraints — building measurement,
memory, and cost discipline into their development loop rather than bolting
them on — hold the compounding advantage the next phase of AI development
will reward. `comparison.md` ranks the three by impact horizon and
actionability.
