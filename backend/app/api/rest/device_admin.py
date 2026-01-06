# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from datetime import datetime

# from app.dependencies import get_current_user
# from app.infrastructure.db.session import get_db
# from app.infrastructure.db.models.device import Device
# from app.common.device_tokens import generate_device_token, hash_device_token
# from app.api.schemas.device_admin import DeviceApproveRequest

# router = APIRouter(prefix="/admin/devices", tags=["devices-admin"])


# @router.post("/{device_id}/approve")
# async def approve_device(
#     device_id: str,
#     payload: DeviceApproveRequest,
#     session: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     result = await session.execute(
#         select(Device).where(Device.id == device_id)
#     )
#     device = result.scalar_one_or_none()

#     if not device or device.state != "PENDING":
#         raise HTTPException(status_code=404, detail="Device not found or invalid state")

#     token = generate_device_token()

#     device.tenant_id = payload.tenant_id
#     device.name = payload.name
#     device.state = "ACTIVE"
#     device.token_hash = hash_device_token(token)
#     device.approved_at = datetime.utcnow()

#     await session.commit()

#     return {
#         "device_id": str(device.id),
#         "token": token
#     }


###################
# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from datetime import datetime

# from app.dependencies import get_current_user
# from app.infrastructure.db.session import get_db
# from app.infrastructure.db.models.device import Device
# from app.common.device_tokens import generate_device_token, hash_device_token
# from app.api.schemas.device_admin import DeviceApproveRequest

# router = APIRouter(prefix="/admin/devices", tags=["devices-admin"])


# @router.post("/{device_id}/approve")
# async def approve_device(
#     device_id: str,
#     payload: DeviceApproveRequest,
#     request: Request,  # 👈 ADD THIS
#     session: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     #print("AUTH HEADER:", request.headers.get("authorization"))  # 👈 ADD THIS

#     result = await session.execute(
#         select(Device).where(Device.id == device_id)
#     )
#     device = result.scalar_one_or_none()

#     if not device or device.state != "PENDING":
#         raise HTTPException(status_code=404, detail="Device not found or invalid state")

#     token = generate_device_token()

#     device.tenant_id = payload.tenant_id
#     device.name = payload.name
#     device.state = "ACTIVE"
#     device.token_hash = hash_device_token(token)
#     device.approved_at = datetime.utcnow()

#     await session.commit()

#     return {
#         "device_id": str(device.id),
#         "token": token
#     }


from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.dependencies import get_current_user
from app.infrastructure.db.session import get_db
from app.infrastructure.db.models.device import Device
from app.common.device_tokens import generate_device_token, hash_device_token
from app.api.schemas.device_admin import DeviceApproveRequest

router = APIRouter(prefix="/admin/devices", tags=["devices-admin"])


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
        raise HTTPException(status_code=404, detail="Device not found or invalid state")

    token = generate_device_token()

    device.tenant_id = payload.tenant_id
    device.name = payload.name
    device.state = "ACTIVE"
    device.token_hash = hash_device_token(token)
    device.approved_at = datetime.now(timezone.utc)  # ✅ FIXED

    await session.commit()

    return {
        "device_id": str(device.id),
        "token": token
    }
