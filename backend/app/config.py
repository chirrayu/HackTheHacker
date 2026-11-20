import os
from pathlib import Path
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings

# Base project directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
backend_posix = str(BACKEND_DIR).replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "HACK THE HACKER"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database (PostgreSQL URL + properly formatted SQLite fallback for Windows)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/hackthehacker"
    SQLITE_FALLBACK_URL: str = f"sqlite:///{backend_posix}/hackthehacker.db"
    USE_SQLITE_FALLBACK: bool = True
    
    # Security
    SECRET_KEY: str = "dev-secret-key-replace-in-production-hackthehacker"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Directories
    LOG_DIR: str = str(PROJECT_DIR / "logs")
    PCAP_UPLOAD_DIR: str = str(PROJECT_DIR / "data" / "pcap_uploads")
    SURICATA_LOG_DIR: str = str(PROJECT_DIR / "data" / "suricata_logs")
    MAX_PCAP_SIZE_MB: int = 100
    
    # Lab Network
    LAB_NETWORK: str = "192.168.56.0/24"
    WINDOWS_HOST_IP: str = "192.168.56.1"
    KALI_IP: str = "192.168.56.20"
    METASPLOITABLE_IP: str = "192.168.56.30"
    
    # Tool Paths
    TSHARK_PATH: str = r"C:\Program Files\Wireshark\tshark.exe"
    DUMPCAP_PATH: str = r"C:\Program Files\Wireshark\dumpcap.exe"
    VBOXMANAGE_PATH: str = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = str(BACKEND_DIR / ".env")
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
