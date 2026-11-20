import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database.connection import get_db
from app.ingestion.event_ingestor import EventIngestor
from app.ingestion.pcap_parser import PcapParser
from app.ingestion.suricata_parser import SuricataParser
from app.detection.rule_engine import DetectionEngine
from app.intelligence.correlation import EventCorrelationEngine
from app.schemas.models import EventCreate

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])
settings = get_settings()

@router.post("/pcap")
async def ingest_pcap(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and parse a PCAP/PCAPNG capture file."""
    if not (file.filename.endswith(".pcap") or file.filename.endswith(".pcapng") or file.filename.endswith(".cap")):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be .pcap or .pcapng")

    os.makedirs(settings.PCAP_UPLOAD_DIR, exist_ok=True)
    target_path = os.path.join(settings.PCAP_UPLOAD_DIR, f"{int(datetime.utcnow().timestamp())}_{file.filename}")

    # Enforce size limit while writing
    max_bytes = settings.MAX_PCAP_SIZE_MB * 1024 * 1024
    bytes_written = 0
    with open(target_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            bytes_written += len(chunk)
            if bytes_written > max_bytes:
                buffer.close()
                os.remove(target_path)
                raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size ({settings.MAX_PCAP_SIZE_MB}MB)")
            buffer.write(chunk)

    # Parse PCAP
    events = PcapParser.parse_file(target_path)
    ingestor = EventIngestor(db)
    count = ingestor.ingest_batch(events)

    # Run Detection & Correlation
    detector = DetectionEngine()
    alerts = detector.run_all(db)
    sessions = EventCorrelationEngine.correlate_sessions(db)

    return {
        "status": "success",
        "filename": file.filename,
        "saved_to": target_path,
        "events_ingested": count,
        "alerts_triggered": len(alerts),
        "attack_sessions_updated": len(sessions)
    }

@router.post("/suricata")
async def ingest_suricata(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and ingest a Suricata EVE JSON log file (eve.json)."""
    os.makedirs(settings.SURICATA_LOG_DIR, exist_ok=True)
    target_path = os.path.join(settings.SURICATA_LOG_DIR, f"{int(datetime.utcnow().timestamp())}_{file.filename}")

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    events = SuricataParser.parse_eve_log(target_path)
    ingestor = EventIngestor(db)
    count = ingestor.ingest_batch(events)

    detector = DetectionEngine()
    alerts = detector.run_all(db)
    sessions = EventCorrelationEngine.correlate_sessions(db)

    return {
        "status": "success",
        "filename": file.filename,
        "events_ingested": count,
        "alerts_triggered": len(alerts),
        "attack_sessions_updated": len(sessions)
    }

@router.post("/simulate")
def inject_simulated_event(event_data: EventCreate, db: Session = Depends(get_db)):
    """
    Directly inject an event into the processing pipeline for testing.
    Clearly marked as simulated.
    """
    event_data.sensor = "simulation_fixture"
    ingestor = EventIngestor(db)
    event = ingestor.ingest_single_event(event_data)

    detector = DetectionEngine()
    alerts = detector.run_all(db)
    EventCorrelationEngine.correlate_sessions(db)

    return {
        "status": "success",
        "event_id": event.id,
        "alerts_generated": len(alerts)
    }
