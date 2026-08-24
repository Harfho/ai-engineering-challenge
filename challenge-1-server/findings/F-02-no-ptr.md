# F-02 — No reverse DNS (PTR) record for the host

- **ID / Title:** F-02 / 185.146.233.222 has no PTR record
- **Severity:** INFO
- **Why this severity:** Not directly exploitable; an operational-hygiene
  issue with security-adjacent consequences.

## Description

`dig +short -x 185.146.233.222` returns empty; authoritative reverse zone
for the block exists (`233.146.185.in-addr.arpa.` with NS `ns1.flokinet.is`)
but contains no PTR for this address. Confirmed against both local and
public resolvers (Cloudflare/Google).

## Evidence

- `reconnaissance/02-reverse-dns.md` (queries + interpretation)
- Corroborated by IPinfo artifact: hostname field absent
  (`Documents/AI/185.146.233.0_24 IP range details _ IPinfo.html`)

## Practical impact

- Outbound mail from this host is more likely to be rejected/spam-flagged.
- Log lines and threat-intel enrichment show bare IPs, reducing triage speed.
- Minor OPSEC signal: unremarkable hosts blend in; this one stands out as
  "unconfigured".

## Remediation

Ask FlokiNET (or manage rDNS via provider panel if offered) to set a PTR
matching the host's forward DNS (forward-confirmed reverse DNS).

## Limitations / what we could not verify

Whether the owner intends this host to send mail or be user-visible at all;
if it is a purely internal jump host behind VPN, INFO remains accurate.
