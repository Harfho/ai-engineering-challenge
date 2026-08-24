# Findings — Challenge 1

Four findings, one file each, all evidence-linked. Start with
[`../report.md`](../report.md) for context; direct answers to the brief:
[`../ANSWERS.md`](../ANSWERS.md).

| ID | Title | Severity |
|----|-------|----------|
| [F-01](F-01-ssh-exposure.md) | SSH service exposed publicly on standard port (only TCP listener) | LOW |
| [F-02](F-02-no-ptr.md) | No reverse DNS (PTR) record for the host | INFO |
| [F-03](F-03-current-openssh.md) | OpenSSH 10.0p2 appears current-generation (positive; version ≠ secure config) | INFO-positive |
| [F-04](F-04-default-deny-posture.md) | Default-deny TCP posture, ICMP permitted (positive + availability caveat) | INFO-positive |

Each finding file contains: ID/title · severity (+ why) · description ·
evidence links into `reconnaissance/` · practical impact · remediation ·
limitations/what could not be verified.
