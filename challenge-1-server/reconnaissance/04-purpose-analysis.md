# 04. Server purpose analysis — what is this machine FOR?

> The brief asks not just "what is exposed" but "find out the **purpose**
> of the server". This file records the inference chain explicitly.
> Date (UTC): 2026-08-24 ~11:00–11:20

## New evidence collected for this question

### A. Independent cross-vantage confirmation (Shodan InternetDB, free API)

```
GET https://internetdb.shodan.io/185.146.233.222
{
  "cpes": ["cpe:/a:openbsd:openssh:10.0p2rn"],
  "hostnames": [],
  "ports": [22],
  "vulns": [],
  "tags": []
}
```

- Shodan's global sensor network sees **exactly what we saw**: only 22/tcp,
  same OpenSSH version, **no CVEs flagged**, **no hostnames ever recorded**.
- This resolves the single-vantage limitation from `03-portscan-ssh-banner.md`
  far more strongly than the owner's (empty) browser artifacts could:
  an independent global scanner with years of history agrees.

### B. Neighboring IPs in the same /24 (block characterization)

```
185.146.233.219 -> ports [22], CPEs: openssh_10.0p2, linux_kernel, debian_linux
185.146.233.220 -> ports [3001]           <- application-style port
```

- `.219`: another hardened Linux/Debian SSH box (the IP that answered ICMP
  from Bucharest per the IPinfo artifact).
- `.220`: runs a service on **3001/tcp** — a port commonly used by custom
  Node.js/Express-style application servers. So the /24 hosts *real
  application infrastructure*, not just network gear.
- Neither has hostnames in Shodan either → the whole slice is
  **deliberately unbranded**.

### C. SSH algorithm negotiation (fingerprint depth)

Probing KEXINIT from .222 returned stock OpenSSH 10.0 defaults:

```
kex: mlkem768x25519-sha256, sntrup761x25519-sha512@openssh.com,
     curve25519-sha256, curve25519-sha256@libssh.org
hostkeys: rsa-sha2-512, rsa-sha2-256, ecdsa-sha2-nistp256, ssh-ed25519
compression: none,zlib@openssh.com
```

- `mlkem768x25519` offered **first** = untouched upstream default order
  (post-quantum hybrid became default-first in recent OpenSSH).
- Conclusion: crypto config is uncustomized — consistent with a
  straightforwardly maintained box, no hardening scripts fiddling with
  algorithm priority, no banner fakery.

### D. Absence evidence (from stages 1–3)

No PTR on .222 (and none on sampled neighbors) · no web/mail/DNS listeners ·
no hostname in Shodan history · no TLS surface · abuse contact is the
provider's generic one.

## Inference chain → purpose

| Observation | Implication |
|---|---|
| Exactly one TCP listener: current OpenSSH | Admin access is the design goal |
| Everything else DROPped silently | Deliberate firewall policy, not neglect |
| Stock sshd config incl. PQ kex | Maintained by hand/upstream defaults, actively patched |
| No PTR, no hostname anywhere, no web | Not meant to be found/visited by humans |
| Same pattern on neighbor .219; app server exists at .220 | A slice of mixed infra: some boxes serve apps, some exist purely to be logged into |

**Assessed purpose:** a **private remote-administration endpoint** — most
plausibly a personal/jump server (bastion-style) or headless management box
belonging to the owner's small infrastructure set within FlokiNET space
(Icelandic privacy-focused hoster). It is *not* a public-facing service
server: there is nothing served except the ability to log in.

Confidence: MEDIUM-HIGH. What would raise it to HIGH: authorized login to
read shell history, running services (`ss -tunlp`), and config. What would
falsify it: any evidence of intended public services (none found across
registry, DNS, passive intel, and active scanning).

## Why this matters to the assessment

The purpose reframes findings: for an admin endpoint, F-01 (SSH exposure)
is the *whole* threat model, and its remediation (key-only auth) is cheap;
F-02 (PTR) becomes near-irrelevant cosmetically but still matters if the
box sends outbound mail (e.g., cron alerts) — unverifiable externally.
