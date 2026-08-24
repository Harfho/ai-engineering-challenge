"""Reminder generation: ErrorPattern -> actionable Reminder.

Actions are chosen by a deterministic rule table keyed on trigger tokens
(e.g. tokens containing 'migration'/'schema' map to migration advice).
The rule table is data, not code paths — extending coverage means adding
rules, which is exactly what an LLM provider could do dynamically later.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import List

from .models import ErrorPattern, Reminder, new_id, now_iso

CATEGORY_ACTIONS = {
    "database_migration":
     "Before altering database schema, check for and create a pending "
     "migration file; run the migration tooling before deploying.",
    "api_rate_limit":
     "Add exponential backoff with jitter around this API call and respect "
     "Retry-After headers instead of retrying immediately.",
    "authentication":
     "Verify credentials/token scope for this operation before executing; "
     "surface an explicit auth error instead of proceeding.",
    "network_timeout":
     "Set an explicit timeout and one bounded retry for this operation; "
     "check service health before repeating the call.",
    "database_connection_drop":
     "Wrap long-running database operations in retry-with-reconnect logic "
     "and verify connection-pool health before starting large batches.",
    "dependency":
     "Pin and install required dependencies before running the affected "
     "command; verify imports resolve in the target environment.",
}

# (regex over trigger+message text) -> action; used when no category matched.
ACTION_RULES = [
    (r"disk|space|storage|quota exceeded",
     "Check available disk/storage before large operations; clean or expand "
     "capacity when usage exceeds threshold."),
]


def choose_action(pattern: ErrorPattern) -> str:
    # Majority vote on member categories (deterministic tie-break by name).
    cats = [m.category for m in pattern.members if m.category]
    if cats:
        winner = Counter(cats).most_common(1)[0][0]
        if winner in CATEGORY_ACTIONS:
            return CATEGORY_ACTIONS[winner]
    text = " ".join([pattern.summary()] + pattern.label_tokens)
    for rx, action in ACTION_RULES:
        if re.search(rx, text):
            return action
    return ("Investigate the root cause of this recurring failure before "
            "repeating the same action; add validation to prevent it.")


def build_description(pattern: ErrorPattern) -> str:
    agents = sorted({m.agent for m in pattern.members})
    agent_part = agents[0] if len(agents) == 1 else "/".join(agents[:3])
    return (f"Recurring issue ({pattern.frequency}x across {pattern.sessions} "
            f"sessions, agent {agent_part}): {pattern.summary()}")


def generate_reminders(patterns: List[ErrorPattern]) -> List[Reminder]:
    reminders: List[Reminder] = []
    for p in patterns:
        freq, sessions = p.frequency, p.sessions
        confidence = min(0.95, 0.35 + 0.12 * freq + 0.08 * sessions)
        reminders.append(Reminder(
            reminder_id=new_id("REM"),
            description=build_description(p),
            trigger_context=list(p.label_tokens),
            recommended_action=choose_action(p),
            evidence_log_ids=sorted(m.log_row_id for m in p.members),
            confidence=round(confidence, 2),
            frequency=freq,
            created_at=now_iso(),
            source_pattern_id=p.pattern_id,
        ))
    return reminders
