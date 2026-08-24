# 03. Port scan (full TCP) + SSH banner — service discovery

## Stage 2: full TCP connect scan

- Why: establish complete TCP attack surface from our vantage point.
- Tool: `reconnaissance/tools/tcp_scan.py` (auditable asyncio connect scanner;
  deliberately chosen over nmap for full source-level review — see tool docstring)
- Command: `python3 tools/tcp_scan.py 185.146.233.222 1 65535`
- Date (UTC): 2026-08-24 ~09:45
- Duration: ~2.5 s wall (1200 concurrent probes, 1.5 s timeout)
- Output: raw JSON retained at `raw/03-tcp-scan-full.json`

```
open:      1 port  -> 22
filtered:  65534   -> no reply (dropped)
closed:    0
```

### Interpretation

- Only **22/tcp** answers; every other port silently drops packets. Either a
  default-DROP firewall with a single allow rule (deliberate hardening) or an
  upstream filter. Notably **no web ports** (80/443) answered from here —
  unusual for a hosted server claiming a purpose; see cross-vantage caveat below.
- Zero RSTs observed: consistent with stateful DROP filtering rather than a
  host without services.

### Cross-vantage caveat — RESOLVED (artifact audit, 2026-08-24 ~10:40 UTC)

The assessment owner supplied saved browser artifacts (`Documents/AI/`).
Machine audit of every HTML file shows **none of them contain scan results**:

| Artifact | Target IP present? | Content |
|---|---|---|
| `Port Checker*.html` ×5 | no | identical landing-page shells (144026 B each); results rendered dynamically, never persisted |
| `Online Port Scanner ... HackerTarget.com.html` | no | landing page only |
| `Free Port Scanner Report (Light).html` | no | Pentest-Tools Nuxt shell; embedded JSON holds CMS/banners only |
| `Blocked Page.html` | no | JS-rendered block page |
| `portScan/*.png` ×3 | n/a | images; unreadable in agent environment (no OCR) |
| `185.146.233.0_24 IP range details _ IPinfo.html` | yes | genuine third-party data, see below |

Conclusion: a second-vantage port list is simply not available in text form.
Our full-TCP result (only 22/tcp open) therefore stands as primary evidence
from one vantage point, with the limitation stated. No discrepancy can be
claimed either way.

### What the IPinfo artifact DOES corroborate

From `IPinfo.html` (saved by owner 2026-08-24 09:16):

```
AS200651 — FlokiNET ehf   BGP Prefix: 185.146.233.0/24
Pingable IPs: 119         Routers: 0
ProbeNet measurement: Bucharest, RO -> 185.146.233.219, 9.577 ms
                          (August 20, 2026)
```

- Independently confirms ASN + org + prefix (third source after RDAP and
  Team Cymru) — recorded in `01-rdap-context.md`.
- "Pingable IPs: 119" across the /24 implies most addresses answer ICMP,
  i.e., the block is not blackholed wholesale — making our observation that
  all TCP ports except 22 are *filtered* look like deliberate per-host or
  per-port firewall policy rather than upstream null-routing.
- The Bucharest ProbeNet ping succeeding to .219 shows at least ICMP
  reachability from outside Iceland; combined with our SSH banner success,
  the host is reachable internationally — so if other online scanners
  reported different results, timing/rate-limiting would be the likeliest
  cause, not geo-blocking.

## Stage 3: service identification on open port

- Why: version fingerprint of the single exposed service.
- Command: python socket connect to 22, read 512 bytes, 8 s timeout
- Date (UTC): 2026-08-24 ~09:52
- Output:

```
SSH-2.0-OpenSSH_10.0p2
```

### Interpretation

- OpenSSH **10.0p2**, protocol 2 only. The 10.x release line is the current
  generation (10.0 GA April 2025); running it indicates active patching within
  roughly the last year. Positive security signal.
- SSH exposed to the whole internet on the standard port: normal practice, but
  it *is* the primary remote-attack surface; brute-force exposure should be
  checked (auth config not observable pre-auth beyond algorithm negotiation).

## Limitations

- Connect-scan cannot observe UDP services; UDP probing deferred (low expected
  value given total TCP filtering).
- A single vantage point; filtering may be source-selective (see caveat).
