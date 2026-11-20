import os
import time
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import get_settings
from app.database.connection import get_db
from app.database.models import Alert
from app.schemas.models import HealthResponse, ComponentHealth

router = APIRouter(prefix="/health", tags=["Health"])
START_TIME = time.time()
settings = get_settings()

@router.get("", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """System health check and diagnostic status."""
    uptime = time.time() - START_TIME

    # Check Database
    db_status = "healthy"
    db_details = "Connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "degraded"
        db_details = f"Connection error: {str(e)}"

    # Check VirtualBox CLI
    vbox_status = "unavailable"
    vbox_details = "Not found"
    if os.path.exists(settings.VBOXMANAGE_PATH):
        vbox_status = "healthy"
        vbox_details = f"Found at {settings.VBOXMANAGE_PATH}"

    # Check Capture Tool (TShark/Dumpcap)
    cap_status = "unavailable"
    cap_details = "Wireshark/TShark not detected on default path"
    if os.path.exists(settings.TSHARK_PATH):
        cap_status = "healthy"
        cap_details = f"Found at {settings.TSHARK_PATH}"
    elif os.path.exists(settings.DUMPCAP_PATH):
        cap_status = "healthy"
        cap_details = f"Found at {settings.DUMPCAP_PATH}"

    # Active Threats
    try:
        active_threats = db.query(Alert).filter(Alert.status == "new").count()
    except Exception:
        active_threats = 0

    overall_status = "healthy" if db_status == "healthy" else "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        uptime_seconds=round(uptime, 2),
        timestamp=datetime.utcnow(),
        database=ComponentHealth(name="Database Engine", status=db_status, details=db_details),
        virtualbox=ComponentHealth(name="VirtualBox Management", status=vbox_status, details=vbox_details),
        capture_tool=ComponentHealth(name="Packet Capture Engine", status=cap_status, details=cap_details),
        active_threats=active_threats
    )
