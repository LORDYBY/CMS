# app/use_cases/devices/revoke_device.py
from app.common.time import time
from app.infrastructure.db.models.device import Device


class RevokeDeviceUseCase:

    def __init__(self, session):
        self.session = session

    async def execute(self, device_id):
        device = await self.session.get(Device, device_id)

        if not device:
            return None

        device.state = "REVOKED"
        device.revoked_at = time.local_now()
        device.token_hash = None

        await self.session.commit()
        return device
