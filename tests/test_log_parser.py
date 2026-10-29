from pathlib import Path

from src.log_parser import normalize_event, parse_file


FIXTURE = Path(__file__).with_name("sample_events.jsonl")


def test_parse_file_preserves_events_and_counts_bad_lines():
    events, diagnostics = parse_file(FIXTURE)

    assert len(events) == 3
    assert diagnostics.total_lines == 4
    assert diagnostics.parsed_lines == 3
    assert diagnostics.malformed_lines == 1
    assert events[0].source_ip == "192.0.2.10"
    assert events[1].command == "id"


def test_normalize_event_handles_missing_optional_fields():
    event = normalize_event({"eventid": "custom.event", "username": "guest"})

    assert event.event_type == "custom.event"
    assert event.username == "guest"
    assert event.source_ip is None
    assert event.timestamp is None


def test_normalize_event_classifies_cowrie_events_and_infers_login_outcome():
    success = normalize_event({"eventid": "cowrie.login.success"})
    command = normalize_event({"eventid": "cowrie.command.input", "input": "whoami"})
    session = normalize_event({"eventid": "cowrie.session.closed"})

    assert success.category == "authentication"
    assert success.success is True
    assert command.category == "command"
    assert command.command == "whoami"
    assert session.category == "session"


def test_parse_file_reports_blank_non_object_invalid_and_duplicate_records(tmp_path):
    fixture = tmp_path / "edge.jsonl"
    record = '{"eventid":"custom.event","timestamp":"not-a-timestamp"}'
    fixture.write_text(f"\n{record}\n{record}\n[]\nnot-json\n", encoding="utf-8")

    events, diagnostics = parse_file(fixture)

    assert len(events) == 2
    assert diagnostics.total_lines == 5
    assert diagnostics.blank_lines == 1
    assert diagnostics.non_object_records == 1
    assert diagnostics.malformed_lines == 1
    assert diagnostics.invalid_timestamps == 2
    assert diagnostics.duplicate_records == 1
    assert events[0].timestamp == "not-a-timestamp"


def test_parse_empty_file_returns_empty_result(tmp_path):
    fixture = tmp_path / "empty.jsonl"
    fixture.write_text("", encoding="utf-8")

    events, diagnostics = parse_file(fixture)

    assert events == []
    assert diagnostics.total_lines == 0
    assert diagnostics.errors == []
