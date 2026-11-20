import json
import os
import logging
from typing import List
from app.ingestion.normalizer import EventNormalizer
from app.schemas.models import EventCreate

logger = logging.getLogger("hackthehacker.suricata_parser")

class SuricataParser:
    """
    Parses Suricata EVE JSON log files (`eve.json`).
    Streams line by line to minimize memory footprint on 16GB RAM machines.
    """

    @classmethod
    def parse_eve_log(cls, filepath: str, max_records: int = 10000) -> List[EventCreate]:
        """Reads eve.json and converts valid records into normalized EventCreate instances."""
        if not os.path.exists(filepath):
            logger.error(f"Suricata EVE log not found at: {filepath}")
            return []

        events: List[EventCreate] = []
        parsed_count = 0
        error_count = 0

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if parsed_count >= max_records:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                        event = EventNormalizer.from_suricata_eve(record)
                        if event:
                            events.append(event)
                            parsed_count += 1
                    except json.JSONDecodeError:
                        error_count += 1
                        continue

            logger.info(f"Parsed {parsed_count} Suricata events from {filepath} (Skipped {error_count} malformed lines).")
            return events

        except Exception as e:
            logger.error(f"Failed to read Suricata log {filepath}: {e}")
            return []
