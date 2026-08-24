"""Log ingestion: JSONL/JSON files -> validated LogEntry -> Store.

Accepted per-line schema (extra keys are ignored, missing optional keys
default to ""):

    {
      "session_id": "...", "timestamp": "...", "agent": "...",
      "user_request": "...", "agent_action": "...",
      "result": "...", "error": "...", "metadata": {}
    }

Malformed lines never abort ingestion; they are counted and reported.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from .models import LogEntry
from .store import Store

REQUIRED = ("session_id", "timestamp", "agent")


def parse_line(line: str) -> tuple[LogEntry | None, str | None]:
    """Returns (entry, None) or (None, error_reason)."""
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as e:
        return None, f"invalid json: {e}"
    if not isinstance(obj, dict):
        return None, "line is not a json object"
    for k in REQUIRED:
        v = obj.get(k)
        if not isinstance(v, str) or not v.strip():
            return None, f"missing required field '{k}'"
    md = obj.get("metadata", {})
    if not isinstance(md, dict):
        md = {"_coerced_metadata": str(md)}
    return LogEntry(
        session_id=obj["session_id"].strip(),
        timestamp=obj["timestamp"].strip(),
        agent=obj["agent"].strip(),
        user_request=str(obj.get("user_request", "")),
        agent_action=str(obj.get("agent_action", "")),
        result=str(obj.get("result", "")),
        error=str(obj.get("error", "")),
        metadata=md,
    ), None


def ingest_file(path: str | Path, store: Store) -> Tuple[int, List[str]]:
    """Ingest a .jsonl or .json file. Returns (inserted_count, problems)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    entries: List[Dict] = []
    if path.suffix == ".json" and text.lstrip().startswith("["):
        arr = json.loads(text)
        problems: List[str] = []
        entries = [(o, None) for o in ([a for a in arr] if isinstance(arr, list) else [])]
    else:
        entries, problems = [], []
        for i, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            entry, err = parse_line(line)
            if err:
                problems.append(f"line {i}: {err}")
            else:
                entries.append((entry, None))
    inserted = 0
    for item, _err in entries:
        e = item[0] if isinstance(item, tuple) else item
        store.insert_log(e)
        inserted += 1
    return inserted, problems
