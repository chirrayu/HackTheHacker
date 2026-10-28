"""Deterministic summaries for normalized honeypot events."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Iterable

from .log_parser import NormalizedEvent


def summarize_events(events: Iterable[NormalizedEvent]) -> dict[str, object]:
    """Return explainable counts and frequency tables from observed events."""

    items = list(events)
    source_ips = Counter(event.source_ip for event in items if event.source_ip)
    usernames = Counter(event.username for event in items if event.username)
    passwords = Counter(event.password for event in items if event.password)
    commands = Counter(event.command for event in items if event.command)
    event_types = Counter(event.event_type for event in items)
    return {
        "total_events": len(items),
        "unique_source_ips": len(source_ips),
        "authentication_attempts": sum(
            event.event_type in {"cowrie.login.failed", "cowrie.login.success"} for event in items
        ),
        "event_types": dict(event_types.most_common()),
        "source_ips": dict(source_ips.most_common()),
        "usernames": dict(usernames.most_common()),
        "passwords": dict(passwords.most_common()),
        "commands": dict(commands.most_common()),
    }


def events_as_records(events: Iterable[NormalizedEvent]) -> list[dict[str, object]]:
    """Convert normalized events into serializable records for dashboard use."""

    return [asdict(event) for event in events]
