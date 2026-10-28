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
