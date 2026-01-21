# app/use_cases/devices/device_activation_service.py
import secrets
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.device_tokens import generate_device_token, hash_device_token
from app.infrastructure.db.models.device import Device


@dataclass
class DeviceActivationService:
    session: AsyncSession

    async def activate(self, device_id: str):
        device = await self.session.get(Device, device_id)

        if not device:
            raise ValueError("Device not found")

        # Device must be approved before activation
        if device.state != "ACTIVE":
            return {
                "state": device.state,
                "device_id": str(device.id)
            }

        # Generate raw token for first activation only
        raw_token = generate_device_token()

        # Hash using SAME method used during WebSocket validation
        device.token_hash = hash_device_token(raw_token)

        await self.session.commit()

        return {
            "state": "ACTIVE",
            "device_id": str(device.id),
            "token": raw_token
        }
