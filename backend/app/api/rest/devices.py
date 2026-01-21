from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import json


from datetime import datetime, timezone
from app.common.time import time
from app.dependencies import get_current_user
import app.infrastructure.redis.client as redis_client

from app.api.schemas.device import (
    DeviceRegisterRequest,
    DeviceRegisterResponse
)
from app.api.schemas.device_commands import DeviceCommand

from app.infrastructure.db.session import get_db
from app.infrastructure.db.models.device import Device

from app.use_cases.playlist.assign_playlist import AssignPlaylistToDeviceUseCase
from app.use_cases.playlist.device_fetch_playlist import DeviceFetchPlaylistUseCase

from app.use_cases.devices.device_heartbeat_service import DeviceHeartbeatService
from app.infrastructure.db.repositories.device_heartbeat_repository import DeviceHeartbeatRepository
from app.common.device_tokens import generate_device_token, hash_device_token
from app.api.schemas.device_admin import DeviceApproveRequest
from app.use_cases.devices.device_activation_service import DeviceActivationService
from app.domain.entities import device
from app.common.device_commands import DeviceCommandEnum
from app.use_cases.devices.remove_device_playlist import RemoveDevicePlaylistUseCase
from app.use_cases.devices.revoke_device import RevokeDeviceUseCase
from app.use_cases.devices.delete_device import DeleteDeviceUseCase
from app.use_cases.devices.register_device import RegisterDeviceUseCase

router = APIRouter(prefix="/devices", tags=["devices"])


# ================================================================
# 1. DEVICE REGISTRATION
# ================================================================


@router.post("/register", response_model=DeviceRegisterResponse)
async def register_device(
    payload: DeviceRegisterRequest,
    session: AsyncSession = Depends(get_db),
):
    use_case = RegisterDeviceUseCase(session)
    return await use_case.execute(payload.fingerprint)

# ================================================================
# 2. ADMIN: LIST DEVICES
# ================================================================
@router.get("/")
async def list_devices(
    session: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)  # make sure admin
):
    result = await session.execute(select(Device))
    devices = result.scalars().all()

    return [
        {
            "id": str(d.id),
            "fingerprint": d.fingerprint,
            "state": d.state,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in devices
    ]


# ================================================================
# 3. ADMIN: APPROVE DEVICE
# ================================================================

@router.post("/{device_id}/approve")
async def approve_device(
    device_id: str,
    payload: DeviceApproveRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await session.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()

    if not device or device.state != "PENDING":
        raise HTTPException(
            status_code=404,
            detail="Device not found or invalid state"
        )

    device.tenant_id = payload.tenant_id
    device.name = payload.name
    device.state = "APPROVED"  # or ACTIVE if you want single-step
    device.approved_at = time.local_now()

    await session.commit()

    return {
        "device_id": str(device.id),
        "state": device.state
    }
# ================================================================
# 4. ADMIN: ASSIGN PLAYLIST TO DEVICE
# ================================================================
@router.post("/{device_id}/assign-playlist/{playlist_id}")
async def assign_playlist_to_device(
    device_id: UUID,
    playlist_id: UUID,
    user = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    use_case = AssignPlaylistToDeviceUseCase(session)

    result = await use_case.execute(
        tenant_id=user.tenant_id,
        device_id=device_id,
        playlist_id=playlist_id
    )

    # notify device
    await redis_client.redis.publish(
        f"device:commands:{device_id}",
        json.dumps({"type": "reload_playlist"})
    )

    return result

# ================================================================
# 5. DEVICE: FETCH PLAYLIST
# ================================================================
@router.get("/{device_id}/playback")
async def get_device_playback(
    device_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    use_case = DeviceFetchPlaylistUseCase(session)
    return await use_case.execute(device_id=device_id, request=request)


# ================================================================
# 6. DEVICE HEARTBEAT
# ================================================================
@router.post("/{device_id}/heartbeat")
async def send_heartbeat(
    device_id: UUID,
    user = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = DeviceHeartbeatService(DeviceHeartbeatRepository())

    hb = await service.record(
        session=session,
        tenant_id=user.tenant_id,
        device_id=device_id,
    )

    return {
        "status": "ok",
        "heartbeat_at": hb.heartbeat_at.isoformat()
    }


# ================================================================
# 7. DEVICE STATUS (ONLINE / OFFLINE)
# ================================================================
@router.get("/{device_id}/status")
async def get_status(
    device_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    # No admin authentication here

    result = await session.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()

    if not device:
        return { "state": "NOT_FOUND" }

    return {
        "device_id": str(device.id),
        "state": device.state
    }


# ================================================================
# 8. ADMIN → SEND COMMAND TO DEVICE (WS PUSH)
# ================================================================

@router.post("/{device_id}/command")
async def send_command_to_device(
    device_id: str,
    command: DeviceCommand,
    user = Depends(get_current_user),   # ensure admin
):
    message = {
        "type": command.type,           # ✅ IMPORTANT
        "payload": command.payload or {}
    }

    await redis_client.redis.publish(
        f"device:commands:{device_id}",
        json.dumps(message)
    )

    return {
        "status": "sent",
        "device_id": device_id,
        "command": message
    }

# ================================================================
# 9. DEVICE ACTIVATION (polling from boot.js)
# ================================================================


@router.post("/{device_id}/activate")
async def activate_device(
    device_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    device = await session.get(Device, device_id)

    if not device:
        raise HTTPException(404, "Device not found")

    if device.state != "ACTIVE":
        return { "state": device.state, "device_id": str(device.id) }

    return {
        "state": "ACTIVE",
        "device_id": str(device.id)
    }

# ================================================================
# 10. ADMIN: REMOVE PLAYLIST FROM DEVICE
# ================================================================


@router.delete("/{device_id}/playlist")
async def remove_playlist(
    device_id: UUID,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    use_case = RemoveDevicePlaylistUseCase(session)
    await use_case.execute(device_id)

    await redis_client.redis.publish(
        f"device:commands:{device_id}",
        json.dumps({"type": "reload_playlist"})
    )

    return {"status": "playlist_removed"}

# ================================================================
# 11. ADMIN: REVOKE DEVICE
# ================================================================


@router.post("/{device_id}/revoke")
async def revoke_device(
    device_id: UUID,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    use_case = RevokeDeviceUseCase(session)
    device = await use_case.execute(device_id)

    if device:
        await redis_client.redis.publish(
            f"device:commands:{device_id}",
            json.dumps({"type": "revoke"})
        )

    return {"status": "revoked"}

# ================================================================
# 12. ADMIN: DELETE DEVICE
# ================================================================

@router.delete("/{device_id}")
async def delete_device(
    device_id: UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    use_case = DeleteDeviceUseCase(session)
    await use_case.execute(device_id)

    return { "status": "deleted" }




############################################################

# End of File===================================================
