# Reconnaissance log — Challenge 1

One file per command/stage: `NN-topic.md`, numbered in execution order.

Format (from `docs/methodology.md`):

```
### <seq>. <tool + purpose>
- Why:
- Command:
- Date (UTC):
- Output (excerpt):
- Interpretation:
```

Contents:

| File | Stage |
|------|-------|
| [`01-rdap-context.md`](01-rdap-context.md) | registry triangulation (RIPE RDAP, Team Cymru, IPinfo) |
| [`02-reverse-dns.md`](02-reverse-dns.md) | PTR lookups for host and neighbors |
| [`03-portscan-ssh-banner.md`](03-portscan-ssh-banner.md) | full TCP connect scan + SSH banner/KEXINIT probe |
| [`04-purpose-analysis.md`](04-purpose-analysis.md) | purpose inference chain + independent Shodan cross-check |

Raw outputs live in `raw/` (verbatim JSON as captured); the scan tool is
`tools/tcp_scan.py`.
