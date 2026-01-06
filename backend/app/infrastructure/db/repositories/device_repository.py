from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.db.models.device import Device

class DeviceRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_fingerprint(self, fingerprint: str):
        result = await self.session.execute(
            select(Device).where(Device.fingerprint == fingerprint)
        )
        return result.scalar_one_or_none()

    async def save(self, device: Device):
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device
