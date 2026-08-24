"""Error identification: scan LogEntries and extract ErrorEvents.

Deterministic detectors (no AI required):
    error_field   - log.error is non-empty
    result_failed - result field matches failure vocabulary
    http_status   - metadata.status / metadata.http_status >= 400
    exit_code     - metadata.exit_code not in (0, None)

Message normalization replaces numbers, uuids, hashes, paths and quoted
strings with placeholders so that recurring *shapes* of failure cluster
together even when details differ.

Rows whose result records success are never error events, no matter what
residual error text they carry (contradictory outcomes resolve in favor of
the recorded outcome).

An optional LLMProvider may enrich events with a category/summary, but never
gates detection — the system works fully without it.
"""
from __future__ import annotations

import re
from typing import Dict, List

from .models import ErrorEvent, LogEntry
from .providers import LLMProvider, NullLLM

FAILURE_WORDS = (
    "fail", "error", "exception", "traceback", "denied", "refused",
    "timeout", "timed out", "missing", "not found", "does not exist",
    "cannot", "unable", "invalid", "panic", "fatal",
)

# Deterministic keyword categories. Applied BEFORE clustering so that
# semantically-identical failures phrased differently ("schema drift",
# "missing migration", "relation does not exist") gain shared strong tokens
# and cluster together. An LLM provider can override/refine these later.
CATEGORIES = [
    (r"migrat|schema|alter table|create table|drop table|add column|"
     r"column .* does not exist|relation .* does not exist|drift",
     "database_migration"),
    (r"rate.?limit|too many requests|429|throttl|quota",
     "api_rate_limit"),
    (r"unauthorized|401|403|auth|permission denied|password authentication",
     "authentication"),
    (r"timeout|timed out|deadline exceeded|connection refused",
     "network_timeout"),
    (r"modulenotfound|no module named|importerror|pip install|npm install|"
     r"dependency",
     "dependency"),
]

_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
_HASH = re.compile(r"\b[0-9a-f]{7,64}\b")
_NUM = re.compile(r"\b\d+(\.\d+)?\b")
_PATH = re.compile(r"(?<=\s)/(?:[\w.\-]+/)+[\w.\-]*|(?<=\s)~?/[\w.\-/]+")
_QUOTED = re.compile(r"'[^']{12,}'|\"[^\"]{12,}\"")  # keep short quoted ids like "users"


def categorize(text: str) -> str | None:
    low = text.lower()
    for rx, cat in CATEGORIES:
        if re.search(rx, low):
            return cat
    return None


def normalize_message(msg: str) -> str:
    m = _UUID.sub("<id>", msg)
    m = _HASH.sub("<hash>", m)
    m = _QUOTED.sub("<str>", m)
    m = _PATH.sub("<path>", m)
    m = _NUM.sub("<n>", m)
    return re.sub(r"\s+", " ", m).strip().lower()


def detect_signals(e: LogEntry) -> List[str]:
    signals: List[str] = []
    blob = f"{e.error} {e.result}".lower()
    if e.error.strip():
        signals.append("error_field")
    if any(w in e.result.lower() for w in FAILURE_WORDS):
        signals.append("result_failure_word")
    status = e.metadata.get("status", e.metadata.get("http_status"))
    if isinstance(status, int) and status >= 400:
        signals.append(f"http_{status}")
    code = e.metadata.get("exit_code")
    if isinstance(code, int) and code != 0:
        signals.append(f"exit_{code}")
    if not signals and any(w in blob for w in FAILURE_WORDS):
        signals.append("failure_word_combined")
    return signals


def raw_message(e: LogEntry) -> str:
    # Prefer the error text; fall back to result only when there is no error
    # field. Concatenating both would just duplicate the status word into
    # every bag-of-tokens and dilute similarity.
    if e.error.strip():
        return e.error
    if e.result.strip():
        return e.result
    return f"(no message; action='{e.agent_action}')"


def identify_errors(logs: List[LogEntry],
                    llm: LLMProvider | None = None) -> List[ErrorEvent]:
    llm = llm or NullLLM()
    events: List[ErrorEvent] = []
    for e in logs:
        # Contradictory outcomes: when the recorded result says the
        # interaction succeeded, residual error text (from an earlier
        # attempt inside the same interaction, say) must not count as a
        # failure — otherwise noisy successes inflate patterns.
        if e.result.strip().lower() in ("success", "succeeded"):
            continue
        signals = detect_signals(e)
        if not signals:
            continue
        raw = raw_message(e)
        enriched: Dict = {}
        try:
            enriched = llm.analyze_error(raw, {"agent": e.agent}) or {}
        except Exception:
            enriched = {"category": None, "summary": None}
        category = enriched.get("category") or categorize(raw) or categorize(e.agent_action + " " + e.user_request)
        summary = enriched.get("summary") or normalize_message(raw)
        if category:
            summary = f"[{category}] {summary}"
        events.append(ErrorEvent(
            log_row_id=e.row_id or -1,
            session_id=e.session_id,
            timestamp=e.timestamp,
            agent=e.agent,
            normalized_message=summary,
            raw_message=raw,
            signals=signals,
            category=category,
        ))
    return events
