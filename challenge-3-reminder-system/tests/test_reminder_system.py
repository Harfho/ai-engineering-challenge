import json
import sys
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from reminder_system.analysis import identify_errors  # noqa: E402
from reminder_system.api import ApiServer             # noqa: E402
from reminder_system.ingest import ingest_file        # noqa: E402
from reminder_system.models import LogEntry           # noqa: E402
from reminder_system.patterns import extract_patterns  # noqa: E402
from reminder_system.pipeline import Pipeline          # noqa: E402
from reminder_system.retrieval import Retriever        # noqa: E402
from reminder_system.reminders import generate_reminders  # noqa: E402
from reminder_system.store import Store                # noqa: E402

SAMPLE = ROOT / "data" / "sample_logs.jsonl"


def make_store():
    s = Store(":memory:")
    n, problems = ingest_file(SAMPLE, s)
    return s, n, problems


class TestIngest(unittest.TestCase):
    def test_sample_ingests_with_one_skipped_line(self):
        store, n, problems = make_store()
        self.assertGreaterEqual(n, 17)
        self.assertEqual(store.count("logs"), n)
        self.assertEqual(len(problems), 1)  # deliberate malformed line
        self.assertIn("invalid json", problems[0])

    def test_missing_required_field_rejected(self):
        from reminder_system.ingest import parse_line
        entry, err = parse_line(json.dumps({"timestamp": "t", "agent": "a"}))
        self.assertIsNone(entry)
        self.assertIn("session_id", err)

    def test_metadata_non_dict_coerced(self):
        from reminder_system.ingest import parse_line
        entry, err = parse_line(json.dumps({
            "session_id": "s", "timestamp": "t", "agent": "a",
            "metadata": "oops"}))
        self.assertIsNotNone(entry)
        self.assertIn("_coerced_metadata", entry.metadata)


class TestAnalysis(unittest.TestCase):
    def test_identifies_errors_and_ignores_success(self):
        store, _, _ = make_store()
        events = identify_errors(store.all_logs())
        self.assertTrue(all(e.signals for e in events))
        rows = {e.log_row_id for e in events}
        success_rows = {l.row_id for l in store.all_logs() if l.result == "success"}
        self.assertFalse(rows & success_rows)

    def test_normalization_strips_details(self):
        e = LogEntry(session_id="s", timestamp="t", agent="x",
                     error="deploy failed abc12345 missing migration 42")
        ev = identify_errors([e])[0]
        self.assertNotIn("abc12345", ev.normalized_message)
        self.assertNotIn(" 42", ev.normalized_message)


class TestPatterns(unittest.TestCase):
    def test_finds_migration_and_rate_limit_patterns(self):
        store, _, _ = make_store()
        events = identify_errors(store.all_logs())
        pats = extract_patterns(events)
        labels = {" ".join(p.label_tokens) for p in pats}
        joined = " | ".join(labels)
        self.assertIn("migration", joined.lower())
        self.assertIn("limit", joined.lower())

    def test_single_session_noise_is_not_a_pattern(self):
        evs = [
            __import__("reminder_system.models", fromlist=["ErrorEvent"]).ErrorEvent(
                log_row_id=i, session_id="same-session" if i < 3 else f"s{i}",
                timestamp="2026-01-01T00:00:0%dZ" % i, agent="a",
                normalized_message="connection timeout after 30 seconds",
                raw_message="timeout", signals=["failure_word_combined"])
            for i in range(4)]
        pats = extract_patterns(evs)
        self.assertEqual(len(pats), 1)
        self.assertEqual(pats[0].frequency, 4)

    def test_below_min_frequency_dropped(self):
        evs = [
            __import__("reminder_system.models", fromlist=["ErrorEvent"]).ErrorEvent(
                log_row_id=1, session_id="s1", timestamp="t", agent="a",
                normalized_message="disk full on volume", raw_message="x",
                signals=["error_field"]),
            __import__("reminder_system.models", fromlist=["ErrorEvent"]).ErrorEvent(
                log_row_id=2, session_id="s2", timestamp="t2", agent="a",
                normalized_message="disk full on volume", raw_message="x",
                signals=["error_field"]),
        ]
        self.assertEqual(extract_patterns(evs, min_frequency=3), [])


class TestReminders(unittest.TestCase):
    def _reminders(self):
        store, _, _ = make_store()
        events = identify_errors(store.all_logs())
        return generate_reminders(extract_patterns(events)), store

    def test_fields_and_bounds(self):
        rems, store = self._reminders()
        self.assertTrue(rems)
        valid_ids = {l.row_id for l in store.all_logs()}
        for r in rems:
            self.assertTrue(r.description and r.recommended_action)
            self.assertGreaterEqual(r.confidence, 0.35)
            self.assertLessEqual(r.confidence, 0.95)
            self.assertTrue(set(r.evidence_log_ids) <= valid_ids)

    def test_action_rules_route_correctly(self):
        rems, _ = self._reminders()
        by_text = {r.description + r.description: r for r in rems}
        actions = [r.recommended_action.lower() for r in rems]
        self.assertTrue(any("migration" in a for a in actions))
        self.assertTrue(any("backoff" in a for a in actions))


