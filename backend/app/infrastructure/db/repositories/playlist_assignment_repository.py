import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.device_playlist_assignment import DevicePlaylistAssignment


class PlaylistAssignmentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def assign_playlist(self, tenant_id, device_id, playlist_id):
        # check for existing assignment
        stmt = (
            select(DevicePlaylistAssignment)
            .where(DevicePlaylistAssignment.device_id == device_id)
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # overwrite existing assignment
            existing.playlist_id = playlist_id
            await self.session.flush()
            return existing

        # create new assignment
        assignment = DevicePlaylistAssignment(
            tenant_id=tenant_id,
            device_id=device_id,
            playlist_id=playlist_id,
        )

        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def get_playlist_for_device(self, device_id):
        stmt = (
            select(DevicePlaylistAssignment)
            .where(DevicePlaylistAssignment.device_id == device_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()