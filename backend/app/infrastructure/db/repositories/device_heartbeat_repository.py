from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models import DeviceHeartbeat


class DeviceHeartbeatRepository:

    async def save_heartbeat(
        self,
        session: AsyncSession,
        tenant_id: str,
        device_id: str,
    ):
        hb = DeviceHeartbeat(
            tenant_id=tenant_id,
            device_id=device_id,
        )
        session.add(hb)
        await session.commit()
        await session.refresh(hb)
        return hb

    async def get_last_heartbeat(
        self,
        session: AsyncSession,
        tenant_id: str,
        device_id: str,
    ):
        query = (
            select(DeviceHeartbeat)
            .where(DeviceHeartbeat.device_id == device_id)
            .where(DeviceHeartbeat.tenant_id == tenant_id)
            .order_by(DeviceHeartbeat.heartbeat_at.desc())
            .limit(1)
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def is_device_online(
        self,
        session: AsyncSession,
        tenant_id: str,
        device_id: str,
    ):
        last = await self.get_last_heartbeat(session, tenant_id, device_id)
        if not last:
            return False

        now = datetime.now(timezone.utc)
        diff = now - last.heartbeat_at

        return diff.total_seconds() < 30