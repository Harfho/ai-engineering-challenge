# 03. Port scan (full TCP) + SSH banner — service discovery

## Stage 2: full TCP connect scan

- Why: establish complete TCP attack surface from our vantage point.
- Tool: `reconnaissance/tools/tcp_scan.py` (auditable asyncio connect scanner;
  written because sudo/nmap was unavailable in the agent shell — see tool docstring)
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

### Cross-vantage caveat

The assessment owner separately ran online scanners (HackerTarget nmap,
portchecker.io variants) and saved screenshots (`Documents/AI/portScan/*.png`)
that are not yet machine-readable in this environment (no image input, no OCR).
Their results must be reconciled against ours before finalizing findings —
differences could indicate geo-filtering or rate-limiting of specific source
ranges. PENDING until owner supplies text output.

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
