# Challenge 1 — Server Investigation

**Target:** `185.146.233.222`
**Authorization:** Assessment owner states the target belongs to them and grants full operational freedom (see `docs/methodology.md` assumption log).
**Status:** COMPLETE — see [`ANSWERS.md`](ANSWERS.md) for direct answers to the brief's five questions; full report in [`report.md`](report.md).

## Plan

| Stage | Activity | Touch level |
|-------|----------|-------------|
| 1 | Context gathering (whois/reverse DNS/routing context) | passive |
| 2 | Port discovery (full TCP sweep, top UDP) | low |
| 3 | Service + version identification on open ports only | low–medium |
| 4 | Targeted enumeration of identified services (HTTP, banners, TLS, etc.) | medium, non-destructive |
| 5 | Validation of suspected weaknesses with safe proofs | controlled |
| 6 | Report writing (`report.md`, findings in `findings/`) | — |

## Tooling note

nmap was deliberately not used: the assessment instead runs a ~50-line
auditable asyncio TCP scanner (`tools/tcp_scan.py`, stdlib only, source
committed) so every probe's behavior is reviewable from first principles.
Trade-off accepted: no OS fingerprinting or scripted version probes beyond
banners. Tool provenance is recorded with each evidence artifact.

## Deliverable

`report.md` — professional security report: executive summary, scope,
methodology, reconnaissance narrative, attack surface, findings with severity
and evidence, remediation, limitations, conclusion.
