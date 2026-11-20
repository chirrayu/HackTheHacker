import os
from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(prefix="/sensors", tags=["Sensors"])
settings = get_settings()

@router.get("/status")
def get_sensor_status():
    """Returns the operational status of capture sensors on the Windows host."""
    tshark_ok = os.path.exists(settings.TSHARK_PATH)
    dumpcap_ok = os.path.exists(settings.DUMPCAP_PATH)
    vbox_ok = os.path.exists(settings.VBOXMANAGE_PATH)

    return {
        "lab_network": settings.LAB_NETWORK,
        "monitored_interface": "VirtualBox Host-Only Ethernet Adapter",
        "sensors": [
            {
                "name": "TShark/Dumpcap Packet Sniffer",
                "type": "Network Packet Capture",
                "installed": tshark_ok or dumpcap_ok,
                "executable": settings.TSHARK_PATH if tshark_ok else settings.DUMPCAP_PATH,
                "status": "ready" if (tshark_ok or dumpcap_ok) else "not_installed"
            },
            {
                "name": "Suricata IDS Log Ingestion",
                "type": "EVE JSON File Ingestor",
                "installed": True,
                "log_dir": settings.SURICATA_LOG_DIR,
                "status": "ready"
            },
            {
                "name": "VirtualBox Internal NIC Trace Integration",
                "type": "Hypervisor Packet Dump",
                "installed": vbox_ok,
                "executable": settings.VBOXMANAGE_PATH,
                "status": "ready" if vbox_ok else "not_installed"
            }
        ]
    }
