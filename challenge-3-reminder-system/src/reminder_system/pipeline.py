"""End-to-end pipeline: ingest -> identify errors -> find patterns ->
generate reminders -> persist -> (re)build retrieval index.

Usage:
    from reminder_system.pipeline import Pipeline
    p = Pipeline(Store("reminders.db"))
    stats = p.ingest_logs("logs.jsonl")
    built = p.build_reminders()
    hits  = p.service.query("add a column to users table")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .analysis import identify_errors
from .ingest import ingest_file
from .patterns import extract_patterns
from .providers import LLMProvider, NullLLM
from .retrieval import ReminderService
from .reminders import generate_reminders
from .store import Store


@dataclass
class PipelineStats:
    logs_ingested: int = 0
    ingestion_problems: list = field(default_factory=list)
    error_events: int = 0
    patterns_found: int = 0
    reminders_built: int = 0

    def to_dict(self) -> Dict:
        return {
            "logs_ingested": self.logs_ingested,
            "ingestion_problems": self.ingestion_problems,
            "error_events": self.error_events,
            "patterns_found": self.patterns_found,
            "reminders_built": self.reminders_built,
        }


class Pipeline:
    def __init__(self, store: Store,
                 llm: LLMProvider | None = None):
        self.store = store
        self.llm = llm or NullLLM()
        self.stats = PipelineStats()
        self.service = ReminderService(store)

    def ingest_logs(self, path) -> PipelineStats:
        n, problems = ingest_file(path, self.store)
        self.stats.logs_ingested += n
        self.stats.ingestion_problems.extend(problems)
        return self.stats

    def build_reminders(self) -> PipelineStats:
        logs = self.store.all_logs()
        events = identify_errors(logs, self.llm)
        patterns = extract_patterns(events)
        reminders = generate_reminders(patterns)
        self.store.replace_reminders(reminders)
        self.service.refresh()
        self.stats.error_events = len(events)
        self.stats.patterns_found = len(patterns)
        self.stats.reminders_built = len(reminders)
        return self.stats
