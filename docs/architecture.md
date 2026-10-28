# Architecture

HackTheHacker follows a local-first, defensive data flow:

1. Cowrie records authorized honeypot activity as JSON Lines.
2. `src.log_parser` reads records independently, preserves raw fields, normalizes common names, and reports malformed input without executing captured content.
3. `src.data_processor` derives transparent counts from normalized events.
4. The dashboard will consume those same parser and processor interfaces; it will not duplicate parsing logic.
5. Optional enrichment and notifications remain isolated integrations and must not prevent local analytics when unavailable.

The raw input is treated as untrusted data. Commands are displayed as text only and are never executed.
