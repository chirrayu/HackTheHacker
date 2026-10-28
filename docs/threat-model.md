# Threat model

## Assets

- The isolated VM and its recovery image.
- Honeypot telemetry, including source IPs, usernames, passwords, commands, and sessions.
- Optional provider credentials and notification credentials.

## Primary risks

- A compromised honeypot becomes a pivot into the host or adjacent networks.
- Raw telemetry exposes personal or sensitive information.
- Captured commands are accidentally executed by analysis tooling.
- External enrichment leaks data or creates inaccurate claims.
- Alerts expose secrets through logs or third-party services.

## Controls

- Host-only or restricted networking, least privilege, snapshots, and a documented recovery test.
- Synthetic fixtures and redaction before publication.
- Parser and dashboard treat attacker-controlled strings as data only.
- Enrichment is optional, timeout-bounded, and contextual rather than proof of malicious intent.
- Credentials come from environment variables and are never committed.
