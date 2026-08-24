# Analysis — Three AI Development Bottlenecks Nobody Keynotes

> STATUS: v3 (supersedes `archive/v1-first-pass/`). v2 fixed the source
> selection after review; v3 fixes the argument structure. Every bottleneck
> below answers the same four questions explicitly: What is the bottleneck?
> Why does it exist? Why does it get worse at scale? Why would a major AI
> company have an incentive NOT to emphasize it? Facts are sourced;
> incentive arguments are labeled as our interpretation, offered as
> analysis rather than fact.

## The selection filter

A bottleneck belongs here only if all three hold:

1. **Structural, not a tooling gap** — more engineers or money don't fix it.
2. **Silence is profitable** — honest discussion costs the big labs revenue,
   narrative, or legal position.
3. **The keynote test** — an executive saying it plainly on stage is
   unthinkable.

Three survivors:

1. **Rented cognition: the dependency and control asymmetry under
   independent AI products**
2. **The rights wall: usable training data got priced and given expiry
   dates before it ever ran out**
3. **Effective-context collapse: the industry markets window size while
   the operative quantity is how much reasoning survives as the window
   fills**

---

# Bottleneck 1 — Rented cognition

### What is the bottleneck?

Independent AI products do not run on infrastructure they own or even
meaningfully influence. They run on rented cognition: a small number of
vendors unilaterally control the models, interfaces, pricing, lifecycle,
and even the serving behavior of the systems those products depend on.
Model deprecation is merely the loudest symptom. The structure underneath
is a dependency and control asymmetry: the vendor can change anything —
what the product costs, how it behaves, whether it exists — and the
customer's recourse is limited to migrating onto another vendor's equally
rented stack.

The asymmetry has five faces:

- **Weights**: closed, never transferable; the customer's prompts and
  fine-tunes adapt to a model they cannot inspect or keep.
- **Interface**: APIs and SDKs are vendor-defined and versioned by the
  vendor; OpenAI retired the Assistants API within a year of its launch
  notice [S1].
- **Lifecycle**: deprecation clocks run 60–62 days at Anthropic in practice
  [S2, S3]; OpenAI removed the GPT-4o family from ChatGPT about two weeks
  after announcement [S15]. Publishing the schedule makes the clock
  transparent; it does not give the customer any control over it.
- **Pricing**: unilaterally set, changed historically without negotiated
  protection.
- **Serving behavior**: silent snapshot updates alter outputs with no
  version bump — the vendor changes the product *inside* the package the
  customer already shipped [S5].

### Why does it exist?

Because capability concentrates. Frontier training runs cost more than
almost any customer could ever amortize, so the market structurally
separates into a handful of producers and millions of dependents. Nothing
about software practice caused this — it is the capital intensity of the
technology. The asymmetry is the natural market shape of this industry,
and standard software-era remedies (open source, self-hosting, multi-cloud
portability) barely exist at the frontier: open weights trail by a
generation, and "portability" means re-prompting and re-validating
everything on someone else's stack.

### Why does it get worse at scale?

Dependence compounds faster than usage. A product that succeeds integrates
deeper: prompt libraries tuned to one model's quirks, fine-tunes trained
on its behavior, agent workflows chaining dozens of calls whose combined
behavior no contract describes. Each layer multiplies the cost of any
vendor-initiated change — a revalidation that costs days for a chatbot
costs months for an agent platform. Meanwhile the producer side
concentrates further: rising training costs shrink the set of credible
vendors, so the customer's negotiating leverage falls precisely as its
dependence rises. Scale buys you volume discounts and removes your exits
at the same time.

### Why would a major AI company have an incentive NOT to emphasize it?
*(our incentive-based interpretation — analysis, not established fact)*

Because the entire enterprise motion sells AI *as* infrastructure, and
infrastructure buyers expect infrastructure obligations: stability
windows, price protection, exit paths. Naming the asymmetry honestly —
"you are dependent on us in ways no contract fully covers, and we intend
to keep changing things" — does three kinds of damage at once. It invites
customers to demand LTS contracts and SLAs, capping the iteration speed
that is the lab's actual moat. It invites regulators to ask whether
something load-bearing for thousands of companies should carry
utility-style obligations. And it arms every procurement department with
the vocabulary to demand concessions. There is also a quieter lever worth
naming carefully as interpretation: forced migration herds users onto
newer models on the vendor's schedule, and depreciation of the old stack
is effectively a monetization tool — which is why even trivially cheap
fixes (machine-readable deprecation feeds) remain unshipped years into the
API era [S2].

**Counterargument and falsifier.** "Policies are public, notice periods
exist, weights are preserved — the market works." That addresses the
symptom's politeness, not the structure's asymmetry: a transparent clock
is still a clock you don't control. Anthropic's commitment to preserve
weights [S3] is the tell — the escape hatch exists only for those who can
run models themselves, i.e., not the dependent customers this bottleneck
is about. Falsifier: genuine LTS tiers with behavior-stability SLAs, or a
real portability standard, would dissolve the asymmetry. None exists as of
August 2026.

---

# Bottleneck 2 — The rights wall arrived before the volume wall

### What is the bottleneck?

The public debate counts tokens — how much internet remains to train on.
That debate is the decoy. The operative constraint is legal usability:
text that cannot lawfully be used might as well not exist. Between late
2023 and late 2025, usable training data acquired two properties it never
had before — a price per work and an expiration date — and both were set
by courts and platforms, not by labs.

### Why does it exist?

