from fastapi import APIRouter, Depends
from app.common.time import time
#from datetime import datetime

from app.dependencies import get_current_device
from app.infrastructure.db.session import get_db

router = APIRouter(prefix="/device/runtime", tags=["device-runtime"])


@router.post("/heartbeat")
async def heartbeat(
    device=Depends(get_current_device),
    session=Depends(get_db),
):
    device.last_seen_at = time.local_now()
    await session.commit()
    return {"status": "ok"}
