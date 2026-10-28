from src.data_processor import summarize_events
from src.log_parser import parse_file


def test_summary_counts_observed_values():
    events, _ = parse_file("tests/sample_events.jsonl")

    summary = summarize_events(events)

    assert summary["total_events"] == 3
    assert summary["unique_source_ips"] == 2
    assert summary["authentication_attempts"] == 2
    assert summary["usernames"]["admin"] == 1
    assert summary["commands"]["id"] == 1