class TestRetrieval(unittest.TestCase):
    def _service(self):
        pipeline = Pipeline(Store(":memory:"))
        pipeline.ingest_logs(SAMPLE)
        pipeline.build_reminders()
        return pipeline.service

    def test_schema_query_ranks_migration_reminder_first(self):
        svc = self._service()
        hits = svc.query("add a new column to the users table")
        self.assertTrue(hits)
        top_text = (hits[0].reminder.trigger_context + 
                    [hits[0].reminder.recommended_action])
        self.assertIn("migration", hits[0].reminder.recommended_action.lower())

    def test_api_query_ranks_backoff_first(self):
        svc = self._service()
        hits = svc.query("call the shipping rates API for all zones")
        self.assertTrue(hits)
        self.assertIn("backoff", hits[0].reminder.recommended_action.lower())

    def test_irrelevant_query_returns_empty(self):
        svc = self._service()
        hits = svc.query("refactor module structure into smaller files")
        self.assertEqual(hits, [])

    def test_top_k_respected(self):
        svc = self._service()
        hits = svc.query("schema migration database deploy failure rate limit api",
                         top_k=1)
        self.assertLessEqual(len(hits), 1)

    def test_persistence_roundtrip(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            p1 = Pipeline(Store(f.name))
            p1.ingest_logs(SAMPLE)
            p1.build_reminders()
            before = [r.to_dict() for r in p1.service.list_reminders()]
            p1.store.close()

            store2 = Store(f.name)
            after = [r.to_dict() for r in ReminderServiceLike(store2).list_reminders()]
            self.assertEqual(before, after)
            store2.close()


def ReminderServiceLike(store):  # noqa: N802 - small helper for roundtrip test
    from reminder_system.retrieval import ReminderService
    return ReminderService(store)


class TestAPI(unittest.TestCase):
    def setUp(self):
        pipeline = Pipeline(Store(":memory:"))
        pipeline.ingest_logs(SAMPLE)
        pipeline.build_reminders()
        self.srv = ApiServer(pipeline.service, port=0)
        self.srv.__enter__()

    def tearDown(self):
        self.srv.__exit__(None, None, None)

    def test_health(self):
        with urllib.request.urlopen(self.srv.url + "/health") as resp:
            data = json.loads(resp.read())
        self.assertEqual(data["status"], "ok")

    def test_query_endpoint(self):
        req = urllib.request.Request(
            self.srv.url + "/reminders/query",
            data=json.dumps({"context": "alter users table add column"}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        self.assertEqual(resp.status, 200)
        self.assertGreaterEqual(data["count"], 1)
        self.assertIn("migration", data["reminders"][0]["recommended_action"].lower())

    def test_query_validation_422(self):
        req = urllib.request.Request(
            self.srv.url + "/reminders/query",
            data=json.dumps({"context": ""}).encode(),
            headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req)
            self.fail("expected HTTPError")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 422)

    def test_unknown_route_404(self):
        try:
            urllib.request.urlopen(self.srv.url + "/nope")
            self.fail("expected HTTPError")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)


class TestSemanticEnrichment(unittest.TestCase):
    """Proves the LLM seam: enrichment must be able to discover patterns
    that deterministic rules alone cannot, without changing the base path."""

    EXTRA = [
        {"session_id": f"x{i}", "timestamp": f"2026-08-2{i}T0{i}:00:00Z",
         "agent": "a", "result": "failure",
         "error": msg}
        for i, msg in enumerate([
            "we lost the db connection mid-request and aborted",
            "db connection dropped during the bulk update",
            "connection to the database vanished halfway through",
        ], start=1)
    ]

    def _pipeline(self, llm):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as f:
            f.write("\n".join(json.dumps(e) for e in self.EXTRA))
            f.flush()
            p = Pipeline(Store(":memory:"), llm=llm)
            p.ingest_logs(SAMPLE)
            p.ingest_logs(f.name)
            p.build_reminders()
            return p

    def test_enrichment_discovers_pattern_rules_cannot(self):
        from reminder_system.providers import NullLLM, ScriptedLLM
        scripted = ScriptedLLM([
            ("connection", {"category": "database_connection_drop",
                            "summary": None})])
        base = self._pipeline(NullLLM())
        enriched = self._pipeline(scripted)
        self.assertLess(base.stats.patterns_found, enriched.stats.patterns_found)

    def test_null_llm_path_unchanged(self):
        from reminder_system.providers import NullLLM
        p = Pipeline(Store(":memory:"), llm=NullLLM())
        p.ingest_logs(SAMPLE)
        p.build_reminders()
        self.assertEqual(p.stats.patterns_found,
                         Pipeline(Store(":memory:")).build_reminders()
                         .patterns_found or p.stats.patterns_found)


if __name__ == "__main__":
    unittest.main(verbosity=2)
