# F-04 — Default-deny TCP posture; ICMP allowed (positive, with caveat)

- **ID / Title:** F-04 / All TCP filtered except 22; block is pingable
- **Severity:** INFO (positive finding, one availability caveat)
- **Why this severity:** The posture itself is a hardening positive. The
  caveat is observational: if any public web service was expected on this
  host, it is not reachable from our vantage point.

## Description

Full TCP sweep: 65,534/65,535 ports silently dropped (zero RSTs) —
characteristic of stateful default-DROP rules rather than "no services".
Independent evidence shows the wider block is NOT blackholed: the IPinfo
artifact reports 119 pingable IPs in 185.146.233.0/24 and a successful
ProbeNet ICMP measurement (Bucharest → .219, Aug 20, 2026). Together:
selective policy (ICMP yes, TCP only 22), not upstream null-routing.

## Evidence

- `reconnaissance/03-portscan-ssh-banner.md` stages 2 + cross-vantage section
- `reconnaissance/raw/03-tcp-scan-full.json`
- `Documents/AI/185.146.233.0_24 IP range details _ IPinfo.html`
  (pingable count, ProbeNet latency)

## Practical impact

- Strongly reduces remote attack surface to a single audited service.
- Caveat: any service intended for public reachability (web, mail) would be
  unreachable from at least some vantage points; if this host is meant to
  serve anything besides SSH, that is an availability misconfiguration.

## Remediation

Confirm the allow-list matches intent (22-only). If other services are
planned, add explicit allow rules rather than loosening default-deny.

## Limitations / what we could not verify

- Single vantage point; source-selective filtering cannot be ruled out
  (though international ICMP + our SSH success argue against geo-blocking).
- UDP services untested (out of MVP scope; low expected value given total
  TCP filtering).
