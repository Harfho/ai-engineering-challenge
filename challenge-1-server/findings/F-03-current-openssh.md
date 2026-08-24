# F-03 — SSH daemon is a current-generation release (positive)

- **ID / Title:** F-03 / OpenSSH 10.0p2 indicates active patching
- **Severity:** INFO (positive finding)
- **Why this severity:** Not a weakness; recorded because it materially
  lowers the residual risk of F-01 and demonstrates maintenance discipline.

## Description

Banner: `SSH-2.0-OpenSSH_10.0p2`. The 10.x line is the current OpenSSH
generation (10.0 GA April 2025); running p2 of it implies OS/package
maintenance within roughly the past year. Protocol version 2 only (v1
long deprecated).

## Evidence

- `reconnaissance/03-portscan-ssh-banner.md` (stage 3, banner capture)
- Banner string itself; version-line dating per OpenSSH release history

## Practical impact

- Reduces likelihood of known-vulnerability exploitation against sshd.
- Signals the host is administered, not abandoned — raises expected quality
  of other controls (e.g., key-only auth plausibly already configured).

**Caveat (important):** a current version is not a secure configuration.
Auth policy (`PasswordAuthentication`, `PermitRootLogin`), per-user
restrictions, and crypto settings cannot be observed pre-authentication;
"current" reduces the known-CVE risk class only.

## Remediation

Continue routine unattended-upgrades/security patching. No action required.

## Limitations / what we could not verify

Banner can be customized (a very old sshd could masquerade as new);
probability is low but acknowledged. Package-level verification would
require authorized shell access.
