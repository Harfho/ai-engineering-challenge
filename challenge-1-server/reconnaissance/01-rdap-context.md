# 01. RDAP registry lookup — network ownership context

- Why: Establish who owns/announces the target address before any active
  probing. Shapes expectations (hosting provider vs residential vs corporate)
  and identifies the correct abuse/reporting channel.
- Command: `curl -sL https://rdap.org/ip/185.146.233.222`
- Date (UTC): 2026-08-24 ~08:25
- Output (excerpt): full response in `raw/01-rdap-185.146.233.222.json`

```
handle:      185.146.232.0 - 185.146.235.255   (/22 block)
name:        IS-FLOKINETEHF-20160411
type:        ALLOCATED PA
country:     IS (Iceland)
registrar:   FlokiNET ehf (ORG-FE72-RIPE), NOC contact abuse@flokinet.is
registration event: 2024-03-21T10:19:15Z
```

## Interpretation

- The /24 containing the target (`185.146.233.0/24`) is announced by a
  commercial hosting/network provider (FlokiNET ehf, Iceland).
- Therefore the target is almost certainly **hosted infrastructure**
  (dedicated server, VPS, or colo) rather than a residential or corporate-LAN
  device. Expectation for later stages: externally reachable services are
  intentional; misconfigurations are still possible but "accidental exposure
  of home device" scenarios are less likely.
- Abuse/reports channel: `abuse@flokinet.is` (relevant only for reporting,
  not part of testing).

## Corroboration

Team Cymru IP-to-ASN whois (`whois.cymru.com:43`, netcat via python):

```
200651 | 185.146.233.222 | 185.146.233.0/24 | IS | ripencc | 2016-04-11 | FlokiNET - FlokiNET ehf, IS
```

Two independent sources (RIPE registry via RDAP + Cymru ASN mapping) agree:
AS200651 FlokiNET.

## Limitations

- Registry data tells us *who announces* the space, not what runs on the box.
- No PTR record exists for this exact address (`dig +short -x` returned empty),
  so reverse-DNS naming gives no additional hint about purpose.
