from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.device_heartbeat_repository import DeviceHeartbeatRepository


@dataclass
class DeviceHeartbeatService:
    repo: DeviceHeartbeatRepository

    async def record(
        self,
        session: AsyncSession,
        tenant_id: str,
        device_id: str,
    ):
        return await self.repo.save_heartbeat(
            session,
            tenant_id,
            device_id,
        )

    async def status(
        self,
        session: AsyncSession,
        tenant_id: str,
        device_id: str,
    ):
        last = await self.repo.get_last_heartbeat(session, tenant_id, device_id)

        if not last:
            return {
                "online": False,
                "last_seen": None,
            }

        online = await self.repo.is_device_online(session, tenant_id, device_id)

        return {
            "online": online,
            "last_seen": last.heartbeat_at.isoformat(),
        }
