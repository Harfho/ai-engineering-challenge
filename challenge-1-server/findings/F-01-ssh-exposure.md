# F-01 — SSH service exposed to the public internet on standard port

- **ID / Title:** F-01 / Only exposed TCP service is OpenSSH on 22/tcp
- **Severity:** LOW
- **Why this severity:** Expected exposure for any administered server; no
  vulnerability identified in the service itself (current-gen version, F-03).
  Rated LOW rather than INFO because it is the host's entire remote attack
  surface and is subject to internet-wide brute-force noise by default.

## Description

A full TCP connect scan of 1–65535 found exactly one open port, 22,
answering `SSH-2.0-OpenSSH_10.0p2`. All other ports silently drop packets
(no RSTs), indicating default-deny firewalling with a single allow rule.

## Evidence

- `reconnaissance/03-portscan-ssh-banner.md` (scan methodology, banner capture)
- `reconnaissance/raw/03-tcp-scan-full.json` (raw result: open=[22], filtered=65534)
- `reconnaissance/tools/tcp_scan.py` (auditable scanner)

## Practical impact

- Credential-guessing exposure against sshd from any source address.
- Compromise of this one service = compromise of the host (typical for SSH).

## Remediation

1. Enforce key-only authentication (`PasswordAuthentication no`,
   `KbdInteractiveAuthentication no`) — highest-value single control.
2. Consider rate-limiting/port-knocking or VPN-gating if admin sources are
   static (defense-in-depth, not a substitute for #1).
3. Ensure `PermitRootLogin no`.

## Limitations / what we could not verify

Auth configuration is not observable pre-authentication beyond algorithm
negotiation; we could not confirm whether password auth is disabled without
an authorized login attempt (out of scope: no credential testing performed).
