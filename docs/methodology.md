# Methodology (all challenges)

## Evidence hierarchy

1. **Recorded observation** — raw command output or measurement stored under the relevant challenge directory, with command, timestamp, and exit status where applicable.
2. **Interpretation** — what we believe the observation means, written by us, clearly separated from the raw output.
3. **Corroboration** — a second independent observation supporting the same interpretation (e.g., version banner + behavior probe).
4. **Cited source** — external material used for research claims, recorded in `sources` files with enough metadata to relocate.

Rules:

- A conclusion may only cite tiers 1–4 above. Speculation must be labeled as speculation or omitted.
- Scanner output is treated as a *lead*, not a finding. Findings require manual validation where feasible.
- Negative results ("we checked X, nothing was found") are recorded too — they bound the attack surface and show coverage.

## Command recording format (Challenge 1)

Every command is logged in `reconnaissance/` as:

```
### <sequence>. <tool + purpose>
- Why:      why this command, at this stage
- Command:  exact command line
- Date:     UTC timestamp
- Output:   relevant excerpt (full raw output kept alongside)
- Interpretation: what it tells us / doesn't tell us
```

## Progressive depth model (Challenge 1)

1. Passive/low-touch recon (whois-style context, no intrusive probing)
2. Service discovery (port scan)
3. Service/protocol identification on open ports only
4. Targeted, non-destructive enumeration of identified services
5. Validation of suspected weaknesses (safe proofs, e.g., retrieving an obviously exposed file)
6. Reporting

Aggressive exploitation (DoS, destructive payloads, credential brute-forcing at scale) is out of scope unless explicitly needed and safe.

## Redaction policy

Before committing reconnaissance artifacts:

- Credentials, session tokens, cookies, personal data of third parties → redacted
- If redaction would destroy evidentiary value, keep hashes/truncated forms and note it
- The committed record must be sufficient to reproduce the *reasoning*, not necessarily the sensitive payload

## Assumption log

| # | Assumption | Made by | Impact if wrong |
|---|------------|---------|-----------------|
| 1 | Target `185.146.233.222` is owned by the assessment owner who grants full operational freedom (stated in the assessment brief). | Phase 0 | All of Challenge 1 depends on this authorization |
| 2 | No prior assessment repo existed locally; created fresh at `~/ai-engineering-challenge`. | Phase 1 | Cosmetic — can be relocated/pushed anywhere |

(This table grows as phases proceed.)
