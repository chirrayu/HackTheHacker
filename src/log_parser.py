"""Safe parsing and normalization for Cowrie-style JSON Lines events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Iterator, Mapping


@dataclass(frozen=True)
class NormalizedEvent:
    """A normalized event with raw data preserved for traceability."""

    event_type: str
    timestamp: str | None = None
    source_ip: str | None = None
    session_id: str | None = None
    username: str | None = None
    password: str | None = None
    command: str | None = None
    success: bool | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ParseDiagnostics:
    """Counters and line-level errors produced while parsing a JSONL file."""

    total_lines: int = 0
    parsed_lines: int = 0
    malformed_lines: int = 0
    non_object_records: int = 0
    errors: list[str] = field(default_factory=list)


def _first(record: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value is not None and value != "":
            return value
    return None


def _normalize_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return text


def normalize_event(record: Mapping[str, Any]) -> NormalizedEvent:
    """Normalize common Cowrie fields without inventing absent values."""

    event_type = str(_first(record, "eventid", "event_type", "event", "type") or "unknown")
    success = _first(record, "success", "is_success", "authenticated")
    if isinstance(success, str):
        success = success.lower() in {"1", "true", "yes", "success", "succeeded"}
    elif not isinstance(success, bool):
        success = None
    return NormalizedEvent(
        event_type=event_type,
        timestamp=_normalize_timestamp(_first(record, "timestamp", "time")),
        source_ip=_first(record, "src_ip", "source_ip", "peerIP", "ip"),
        session_id=_first(record, "session", "session_id", "sensor"),
        username=_first(record, "username", "user", "input" if event_type == "cowrie.login.failed" else "username"),
        password=_first(record, "password", "pass"),
        command=_first(record, "input" if event_type in {"cowrie.command.input", "command"} else "command"),
        success=success,
        raw=dict(record),
    )


def iter_events(path: str | Path, diagnostics: ParseDiagnostics | None = None) -> Iterator[NormalizedEvent]:
    """Yield valid normalized events and record malformed input diagnostics."""

    report = diagnostics if diagnostics is not None else ParseDiagnostics()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            report.total_lines += 1
            text = line.strip()
            if not text:
                continue
            try:
                record = json.loads(text)
            except json.JSONDecodeError as exc:
                report.malformed_lines += 1
                report.errors.append(f"line {line_number}: malformed JSON ({exc.msg})")
                continue
            if not isinstance(record, dict):
                report.non_object_records += 1
                report.errors.append(f"line {line_number}: JSON record is not an object")
                continue
            report.parsed_lines += 1
            yield normalize_event(record)


def parse_file(path: str | Path) -> tuple[list[NormalizedEvent], ParseDiagnostics]:
    """Parse a complete JSONL file and return events plus diagnostics."""

    diagnostics = ParseDiagnostics()
    return list(iter_events(path, diagnostics)), diagnostics
