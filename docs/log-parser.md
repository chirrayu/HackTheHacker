# Phase 3: JSONL log parser

The parser consumes Cowrie-style JSON Lines files without executing or interpreting captured strings.

```python
from src.log_parser import parse_file

events, diagnostics = parse_file("sanitized-events.jsonl")
```

`NormalizedEvent` keeps the original record in `raw` and exposes common fields such as `event_type`, `timestamp`, `source_ip`, `session_id`, `username`, `password`, `command`, `success`, and `category`.

`ParseDiagnostics` reports total lines, parsed records, blank lines, malformed JSON, non-object JSON values, invalid timestamps, duplicate records, and line-level messages. Invalid timestamps are preserved as text for traceability; malformed and non-object records are skipped because they cannot be normalized safely.

The parser preserves duplicate records and counts them rather than silently deduplicating observations. Raw production logs, credentials, and session transcripts must remain inside the isolated VM. Use synthetic or sanitized fixtures for repository tests and reports.
