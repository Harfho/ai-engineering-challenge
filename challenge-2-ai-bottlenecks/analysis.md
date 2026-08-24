# Analysis — Three AI Development Bottlenecks Nobody Keynotes

> STATUS: v2 (supersedes `archive/v1-first-pass/`). The first pass picked real
> problems but ones that fail the brief's actual test: benchmark saturation,
> the "data wall" and inference costs are all keynote material — you find
> them on page one of any search. The brief asks for bottlenecks that exist
> *because* nobody wants them discussed. So v2 applies a stricter selection
> filter, stated up front, and keeps the same evidence discipline: every
> factual claim sourced, every incentive argument labeled as interpretation.

## The selection filter

A bottleneck belongs on this list only if it passes all three:

1. **Structural, not a tooling gap.** More engineers or money don't fix it.
2. **Silence is profitable.** Discussing it honestly costs the big labs
   revenue, narrative, or legal position — which explains the silence.
3. **The keynote test.** Imagine an OpenAI or Google executive saying it
   plainly in a keynote. If that sentence is unthinkable, it belongs here.

Three survivors:

1. **Model churn: AI infrastructure with no stability guarantees**
2. **The rights wall: usable training data got priced and given expiry
   dates before it ever ran out**
3. **Effective-context collapse: the advertised window is not a working
   memory**

---

# Bottleneck 1 — Model churn (infrastructure without an LTS)

**What it is.** Enterprises are told to treat frontier models like
infrastructure — the new cloud, the new database. But no vendor offers what
infrastructure vendors offer: long-term support. Models get deprecated in
60-day windows, APIs that entire products were built on get retired within
a year of launch, and even model *parameters* break silently.

**Evidence it exists (all verifiable, none of it secret).**

- OpenAI's own deprecation log [S1] shows a rolling series of 2026 sunsets:
  the Assistants API retired Aug 26, 2026, one year after launch notice;
  the Evals platform was deprecated June 3, 2026; Agent Builder deprecated
  the same day; the Sora API exits Sept 24, 2026 *with no successor model
  listed*. The GPT-4o family went from announcement to full removal from
  ChatGPT in about two weeks (Jan 29 – Feb 13, 2026) [S2].
- Anthropic's written policy promises a 60-day minimum runway; its own
  published dates deliver exactly 60–62 days (claude-3-haiku: Feb 19 to
  Apr 20, 2026) [S2, S3]. A 60-day migration window for a system that took
  months to integrate is a forced march, not support.
- Breaking changes reach below the model level: on Claude Opus 4.7 and
  later, setting `temperature`, `top_p` or `top_k` to a non-default value
  returns a 400 error [S2]. A parameter your code sets can be deprecated.
- Resellers set their own clocks: Anthropic states its dates do not apply
  to Bedrock or Vertex deployments, so one integration can carry three
  different retirement schedules [S2].
- No vendor publishes a machine-readable deprecation feed; tracking is
  manual polling of changelog pages [S2].
- The cost lands on customers: regression-testing a prompt library of
  40–200 prompts against each new model version takes 2–5 engineer-days,
  roughly $5k–25k per quarter at consulting rates [S4]. And deprecation is
  only the loud case — silent snapshot updates change output behavior with
  no version bump at all, which has broken production prompts at "every
  team that's been in production long enough" [S5].

**Why it's structural.** Iteration speed *is* the moat. A lab that commits
to 24-month LTS freezes its ability to ship improvements, retrain, or kill
money-losing models. Stability and iteration speed are in direct tension,
and every frontier lab has chosen speed. This is why the fix never comes
from the vendors themselves.

**Counterargument and falsifier.** "Deprecations give months of notice and
weights stay available; enterprises just need better pipeline hygiene."
True as far as it goes, but it concedes the point: the customer absorbs a
recurring tax (revalidation, contract tests, routing layers) because the
vendor will not. Falsifier: if any major vendor ships a genuine LTS tier
(18+ months behavior-stable, SLA-backed), this bottleneck starts dissolving.
None has as of August 2026.

