# 02. Reverse DNS — naming context

- Why: PTR records often hint at a host's function (e.g. `mail.example.com`,
  `vps-hostname.provider.net`). Zero-touch query.
- Command: `dig +short -x 185.146.233.222 +time=5 +tries=1`
- Date (UTC): 2026-08-24 ~08:27
- Output: (empty — no PTR record)

## Interpretation

No reverse DNS configured for this address. No naming signal about purpose.
Slightly unusual for professionally managed infrastructure but common for
single-purpose servers or privacy-oriented hosting.

## Limitations

Absence of PTR is weak evidence either way; recorded for completeness.
