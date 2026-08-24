"""Reminder generation: ErrorPattern -> actionable Reminder.

Content is LAYERED, from most to least specific:

1. LLM-authored lesson: if a provider implements author_lesson(), the
   top member messages are sent to it and its lesson/action are used.
   This is how the system learns failure modes no rule anticipated.
2. Curated playbook: for patterns whose members have a known category,
   a hand-written action (CATEGORY_ACTIONS) is attached.
3. Evidence-derived fallback: otherwise the description and action are
   DERIVED FROM THE EVIDENCE ITSELF (frequency, sessions, most common
   message variants) — never generic boilerplate. A brand-new recurring
   failure therefore still produces an honest, useful reminder.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

from .models import ErrorPattern, Reminder, new_id, now_iso
from .providers import LLMProvider

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

# (regex over trigger+message text) -> action; used when no category matched
# AND no lesson was authored. Kept deliberately tiny: anything not covered
# here falls through to the evidence-derived text below.
ACTION_RULES = [
    (r"disk|space|storage|quota exceeded",
     "Check available disk/storage before large operations; clean or expand "
     "capacity when usage exceeds threshold."),
]

DERIVED_NEXT_STEP = (
    "Next step: reproduce the most common variant above, then diff "
    "environment and state between a failing and a succeeding run; promote "
    "the confirmed cause into a curated playbook.")


def _majority_category(pattern: ErrorPattern):
    cats = [m.category for m in pattern.members if m.category]
    if cats:
        return Counter(cats).most_common(1)[0][0]
    return None


def _top_variants(pattern: ErrorPattern, k: int = 3) -> List[str]:
    """Most frequent raw messages of the cluster, deduplicated."""
    seen: Dict[str, int] = {}
    for m in pattern.members:
        key = " ".join(m.normalized_message.split())[:160]
        seen.setdefault(key, 0)
        seen[key] += 1
    ranked = sorted(seen.items(), key=lambda kv: (-kv[1], kv[0]))
    return [msg for msg, _ in ranked[:k]]


def derive_action(pattern: ErrorPattern) -> str:
    lines = [f"No curated playbook exists yet for this failure "
             f"({pattern.frequency} occurrences across {pattern.sessions} "
             f"sessions). Most common forms observed:"]
    lines += [f"- \"{v}\"" for v in _top_variants(pattern)]
    lines.append(DERIVED_NEXT_STEP)
    return "\n".join(lines)


def choose_action(pattern: ErrorPattern,
                  authored: Dict | None = None) -> str:
    if authored and authored.get("action"):
        return authored["action"]
    cat = _majority_category(pattern)
    if cat in CATEGORY_ACTIONS:
        return CATEGORY_ACTIONS[cat]
    text = " ".join([pattern.summary()] + pattern.label_tokens)
    for rx, action in ACTION_RULES:
        if re.search(rx, text):
            return action
    return derive_action(pattern)


def build_description(pattern: ErrorPattern,
                      authored: Dict | None = None) -> str:
    agents = sorted({m.agent for m in pattern.members})
    agent_part = agents[0] if len(agents) == 1 else "/".join(agents[:3])
    base = (f"Recurring issue ({pattern.frequency}x across {pattern.sessions} "
            f"sessions, agent {agent_part}):")
    if authored and authored.get("lesson"):
        return f"{base} {authored['lesson']} First seen as: " \
               f"\"{_top_variants(pattern, 1)[0]}\""
    if _majority_category(pattern):
        return f"{base} [{_majority_category(pattern)}] {pattern.summary()}"
    return f"{base} {_top_variants(pattern, 1)[0]}"


def generate_reminders(patterns: List[ErrorPattern],
                       llm: LLMProvider | None = None) -> List[Reminder]:
    reminders: List[Reminder] = []
    for p in patterns:
        freq, sessions = p.frequency, p.sessions
        confidence = min(0.95, 0.35 + 0.12 * freq + 0.08 * sessions)
        authored = None
        if llm is not None:
            try:
                authored = llm.author_lesson(
                    [m.normalized_message for m in p.members[:5]])
            except Exception:
                authored = None  # enrichment must never gate generation
        reminders.append(Reminder(
            reminder_id=new_id("REM"),
            description=build_description(p, authored),
            trigger_context=list(p.label_tokens),
            recommended_action=choose_action(p, authored),
            evidence_log_ids=sorted(m.log_row_id for m in p.members),
            confidence=round(confidence, 2),
            frequency=freq,
            created_at=now_iso(),
            source_pattern_id=p.pattern_id,
        ))
    return reminders
