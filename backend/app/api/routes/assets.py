import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Asset
from app.schemas.models import AssetResponse

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("", response_model=List[AssetResponse])
def get_assets(db: Session = Depends(get_db)):
    """List all monitored, discovered, and lab assets."""
    assets = db.query(Asset).order_by(Asset.last_seen.desc()).all()
    res = []
    for a in assets:
        services = json.loads(a.services) if a.services else []
        res.append(AssetResponse(
            id=a.id,
            ip_address=a.ip_address,
            hostname=a.hostname,
            os_type=a.os_type,
            role=a.role,
            status=a.status,
            services=services,
            first_seen=a.first_seen,
            last_seen=a.last_seen
        ))
    return res
