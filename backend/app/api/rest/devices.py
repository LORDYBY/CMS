from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.db.session import get_db
from app.infrastructure.db.models.device import Device
from app.api.schemas.device import (
    DeviceRegisterRequest,
    DeviceRegisterResponse
)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceRegisterResponse)
async def register_device(
    payload: DeviceRegisterRequest,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Device).where(Device.fingerprint == payload.fingerprint)
    )
    device = result.scalar_one_or_none()

    if not device:
        device = Device(fingerprint=payload.fingerprint)
        session.add(device)
        await session.commit()
        await session.refresh(device)

    return DeviceRegisterResponse(
        device_id=str(device.id),
        state=device.state
    )
