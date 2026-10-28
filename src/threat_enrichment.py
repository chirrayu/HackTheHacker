"""Optional, failure-tolerant threat-intelligence interfaces."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any


@dataclass(frozen=True)
class EnrichmentResult:
    """Context returned by an enrichment provider, never a verdict."""

    ip_address: str
    provider: str
    available: bool
    retrieved_at: str | None = None
    data: dict[str, Any] | None = None
    error: str | None = None


def configured_provider() -> str | None:
    """Return the explicitly configured provider name without exposing secrets."""

    provider = os.getenv("HACKTHEHACKER_TI_PROVIDER", "").strip().lower()
    return provider or None


def unavailable_result(ip_address: str, provider: str = "none", error: str = "not configured") -> EnrichmentResult:
    """Create a safe result for unavailable or disabled enrichment."""

    return EnrichmentResult(ip_address=ip_address, provider=provider, available=False, error=error)
