# HACK THE HACKER — System Architecture & Data Pipeline

This document details the engineering architecture, telemetry pipeline, data models, and analytical engines comprising the **HACK THE HACKER** platform.

---

## 1. End-to-End Processing Pipeline

```
     Network Traffic (Npcap / VirtualBox NIC Trace / TShark)
                              |
                              v
                 Packet Capture (.pcap / .pcapng)
                              |
                              v
           Security Event Ingestion & Suricata EVE Logs
                              |
                              v
                   Event Normalization Layer
             (ISO UTC Timestamp, IP Standardization, Schema)
                              |
                              v
                Intrusion Detection Engine
        [Port Scan, Brute-Force, Suspicious Services, Anomaly]
                              |
                              v
                 Event Correlation Engine
        (Temporal Proximity, Source-Target Session Aggregation)
                              |
                              v
                Explainable Threat Scoring Engine
           (0.30*Sev + 0.25*Freq + 0.25*Behav + 0.20*Recur)
                              |
                              v
           Threat Intelligence Database (PostgreSQL / SQLite)
                              |
                              v
                FastAPI High-Performance Engine
                     (REST APIs & WebSocket)
                              |
                              v
                   React SOC Dashboard
        (Live Monitor, Timeline Analytics, Attack Trees)
```

---

## 2. Ingestion & Normalization

The ingestion layer (`backend/app/ingestion`) consumes:
1. **Suricata EVE JSON Logs:** Extracted from `/data/suricata_logs/eve.json` line-by-line using streaming buffers to conserve RAM.
2. **PCAP & PCAPNG Files:** Parsed via Scapy and TShark into flow records.
3. **Simulated Telemetry:** Injected via REST API for rule and regression testing.

### Normalized Event Schema
Every event conforms to the `Event` schema:
- `event_id`: Unique UUIDv4 identifier
- `timestamp`: UTC DateTime
- `source_ip`: IPv4 / IPv6 source string
- `destination_ip`: IPv4 / IPv6 destination string
- `source_port`: Integer TCP/UDP source port
- `destination_port`: Integer TCP/UDP destination port
- `protocol`: Transport protocol (`TCP`, `UDP`, `ICMP`)
- `event_type`: Detection classifier (e.g., `port_scan`, `brute_force`, `suricata_alert`)
- `severity`: Standardized tier (`Low`, `Moderate`, `High`, `Critical`)
- `sensor`: Originating sensor (`pcap_parser`, `suricata_eve`, `tshark`)
- `signature`: Human-readable threat signature
- `raw_evidence`: JSON-encoded packet/log forensic payload
- `related_attack_id`: Foreign key linking to an aggregated `AttackSession`

---

## 3. Detection & Behavioral Engines

1. **PortScanDetector (`port_scan_detector.py`):**
   - Employs a sliding-window algorithm tracking unique destination ports probed by each source IP.
   - Triggers a `Moderate` alert when exceeding 5 ports within 120s; escalates to `High` if exceeding 20 ports.

2. **BruteForceDetector (`brute_force_detector.py`):**
   - Monitors repeated authentication connection sequences against standard service ports (FTP 21, SSH 22, Telnet 23, HTTP 80, MySQL 3306).
   - Generates high-confidence alerts when connection frequency exceeds failure thresholds.

3. **SuspiciousConnectionDetector (`suspicious_connection_detector.py`):**
   - Identifies interactions with dangerous service ports, such as Metasploitable 2's root bindshell on port 1524 or UnrealIRCD backdoor on port 6667.

4. **AnomalyDetector (`anomaly_detector.py`):**
   - Uses Scikit-Learn's `IsolationForest` to analyze 3-dimensional behavioral feature vectors (Event Frequency, Unique Port Variety, Target Diversity).
   - Produces transparent anomaly scores without asserting unproven malice.

---

## 4. Threat Scoring & Explainability

Threat scores range from **0 to 100**, calculated per source IP:
$$\text{Score} = (0.30 \times S) + (0.25 \times F) + (0.25 \times B) + (0.20 \times R)$$
Where:
- **$S$ (Severity):** Highest alert severity triggered (Critical=100, High=75, Moderate=45, Low=15).
- **$F$ (Frequency):** Volume of observed packets and requests scaled non-linearly.
- **$B$ (Behavioral):** Port diversity and attack category flags.
- **$R$ (Recurrence):** Temporal duration of sustained adversarial activity.

Every score output includes an array of `reasons` explaining the exact contributing factors to the analyst.
