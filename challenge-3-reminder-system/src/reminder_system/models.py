"""Core data models for the reminder system.

All components exchange these dataclasses; nothing here knows about any
specific AI provider or storage engine.
"""
from __future__ import annotations

import dataclasses
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


@dataclass
class LogEntry:
    """One historical AI interaction. Mirrors the assessment's log schema."""
    session_id: str
    timestamp: str
    agent: str
    user_request: str = ""
    agent_action: str = ""
    result: str = ""
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    row_id: Optional[int] = None  # assigned by the store

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class ErrorEvent:
    """A single identified failure extracted from a LogEntry."""
    log_row_id: int
    session_id: str
    timestamp: str
    agent: str
    normalized_message: str   # numbers/ids/paths replaced with placeholders
    raw_message: str          # best-effort concatenation of error+result text
    signals: List[str]        # which detectors fired, e.g. ["error_field", "http_429"]
    category: Optional[str] = None  # deterministic keyword category or LLM-provided
    event_id: Optional[str] = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = new_id("err")


@dataclass
class ErrorPattern:
    """A cluster of similar ErrorEvents observed repeatedly."""
    pattern_id: str
    members: List[ErrorEvent]
    label_tokens: List[str]           # salient shared tokens, used as triggers
    sessions: int                     # number of distinct sessions involved
    first_seen: str
    last_seen: str

    @property
    def frequency(self) -> int:
        return len(self.members)

    def summary(self) -> str:
        return self.members[0].normalized_message


@dataclass
class Reminder:
    """An actionable, machine-queryable reminder derived from a pattern."""
    reminder_id: str
    description: str
    trigger_context: List[str]        # tokens/phrases that describe when it applies
    recommended_action: str
    evidence_log_ids: List[int]
    confidence: float                 # [0,1] how sure we are the pattern is real
    frequency: int                    # occurrences in history
    created_at: str
    source_pattern_id: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