**Why Big Players stay quiet — our incentive-based interpretation (analysis,
not established fact).** The whole enterprise sales motion rests on "AI is
the new infrastructure." Nobody buying infrastructure accepts 60-day
deprecation cycles — database vendors promise years. Saying the quiet part
("our models are more like fashion than like Postgres") invites customers to
demand LTS contracts, which would cap iteration speed, and invites
regulators to ask whether something sold as infrastructure should be
regulated like it. There is also a telling detail: OpenAI deprecated its
own Evals platform in June 2026 while marketing reliability to enterprises
[S1] — admitting how fast even flagship-adjacent tooling dies undercuts the
stability pitch. Silence is cheaper.

**What would actually help.** Machine-readable deprecation feeds (an RSS
equivalent — trivially cheap, still absent); contractual behavior-stability
windows priced as a premium tier; industry-standard "model semver" so
breaking changes are machine-detectable. Customers are already building the
workarounds (routing layers, contract tests, owned calendars [S2]) — the
market is paying a private tax to patch a public gap.

---

# Bottleneck 2 — The rights wall arrived before the volume wall

**What it is.** The public debate is about running out of internet — token
counts, 300T estimates, synthetic data. That debate is a decoy. The binding
constraint moved in 2024–2025 from *volume* to *rights*: text that cannot
legally be used might as well not exist, and the courts and the market have
started attaching prices and expiry dates to what was previously free to
crawl.

**Evidence it exists.**

- Anthropic's copyright class action settled in September 2025 for a
  reported $1.5B — the largest copyright recovery in history — establishing
  a de facto baseline of roughly $3,000 per work that now functions as a
  reference price across the whole market [S6, S7].
- Data access became recurring opex with expiration dates, not a one-time
  crawl: Reddit licenses to Google (~$60M/yr) and OpenAI (~$70M/yr) — about
  $130M/yr, ~10% of Reddit's total revenue per its SEC filings [S8] — and
  by mid-2026 those deals were up for renegotiation with Reddit publicly
  weighing *blocking* Google's access entirely [S10].
- The same content carries two simultaneous prices: Reddit sued Anthropic
  in June 2025 alleging 100,000+ unauthorized scrapes while cashing checks
  from Google and OpenAI [S9]. Getty won judgment in its UK case in Nov
  2025; NYT v. OpenAI remains active [S7].
- Deal volume went from 12 disclosed licensing deals in 2023 to a projected
  ~127 by mid-2026, with roughly $2B in disclosed value led by News
  Corp–OpenAI ($250M over five years) and News Corp–Meta (up to $50M/yr)
  [S6, S7].

**Why it's structural.** Unlike the volume wall, this constraint *tightens*
over time regardless of technical progress: every court decision raises the
price floor, every expiring deal is repriced upward, and opt-outs compound.
Compute scales with capital; rights scale with litigation, and litigation
has no Moore's law.

**Counterargument and falsifier.** "Licensing deals prove the market works;
content flows to whoever pays." That is true for the top ~100 publishers —
and irrelevant for the long tail that made web-scale training possible.
Nobody can sign 100M individual authors. The settlement price floor makes
the tail *more* litigable, not less. Falsifier: if a functioning collective-
licensing mechanism emerged (a BMI for text) that cleared most rights
cheaply, the wall would come down. As of August 2026 nothing resembling it
exists.

