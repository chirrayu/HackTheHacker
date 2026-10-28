"""Notification boundary with no network side effects by default."""

from __future__ import annotations

import logging
import os
from typing import Mapping

LOGGER = logging.getLogger(__name__)


def notify(message: str, context: Mapping[str, object] | None = None) -> bool:
    """Log a notification request only when an explicit notifier is configured.

    Provider integrations are intentionally not enabled by this baseline module.
    Captured commands and credentials must not be included in notification text.
    """

    provider = os.getenv("HACKTHEHACKER_ALERT_PROVIDER", "").strip().lower()
    if not provider:
        LOGGER.info("Alert suppressed because no provider is configured: %s", message)
        return False
    LOGGER.warning("Alert provider %s is configured but has no implementation", provider)
    return False