Because the default flipped. For a decade the working assumption was
*crawlable equals usable*. A wave of litigation (NYT v. OpenAI, Getty's UK
judgment, Authors Guild cases) and one landmark settlement moved the
default: Anthropic's September 2025 copyright resolution, reported at
$1.5B, established a de facto reference price near $3,000 per work that
now anchors negotiations across the market [S6, S7]. Simultaneously,
platforms that aggregate user-generated content discovered they are toll
booths: Reddit licenses the same corpus to Google (~$60M/yr) and OpenAI
(~$70M/yr) — roughly $130M/yr, about 10% of Reddit's revenue per its SEC
filings [S8] — while suing Anthropic over the identical content [S9].
Deal volume grew from 12 disclosed agreements in 2023 to a projected ~127
by mid-2026, roughly $2B disclosed [S6, S7].

### Why does it get worse at scale?

Every scaling pressure pushes the wrong way. Larger models need *more*
high-quality human text exactly as enforcement strengthens. Bigger labs
are richer lawsuit targets, so legal exposure grows with success. Each
settled case and signed deal raises the comparable that rights-holders
cite next — the price floor ratchets upward automatically. And the
market-based escape, synthetic data, fails hardest at the frontier: the
most capable models are the ones most sensitive to training on their own
output. The constraint tightens fastest for whoever is scaling hardest.

### Why would a major AI company have an incentive NOT to emphasize it?
*(our incentive-based interpretation — analysis, not established fact)*

Three silences stack. First, valuation: the growth story is "scale solves
everything," and admitting that the input to scale is priced-per-work and
expiring breaks the compounding math investors are buying. Second,
pricing power: saying "$3,000 per work is now the floor" out loud invites
every author, publisher, and platform on earth to demand exactly that.
Third, legal exposure: engaging with the topic concedes that past training
runs are contestable — which is why public communication stays frozen on
"efficiency and synthetic data" while the decisive action happens in court
dockets and private contracts nobody keynotes. The unsayable sentence:
*the scarce resource of this decade is cleared text.*

**Counterargument and falsifier.** "Licensing deals prove the market
works." They prove it works for perhaps the top hundred publishers. The
long tail — the millions of sites and authors who made web-scale corpora
possible — cannot be individually contracted, and the new price floor
makes suing the tail more attractive, not less. Falsifier: a functioning
collective-licensing clearinghouse (a BMI for text) that clears most
rights cheaply would tear this wall down. As of August 2026 nothing
resembling one exists.

---

# Bottleneck 3 — Effective-context collapse

### What is the bottleneck?

The industry measures context capability using the size of the window,
while the economically and technically relevant quantity is how much
useful reasoning and retrieval survives as the window fills. Those two
quantities diverge enormously. The distinction matters because "1M
context" is a compelling product metric; admitting that effective
utilization is substantially lower weakens that narrative — so the
utilization curve is measured in academia and omitted from model cards.

### Why does it exist?

Attention over a window is not memory over a window. Architecturally,
models lose grip on information as position and interference grow;
training distributions contain few genuinely long-range supervision
signals worth the name; and the benchmark that made window claims
credible — needle-in-a-haystack — is beatable through lexical overlap,
so it measures matching, not reasoning [S11–S13]. Remove the overlap
(NoLiMa) and effective lengths collapse to ≤2K–8K tokens for most models
claiming 128K+ [S12]. RULER found only four of seventeen models claiming
≥32K sustained satisfactory performance even at 32K; LWM claimed 1M and
delivered under 4K [S11].

### Why does it get worse at scale?

Two multipliers. First, workload shape: agentic systems accumulate
context every step — history, tool outputs, retrieved chunks — so the
gap between billed tokens and usefully-used tokens compounds per action,
and agent economics inherit the tax multiplicatively. Second, billing
structure: input tokens are priced uniformly, which means the region of
the window beyond effective context is pure margin for the vendor and
pure waste for the buyer. Practitioner measurements put retrieval-only
approaches at 17–38% of full-window token consumption [S14] — the gap
between those numbers and the spec sheet is the size of the problem.

### Why would a major AI company have an incentive NOT to emphasize it?
*(our incentive-based interpretation — analysis, not established fact)*

Window size is the last specification a buyer can compare without reading
benchmark methodology, which makes it disproportionately valuable
marketing real estate. Publishing honest accuracy-versus-length curves
would reset every competitor comparison overnight, concede that RAG
plumbing — which the lab does not sell — remains mandatory, and draw
attention to the fact that per-token pricing bills the portion of the
window the model cannot reliably use. The research community built the
measurement tools years ago; adoption on model cards is the missing
piece, and adoption is precisely what the incentives resist.

**Counterargument and falsifier.** "Capability improves every generation,
and NoLiMa reflects older models." Fair, and beside the point: the claim
being sold is the window, and the curves that would substantiate it are
never published next to it. If the gap had truly closed, those curves
would be marketing assets — their absence is the tell. Falsifier: vendors
publishing reliability-vs-length curves as prominently as the window
number retires this bottleneck.

---

## Why these three, and not the famous ones

| Famous bottleneck | Why it fails the brief's test |
|---|---|
| Benchmark saturation | keynoted constantly; labs fund eval teams publicly |
| Training-data exhaustion (token counts) | among the most-cited articles on the internet |
| Inference economics / GPU costs | earnings-call staple |

Each of ours inverts that placement: the facts live in changelogs, court
records, SEC filings, and appendix tables — places a buyer might look but
a keynote never goes. That placement is not accidental; connecting it to
incentives is our labeled interpretation.

## How the three interlock

Rented cognition is the umbrella. The rights wall (2) determines what the
few controllers can train on, pushing them toward proprietary flywheels
that deepen dependence. Effective-context collapse (3) determines how
much of what customers pay for actually reasons — and since the vendor
controls serving behavior, the customer often cannot measure it except by
building the measurement infrastructure themselves. All three taxes land
on the same party: the independent builder.

Full source list with quality tiers: [`sources.md`](sources.md).
Leverage ranking: [`comparison.md`](comparison.md).
