import json
import sys
import tempfile
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from reminder_system.analysis import identify_errors  # noqa: E402
from reminder_system.api import ApiServer             # noqa: E402
from reminder_system.ingest import ingest_file        # noqa: E402
from reminder_system.models import ErrorEvent, LogEntry  # noqa: E402
from reminder_system.patterns import extract_patterns  # noqa: E402
from reminder_system.pipeline import Pipeline          # noqa: E402
from reminder_system.providers import NullLLM, ScriptedLLM  # noqa: E402
from reminder_system.retrieval import ReminderService, Retriever  # noqa: E402
from reminder_system.reminders import generate_reminders  # noqa: E402
from reminder_system.store import Store                # noqa: E402

SAMPLE = ROOT / "data" / "sample_logs.jsonl"


def make_store():
    s = Store(":memory:")
    n, problems = ingest_file(SAMPLE, s)
    return s, n, problems


def build_pipeline(llm=None):
    p = Pipeline(Store(":memory:"), llm=llm or NullLLM())
    p.ingest_logs(SAMPLE)
    p.build_reminders()
    return p


class TestIngest(unittest.TestCase):
    def test_sample_ingests_with_one_skipped_line(self):
        store, n, problems = make_store()
        self.assertGreaterEqual(n, 20)
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

    def test_json_array_ingests_like_jsonl(self):
        """Regression: .json arrays used to crash with AttributeError."""
        docs = [
            {"session_id": "ja1", "timestamp": "t1", "agent": "a",
             "result": "success"},
            {"session_id": "ja2", "timestamp": "t2", "agent": "b",
             "error": "boom", "result": "failure"},
            {"timestamp": "missing session"},          # invalid -> counted
            "not an object at all",                    # invalid -> counted
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "batch.json"
            path.write_text(json.dumps(docs), encoding="utf-8")
            store = Store(":memory:")
            n, problems = ingest_file(str(path), store)
        self.assertEqual(n, 2)
        self.assertEqual(len(problems), 2)
        self.assertEqual(store.count("logs"), 2)

    def test_malformed_array_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "broken.json"
            path.write_text("{nope", encoding="utf-8")
            n, problems = ingest_file(str(path), Store(":memory:"))
        self.assertEqual(n, 0)
        self.assertTrue(problems and "invalid json" in problems[0])


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


def _ev(i, msg, session=None):
    return ErrorEvent(
        log_row_id=i, session_id=session or f"s{i}",
        timestamp=f"2026-01-01T00:00:{i % 60:02d}Z", agent="a",
        normalized_message=msg, raw_message=msg,
        signals=["error_field"])


class TestPatterns(unittest.TestCase):
    def test_finds_migration_and_rate_limit_patterns(self):
        store, _, _ = make_store()
        events = identify_errors(store.all_logs())
        pats = extract_patterns(events)
        labels = {" ".join(p.label_tokens) for p in pats}
        joined = " | ".join(labels)
        self.assertIn("migration", joined.lower())
        self.assertIn("limit", joined.lower())

    def test_identical_failures_across_sessions_cluster_together(self):
        """Regression: uncategorized events used to be welded onto the wrong
        (category) clusters by an index bug in the lexical fallback."""
        msgs = ["kafka consumer lag spike kills stream processor"] * 3
        evs = [_ev(i, m, session=f"sess{i}") for i, m in enumerate(msgs)]
        pats = extract_patterns(evs)
        self.assertEqual(len(pats), 1)
        self.assertEqual(pats[0].frequency, 3)

    def test_uncategorized_events_do_not_corrupt_category_clusters(self):
        store, _, _ = make_store()
        base_events = identify_errors(store.all_logs())
        base_pats = extract_patterns(base_events)
        cat_sizes = {" ".join(p.label_tokens): p.frequency
                     for p in base_pats if any(m.category for m in p.members)}

        injected = [
            {"session_id": f"inj{i}", "timestamp": f"2026-08-20T0{i}:00:00Z",
             "agent": "z", "result": "failure",
             "error": "kafka consumer lag spike kills stream processor"}
            for i in range(3)]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inj.jsonl"
            path.write_text("\n".join(json.dumps(d) for d in injected),
                            encoding="utf-8")
            s2 = Store(":memory:")
            ingest_file(SAMPLE, s2)
            ingest_file(str(path), s2)
            mixed_events = identify_errors(s2.all_logs())
            mixed_pats = extract_patterns(mixed_events)

        mixed_cat_sizes = {" ".join(p.label_tokens): p.frequency
                           for p in mixed_pats
                           if any(m.category for m in p.members)}
        self.assertEqual(cat_sizes, mixed_cat_sizes)

    def test_single_session_noise_is_not_a_pattern(self):
        evs = [_ev(i, "connection timeout after 30 seconds",
                   session="same-session") for i in range(4)]
        self.assertEqual(extract_patterns(evs), [])

    def test_cluster_spanning_two_sessions_becomes_pattern(self):
        evs = ([_ev(i, "connection timeout after 30 seconds",
                    session="same-session") for i in range(3)]
               + [_ev(9, "connection timeout after 30 seconds",
                      session="other-session")])
        pats = extract_patterns(evs)
        self.assertEqual(len(pats), 1)
        self.assertEqual(pats[0].frequency, 4)

    def test_below_min_frequency_dropped(self):
        evs = [_ev(1, "disk full on volume"), _ev(2, "disk full on volume")]
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
        actions = [r.recommended_action.lower() for r in rems]
        self.assertTrue(any("migration" in a for a in actions))
        self.assertTrue(any("backoff" in a for a in actions))

    def test_uncategorized_failure_gets_evidence_derived_action(self):
        """The old fallback was one hardcoded sentence for everything; now
        unknown recurring failures cite their own evidence."""
        rems, _ = self._reminders()
        derived = [r for r in rems if "fonts are subsetted" in r.description]
        self.assertEqual(len(derived), 1)
        action = derived[0].recommended_action
        self.assertIn("No curated playbook exists yet", action)
        self.assertIn("fonts are subsetted", action)   # cites evidence
        self.assertIn("Next step:", action)
        # description must also carry real provenance
        self.assertIn("across 3 sessions", derived[0].description)

    def test_llm_can_author_lesson_for_unknown_failure(self):
        scripted = ScriptedLLM([(
            "fonts",
            {"lesson": "Renderer drops the text layer when it subsets "
                       "embedded fonts.",
             "action": "Disable font subsetting or embed full font tables "
                       "until the renderer is fixed."})])
        p = build_pipeline(scripted)
        hits = [r for r in p.service.list_reminders()
                if "subsets embedded fonts".split()[0] in r.description
                or "text layer" in r.description]
        self.assertTrue(hits)
        self.assertIn("font subsetting", hits[0].recommended_action.lower())


class TestRetrieval(unittest.TestCase):
    NEGATIVE_QUERIES = [
        "retry the flaky ui animation assertion",
        "refactor module structure into smaller files",
        "rename variables for readability",
        "add a dark mode toggle to the settings page",
        "write docstrings for public functions",
        "upgrade eslint config to the flat format",
        "remove console log statements from the frontend",
        "split this component into two files",
        "translate the onboarding copy to german",
        "set up prettier formatting rules",
        "fix typo in contributing guide",
        "benchmark sorting algorithm implementations",
        "clean up unused imports across the project",
        "add keyboard shortcuts for undo redo",
        "update copyright year in footer",
        "configure git aliases for common commands",
        "write release notes for version two point one",
        "mock the file system in unit tests",
        "compress screenshots before uploading assets",
        "document environment variables in readme",
    ]

    def _service(self):
        return build_pipeline().service

    def test_schema_query_ranks_migration_reminder_first(self):
        svc = self._service()
        hits = svc.query("add a new column to the users table")
        self.assertTrue(hits)
        self.assertIn("migration", hits[0].reminder.recommended_action.lower())

    def test_api_query_ranks_backoff_first(self):
        svc = self._service()
        hits = svc.query("call the shipping rates API for all zones")
        self.assertTrue(hits)
        self.assertIn("backoff", hits[0].reminder.recommended_action.lower())

    def test_adversarial_battery_fires_nothing(self):
        """Reviewer probe + 19 unrelated dev requests: none may trigger a
        reminder. This is the regression battery for retrieval calibration."""
        svc = self._service()
        for q in self.NEGATIVE_QUERIES:
            hits = svc.query(q)
            self.assertEqual(
                hits, [],
                f"false positive for {q!r}: "
                f"{[(h.reminder.reminder_id, h.relevance) for h in hits]}")

    def test_relevance_separates_direct_from_expanded_matches(self):
        svc = self._service()
        direct = svc.query("deploy failed missing migration schema drift")
        expanded = svc.query("add a new column to the users table")
        self.assertTrue(direct and expanded)
        self.assertGreater(direct[0].relevance, expanded[0].relevance)

    def test_top_k_respected(self):
        svc = self._service()
        hits = svc.query("schema migration database deploy failure rate limit api",
                         top_k=1)
        self.assertLessEqual(len(hits), 1)

    def test_persistence_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            db = str(Path(td) / "r.db")
            p1 = Pipeline(Store(db))
            p1.ingest_logs(SAMPLE)
            p1.build_reminders()
            before = [r.to_dict() for r in p1.service.list_reminders()]
            p1.store.close()

            after = [r.to_dict()
                     for r in ReminderService(Store(db)).list_reminders()]
        self.assertEqual(before, after)


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.srv = ApiServer(build_pipeline().service, port=0)
        self.srv.__enter__()

    def tearDown(self):
        self.srv.__exit__(None, None, None)

    def test_health(self):
        with urllib.request.urlopen(self.srv.url + "/health") as resp:
            data = json.loads(resp.read())
        self.assertEqual(data["status"], "ok")

    def test_list_reminders_endpoint_thread_safe(self):
        """Regression: GET /reminders used to raise sqlite3.ProgrammingError
        because worker threads touched a main-thread connection."""
        def fetch(_):
            with urllib.request.urlopen(self.srv.url + "/reminders") as resp:
                return resp.status
        with ThreadPoolExecutor(max_workers=8) as ex:
            codes = list(ex.map(fetch, range(24)))
        self.assertEqual(codes, [200] * 24)
        with urllib.request.urlopen(self.srv.url + "/reminders") as resp:
            data = json.loads(resp.read())
        self.assertGreaterEqual(len(data["reminders"]), 3)

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
    """Proves both LLM seams: enrichment can discover patterns rules cannot,
    and author lessons rules cannot — without changing the base path."""

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
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extra.jsonl"
            path.write_text(
                "\n".join(json.dumps(e) for e in self.EXTRA),
                encoding="utf-8")
            p = Pipeline(Store(":memory:"), llm=llm)
            p.ingest_logs(SAMPLE)
            p.ingest_logs(str(path))
            p.build_reminders()
        return p

    def test_enrichment_discovers_pattern_rules_cannot(self):
        scripted = ScriptedLLM([
            ("connection", {"category": "database_connection_drop",
                            "summary": None})])
        base = self._pipeline(NullLLM())
        enriched = self._pipeline(scripted)
        self.assertLess(base.stats.patterns_found, enriched.stats.patterns_found)

    def test_null_llm_matches_default_pipeline(self):
        """Regression: this assertion used to be tautological (`x or x`)."""
        explicit = build_pipeline(NullLLM()).stats
        default = build_pipeline(None).stats
        self.assertEqual(explicit.patterns_found, default.patterns_found)
        self.assertEqual(explicit.reminders_built, default.reminders_built)
        self.assertGreater(default.patterns_found, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
