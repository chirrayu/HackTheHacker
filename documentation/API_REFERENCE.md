# HACK THE HACKER — REST API Reference

The FastAPI backend exposes all REST endpoints under `/api/v1`. Interactive documentation is available via Swagger UI at `http://localhost:8000/docs`.

---

## Endpoints

### 1. Health & Sensor Status
- `GET /api/v1/health`
  Returns platform status, component connectivity (Database, VirtualBox, Packet Capture), uptime, and active alert counts.
- `GET /api/v1/sensors/status`
  Returns operational status of local packet sniffers and log directory paths.

### 2. Events & Telemetry
- `GET /api/v1/events`
  Query parameters: `source_ip`, `destination_ip`, `severity`, `event_type`, `limit`, `offset`.
  Returns paginated list of normalized security events.

### 3. Security Alerts
- `GET /api/v1/alerts`
  Query parameters: `severity`, `status`, `source_ip`, `limit`, `offset`.
  Returns detection alerts triggered by rule engines.
- `PATCH /api/v1/alerts/{alert_id}/status`
  Update alert triage state (`new`, `investigating`, `acknowledged`, `resolved`).

### 4. Attack Sessions & Correlation
- `GET /api/v1/attacks`
  Returns correlated attack chains grouped by adversary source IP and destination target.
- `GET /api/v1/attacks/{session_id}/timeline`
  Returns chronologically ordered events and correlated alerts for an attack session.

### 5. Asset Catalog
- `GET /api/v1/assets`
  Returns monitored and discovered network nodes, open services, and observation times.

### 6. Analytics & Intelligence
- `GET /api/v1/analytics/overview`
  Summary statistics, severity breakdown, top sources, and activity timeline for the SOC Overview dashboard.
- `GET /api/v1/analytics/timeline`
  Returns hourly event and alert trends for time-series charts.
- `GET /api/v1/intelligence/top-sources`
  Returns highest-risk communicating source IPs ranked by calculated threat score.
- `GET /api/v1/intelligence/score/{source_ip}`
  Calculates and returns an explainable risk score (0-100) with detailed contributing factors.

### 7. File Ingestion
- `POST /api/v1/ingestion/pcap`
  Upload and ingest a `.pcap` or `.pcapng` capture file. Automatically extracts flows, runs detection passes, and correlates attack sessions.
- `POST /api/v1/ingestion/suricata`
  Upload and ingest a Suricata `eve.json` log file.
- `POST /api/v1/ingestion/simulate`
  Inject a simulated event fixture for automated testing.

### 8. Executive Reports
- `GET /api/v1/reports`
  Returns historical generated security reports.
- `POST /api/v1/reports/generate`
  Synthesizes an executive threat report over a specified time window (`time_period_hours`).

### 9. Real-Time WebSockets
- `WebSocket /ws/alerts`
  Bidirectional WebSocket for live alert broadcasting to the React SOC dashboard.
