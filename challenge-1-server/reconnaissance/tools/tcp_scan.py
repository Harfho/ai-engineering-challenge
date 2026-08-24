#!/usr/bin/env python3
"""Minimal async TCP connect scanner (Challenge 1, stage 2).

Why home-made instead of nmap:
    sudo was unavailable in the agent shell at execution time; this keeps the
    assessment unblocked with fully auditable logic (~50 lines, stdlib only).
    Semantics match nmap's connect scan classification:
      open      - TCP handshake completed
      closed    - RST received (port reachable but nothing listening)
      filtered  - no reply within timeout (dropped or unreachable)

Usage: python3 tcp_scan.py <target-ip> [start-port] [end-port]
Output: JSON {port: state} on stdout, human progress on stderr.
"""
import asyncio
import json
import sys
import time

CONCURRENCY = 1200
TIMEOUT_S = 1.5


async def probe(target: str, port: int, sem: asyncio.Semaphore, out: dict):
    async with sem:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(target, port), TIMEOUT_S)
            out[port] = "open"
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
        except ConnectionRefusedError:
            out[port] = "closed"
        except asyncio.TimeoutError:
            out[port] = "filtered"
        except OSError as e:
            out[port] = f"oserr:{e.errno}"


async def main():
    target = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 65535
    sem = asyncio.Semaphore(CONCURRENCY)
    out: dict = {}
    done = 0
    total = end - start + 1
    t0 = time.monotonic()

    async def tick():
        nonlocal done
        done += 1
        if done % 5000 == 0:
            print(f"[{time.monotonic()-t0:6.1f}s] {done}/{total}", file=sys.stderr)

    tasks = []
    for p in range(start, end + 1):
        tasks.append(asyncio.create_task(probe(target, p, sem, out)))
        tasks.append(asyncio.create_task(tick()))
    await asyncio.gather(*tasks)

    print(json.dumps({str(k): v for k, v in sorted(out.items())}, indent=0))


if __name__ == "__main__":
    asyncio.run(main())
