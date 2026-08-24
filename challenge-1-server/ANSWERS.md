# Direct Answers to the Brief — Challenge 1

> The brief asks five specific things. Each is answered below in one or two
> lines, with the evidence trail right behind it. Full detail: `report.md`.

---

## 1. What is the server being used for?

**A private remote-administration endpoint (jump-host / headless management
box) — not a public-facing service server.**

Evidence chain: single SSH listener by design · everything else silently
DROPped (deliberate firewall) · no PTR, no hostname, no web/TLS anywhere in
registry data, DNS, Shodan history, or active scans (built *not* to be
found) · sits in FlokiNET ehf space (Icelandic privacy-focused hoster,
AS200651) among similar hardened boxes plus one app server (.220:3001).
Confidence MEDIUM-HIGH; full inference chain + falsifier:
[`reconnaissance/04-purpose-analysis.md`](reconnaissance/04-purpose-analysis.md)

## 2. What services are running?

**Exactly one: OpenSSH.** Nothing else answers on TCP.

Evidence: full connect scan 1–65535 → open=[22], closed=0, filtered=65534.
Independent confirmation: Shodan InternetDB sees ports=[22] only.
[`reconnaissance/03-portscan-ssh-banner.md`](reconnaissance/03-portscan-ssh-banner.md),
[`04-purpose-analysis.md`](reconnaissance/04-purpose-analysis.md)

## 3. What ports are exposed?

**22/tcp only.** All other 65,534 ports are filtered (silent DROP, zero RSTs
→ stateful default-deny policy, not "nothing listening"). ICMP: block-wide
pingability reported by third parties (119 pingable IPs in the /24).

Raw scan result: [`reconnaissance/raw/03-tcp-scan-full.json`](reconnaissance/raw/03-tcp-scan-full.json)

## 4. What software/services are behind those ports?

**`SSH-2.0-OpenSSH_10.0p2`** — appears to be current-generation OpenSSH
(10.x line GA April 2025), protocol 2 only. KEXINIT probe shows stock
upstream defaults incl. post-quantum hybrid kex (`mlkem768x25519` offered
first) → uncustomized, honestly-bannered daemon; no banner fakery
indicators. Note: version currency *suggests* active patching but does not
establish secure configuration — auth policy remains unverifiable without
login.

Evidence: banner capture + KEXINIT transcript in
[`03-portscan-ssh-banner.md`](reconnaissance/03-portscan-ssh-banner.md) and
[`04-purpose-analysis.md`](reconnaissance/04-purpose-analysis.md)

## 5. Are there vulnerabilities, misconfigurations, or unusual behavior?

**No externally verifiable exploitable vulnerability was identified within
the assessment scope.** Posture appears unusually deliberate; three
observations recorded. (External, unauthenticated recon only — no login,
no exploitation attempted.)

- **Shodan flags zero known CVEs** for this host/version; independent
  passive intel agrees with our active scan exactly.
- **Unusual (positive):** default-DROP everything except SSH while the
  wider block stays pingable — selective hardening, rare among internet hosts.
- **F-01 (LOW):** SSH exposed on standard port = constant brute-force noise;
  key-only auth could not be verified externally. → verify
  `PasswordAuthentication no`, `PermitRootLogin no`.
- **F-02 (INFO):** No PTR record (hygiene, affects mail/log readability).
- **Caveat:** if any public web/mail service was intended here, it is
  unreachable from tested vantage points — availability misconfiguration.

**Scope bounds on this answer:** local configuration behind SSH was not
inspected (no credentials), and **UDP services were not assessed at all** —
a TCP-only methodology cannot see them. "No findings" here means "none
detectable by the methods used", which is deliberately narrower than
"secure".

Findings with severity rationale & remediation:
[`findings/F-01-ssh-exposure.md`](findings/F-01-ssh-exposure.md) …
[`F-04-default-deny-posture.md`](findings/F-04-default-deny-posture.md);
full report: [`report.md`](report.md)
