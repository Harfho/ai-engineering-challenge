# Security Report — Server Investigation

- **Target:** 185.146.233.222 (185.146.233.0/24, AS200651 — FlokiNET ehf, IS)
- **Date(s) of assessment:** 2026-08-24 (all times UTC)
- **Assessor:** Harfho
- **Authorization:** Owner-stated ownership + full operational freedom
  (assumption #1, `docs/methodology.md`)
- **Status:** COMPLETE — passive recon + full TCP scan + service
  identification performed; no exploitation attempted.

---

## 1. Executive summary

The assessment owner asked us to investigate their server at
`185.146.233.222`. Registry triangulation (RIPE RDAP, Team Cymru, IPinfo)
confirms the host sits in FlokiNET ehf space in Iceland (AS200651,
prefix 185.146.233.0/24). A full TCP connect scan of all 65,535 ports found
exactly **one open port — 22/tcp**, answering `SSH-2.0-OpenSSH_10.0p2`; the
remaining 65,534 ports are silently filtered. The OpenSSH version is
current-generation, indicating active patching.

Overall risk posture: **strong**. The attack surface is a single, well-
maintained service behind default-deny filtering. Findings: F-01 SSH
exposure (LOW), F-02 missing PTR record (INFO), F-03 current OpenSSH
(INFO-positive), F-04 deliberate deny-by-default posture with an
availability caveat (INFO-positive). No exploitable condition was
identified from external reconnaissance alone; the highest-value remaining
control is confirming key-only SSH authentication.

## 2. Scope

- **In scope:** `185.146.233.222` (single IPv4). DNS lookups touching the
  host and its parent zones.
- **Out of scope:** any other host in the /24 (including `.219`, which
  appears pingable); UDP scanning; credential brute force or login attempts;
  application-layer testing (no HTTP service observed); denial-of-service
  of any kind.
- **Permitted techniques:** passive registry queries, DNS enumeration,
  TCP connect scanning (full range), banner capture on open ports — per
  progressive-recon plan agreed in Phase 2 (`docs/methodology.md`).
- **Assessment window:** single session, 2026-08-24 ~09:20–10:45 UTC.

## 3. Methodology

Full rationale and rules: `docs/methodology.md`. Summary of what was done:

| Stage | Technique | Tooling | Evidence |
|---|---|---|---|
| 1. Passive context | RDAP (RIPE), ASN (Team Cymru DNS), IPinfo artifact | `curl`, `dig`, saved HTML | `01-rdap-context.md`, `raw/01-*.json` |
| 2. Reverse DNS | PTR queries via local + public resolvers, SOA check | `dig` | `02-reverse-dns.md` |
| 3. Full TCP sweep | asyncio connect scan, 1200 concurrency, 1.5 s timeout | custom auditable scanner (`tools/tcp_scan.py`; nmap unavailable without sudo) | `03-portscan-ssh-banner.md`, `raw/03-tcp-scan-full.json` |
| 4. Service ID | Banner capture on open port | python socket | `03-portscan-ssh-banner.md` stage 3 |
| 5. Artifact audit | Owner-supplied browser artifacts parsed & reconciled | python text/JSON extraction | `03-portscan-ssh-banner.md` cross-vantage section |

Every claim traces to a logged command with output excerpt and UTC
timestamp. Speculation is labeled as such; scanners were treated as lead
generators whose raw outputs are retained verbatim.

## 4. Reconnaissance narrative

1. **Registry context (stage 1).** RDAP over HTTPS returned network
   `IS-FLOKINETEHF-20160411`, org ORG-FE72-RIPE (FlokiNET ehf, Reykjavík),
   country IS, abuse contact abuse@flokinet.is. Independent Team Cymru
   origin lookup: AS200651 | 185.146.233.0/24 | IS | flokinet.is. The
   owner's later-saved IPinfo page independently confirmed all three values
   — three concordant sources, zero conflicts.
2. **Reverse DNS (stage 2).** No PTR exists for .222 despite the reverse
   zone being delegated to FlokiNET nameservers (`ns1/ns2.flokinet.is`) —
   a hygiene gap, not a security control (→ F-02).
3. **Full TCP sweep (stage 3).** Custom asyncio scanner swept 1–65535 in
   ~2.5 s wall time. Result: open=[22], closed=0, filtered=65534. Zero RSTs
   anywhere → stateful DROP behavior, i.e., deliberate firewalling rather
   than "nothing listening" (which would RST on most stacks).
4. **Service identification (stage 4).** Port 22 answered immediately with
   `SSH-2.0-OpenSSH_10.0p2`. Deeper KEXINIT probing shows stock OpenSSH 10
   algorithm defaults (post-quantum `mlkem768x25519` offered first) — an
   uncustomized, honestly-bannered daemon.
5. **Artifact reconciliation (stage 5).** The owner's saved online-scanner
   pages contained no persisted results (verified by exhaustive IP-string
   search across every HTML file); the IPinfo artifact did corroborate
   registry data and added two useful facts: 119 pingable IPs across the
   /24, and a successful ICMP measurement from Bucharest to `.219`
   (2026-08-20).
6. **Cross-vantage closure + purpose analysis (stage 6).** Shodan's passive
   InternetDB independently confirms our active scan exactly: ports=[22],
   OpenSSH 10.0p2, zero flagged CVEs, and — critically — **no hostname in
   its history for .222** (nor neighbors sampled). Neighbor characterization:
   `.219` is a Debian SSH box; `.220` serves something on 3001/tcp. Full
   inference chain: `reconnaissance/04-purpose-analysis.md`.

### Determining the server's purpose (brief requirement)

The evidence triangulates to: **a private remote-administration endpoint**
(jump-host / headless management box), not a public-facing service server.
Chain: single listener = current sshd → admin access by design; silent DROPs
elsewhere → deliberate policy; no PTR/hostname/web/TLS anywhere in registry,
DNS, Shodan history, or active scans → built *not* to be found; neighbors
show the block mixes hardened SSH boxes with real app servers (.220:3001) →
this slice hosts personal/small-team infrastructure at FlokiNET (Icelandic
privacy-focused hoster). Confidence MEDIUM-HIGH; falsifier would be any
trace of intended public service — none exists.

## 5. Attack surface

| # | Service | Port | Version | Identification confidence | Notes |
|---|---------|------|---------|---------------------------|-------|
| 1 | OpenSSH | 22/tcp | SSH-2.0-OpenSSH_10.0p2 | High (direct banner) | Only TCP listener; internet-reachable |
| — | (none) | 1–65535 excl. 22 | — | n/a | Filtered/DROP, no RST |
| — | ICMP | n/a | n/a | Medium (third-party artifact only; not probed directly) | Block reported pingable (119 IPs) |

UDP surface unassessed (see §10). Cross-vantage corroboration (Shodan
InternetDB): ports=[22] only, OpenSSH 10.0p2, vulns=[], hostnames=[] —
full agreement with our active scan (`reconnaissance/04-purpose-analysis.md`).

## 6. Findings

Full detail per finding in `findings/F-NN-*.md`.

### F-01 — SSH service exposed publicly on standard port (LOW)
Single exposed service = entire remote attack surface; subject to constant
internet-wide credential noise. Current version mitigates known-CVE risk.
Remediation focus: verify key-only auth, `PermitRootLogin no`, optional
rate-limiting.

### F-02 — No PTR record for .222 (INFO)
Reverse zone delegated but no record published. Hygiene issue affecting
mail deliverability and log readability, not exploitable.

### F-03 — OpenSSH 10.0p2, actively maintained (INFO, positive)
Current-generation daemon implies patch discipline within ~the last year;
materially lowers residual risk of F-01.

### F-04 — Default-deny TCP posture; ICMP permitted (INFO, positive + caveat)
65,534 ports dropped silently while the block answers ICMP elsewhere —
selective hardening, not null-routing. Caveat: if public web/mail service
was intended on this host, it is not reachable from our vantage point.

## 7. Severity assessment

Qualitative scale used: CRITICAL / HIGH / MEDIUM / LOW / INFO, informed by
CVSS-style factors (exposure, complexity, impact) but assigned judgmentally
because **no exploitation or authenticated testing was performed** — there
is no basis in external recon alone to claim exploitability, so nothing
above LOW could be honestly justified. Positives recorded as INFO-positive
rather than omitted: a report that lists only problems overstates risk.

## 8. Evidence index

| Finding / claim | Primary evidence |
|---|---|
| Network ownership (FlokiNET, AS200651, /24) | `reconnaissance/raw/01-rdap-185.146.233.222.json`; `01-rdap-context.md`; IPinfo artifact |
| No PTR record | `02-reverse-dns.md` (dig transcripts) |
| Only 22/tcp open; rest filtered | `raw/03-tcp-scan-full.json`; scanner source `tools/tcp_scan.py` |
| OpenSSH_10.0p2 banner | `03-portscan-ssh-banner.md` stage 3 |
| Block not blackholed (ICMP) | IPinfo HTML artifact (`Documents/AI/`) quoted in `03-...md` |
| Online-scanner artifacts contain no results | audit method + result table in `03-...md` cross-vantage section |
| Purpose determination + Shodan corroboration | `04-purpose-analysis.md` (InternetDB JSON excerpts, neighbor data, KEXINIT probe) |

## 9. Remediation recommendations

Priority order:

1. **Verify SSH key-only auth** (addresses F-01): confirm
   `PasswordAuthentication no`, `KbdInteractiveAuthentication no`,
   `PermitRootLogin no`. Ten-minute change, removes the dominant risk.
2. **Publish PTR** for .222 matching forward DNS (F-02): provider request
   to FlokiNET or self-service panel if available.
3. **Confirm allow-list matches intent** (F-04 caveat): document why 22 is
   the only TCP allowance; add explicit rules when new services are planned.
4. **Maintain patch cadence** (preserves F-03): keep unattended-upgrades or
   equivalent enabled.
5. Optional defense-in-depth for F-01: source-allowlisting admin IPs,
   rate-limiting (e.g., nftables limit), or VPN-gating SSH.

## 10. Limitations

- **No exploitation, no credentialed access:** findings reflect external
  reconnaissance only; sshd configuration (key-only? root login?) and host
  internals unverified.
- **Single vantage point:** ~~one source IP performed all probing;~~
  **resolved post-scan** — Shodan InternetDB's global sensor history agrees
  exactly (22 only, same version, no CVEs). Residual: Shodan is passive and
  periodic, so a briefly-lived service between its sweeps could evade both
  methods.
- **UDP unscanned:** connect-scanning does not observe UDP; deferred given
  total TCP filtering made broader exposure unlikely.
- **Tooling constraint:** nmap unavailable (no sudo in agent shell);
  equivalent coverage achieved with a custom asyncio connect scanner whose
  source is committed for audit. OS fingerprinting and service-version
  probes beyond banners were therefore out of reach.
- **Timing:** snapshot assessment (one window on 2026-08-24); posture may
  differ at other times or from other networks.

## 11. Conclusion

From the outside, `185.146.233.222` presents the profile of a deliberately
minimized, well-maintained host: registry data coherent across three
independent sources, a single current-generation SSH service, everything
else dropped rather than rejected, and no stale services leaking history.
The honest headline is as much about what was *not* found: no unexpected
listeners, no version-red-flag services, no contradictory signals between
vantages. Residual risk concentrates entirely in SSH credential policy,
which external methods cannot see — the recommended next step (§9 item 1)
is a five-minute config review that would close the largest remaining
unknown. Within the authorized scope, the investigation is complete.