**Why Big Players stay quiet — our incentive-based interpretation (analysis,
not established fact).** Three silences stack here. Admitting that usable
supply is priced-per-work and expiring kills the scale narrative ("we'll
just train on more") that drives valuation. Naming the $3k/work floor out
loud invites every rights-holder on earth to demand it. And conceding that
past training may have been infringing has direct legal exposure — which is
why public statements stay frozen on "efficiency and synthetic data" while
the real action happens in court dockets and contract negotiations nobody
keynotes. The one thing no frontier lab will say: the scarce resource of
this decade is not compute or tokens. It is *cleared* text.

**What would actually help.** Collective licensing with blanket rights
(the music-industry model); provenance metadata standards so consent is
machine-checkable at crawl time; revenue-share arrangements tied to
inference rather than one-time training fees. All three exist as proposals;
none exists as infrastructure, because building it means admitting the wall
is real.

---

# Bottleneck 3 — Effective-context collapse

**What it is.** Context window size became the spec-sheet arms race of
2024–2026: 128K, 200K, 400K, a million tokens, printed on every model card.
Measured reality: the fraction of that window over which a model *reasons
reliably* is far smaller, task-dependent, and almost never published. You
pay per token for the whole window; you get reliable recall from a slice
of it.

**Evidence it exists.**

- RULER (NVIDIA, COLM 2024) evaluated 17 models claiming ≥32K contexts:
  only four sustained satisfactory performance even at 32K. Claimed vs
  effective: LWM 1M → under 4K; Yi-34B 200K → 32K; GPT-4 128K → 64K;
  Command-R 128K → 32K [S11].
- NoLiMa (LMU Munich + Adobe Research, 2025) removed the lexical overlap
  that lets models cheat needle-tests: effective lengths collapsed to
  ≤2K–8K tokens for most models claiming 128K+ — Llama 3.3 70B fell from a
  claimed 128K to ~8K effective [S12].
- The shape problem predates both: "Lost in the Middle" (Liu et al., 2023)
  showed recall depends strongly on *where* information sits, not just how
  much there is [S13]. Follow-up work in 2026 found information density
  collapses effective context earlier than length alone predicts [S14].
- Practitioner synthesis puts it bluntly: retrieval feeds the model 17–38%
  of the tokens a full-window approach consumes, and at volume the cost
  difference reaches orders of magnitude — which is why RAG refuses to die
  despite every "RAG is dead, long context killed it" headline [S14].

**Why it's structural.** Attention over a window is not memory over a
window. Making a million tokens *reliably* useful requires architectural
changes whose costs (attention compute, training data with genuinely
long-range dependencies, evaluation at length) all scale badly. Meanwhile
the marketing benefit of a bigger number is instant and free.

**Counterargument and falsifier.** "The window is honest — it's an input
limit, and capability keeps improving; NoLiMa-style results reflect older
models." Partly fair: newer models score better. But the claim being sold
is the window, and no frontier lab publishes accuracy-versus-length curves
for its own flagship next to the spec number. If the gap had closed, the
curves would be marketing assets — their absence is the tell. Falsifier:
vendors publishing reliability-vs-length curves as prominent as the window
number would retire this bottleneck.

**Why Big Players stay quiet — our incentive-based interpretation (analysis,
not established fact).** Context length is the last spec-sheet number a
buyer can compare without reading a benchmark methodology, so it carries
enormous marketing leverage; publishing honest curves would reset every
competitor comparison overnight and admit that RAG plumbing — unglamorous,
unmonetized by the lab — is still required. There is also a pricing angle
worth naming carefully as interpretation: per-token input pricing monetizes
the region of the window beyond effective context. The unusable part of the
window still bills.

**What would actually help.** Publish effective-context curves per task
family (retrieval / multi-hop / aggregation) beside every window spec;
price by *effective* tokens or offer long-context tiers honestly; standard
benchmarks (RULER-class) run at release and reported in model cards. The
research community already built the measurement tools — adoption is the
missing piece, and adoption is exactly what the incentives resist.

---

## Why these three, and not the famous ones

| Famous bottleneck | Why it fails the brief's test |
|---|---|
| Benchmark saturation | Keynoted constantly ("evals crisis" panels at every major conference); labs fund eval teams publicly |
| Training-data exhaustion (token counts) | Epoch-style estimates are among the most-cited AI articles on the internet |
| Inference economics / GPU costs | Earnings-call staple; CFOs discuss it openly |

Each of our three inverts that: the facts sit in changelogs, court dockets,
and appendix tables — places a buyer might look but a keynote never goes.
That placement is not accidental, and connecting the placement to the
incentives is our interpretation, offered as analysis rather than fact.

## How the three interlock

They compound on the same victim: the team trying to build on top.
Model churn (1) forces constant revalidation; effective-context collapse
(3) means the revalidation must measure curves, not single numbers; the
rights wall (2) shapes what the next generation of models can even learn,
pushing vendors toward proprietary data flywheels — which further locks in
churn because switching providers means abandoning the flywheel you fed.

Full source list with quality tiers: [`sources.md`](sources.md).
Head-to-head ranking: [`comparison.md`](comparison.md).
