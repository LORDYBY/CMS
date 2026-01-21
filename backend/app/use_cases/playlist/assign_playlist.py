from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.playlist_assignment_repository import PlaylistAssignmentRepository


class AssignPlaylistToDeviceUseCase:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PlaylistAssignmentRepository(session)

    async def execute(self, tenant_id: UUID, device_id: UUID, playlist_id: UUID):
        assignment = await self.repo.assign_playlist(
            tenant_id=tenant_id,
            device_id=device_id,
            playlist_id=playlist_id
        )

        await self.session.commit()

        return {
            "device_id": str(device_id),
            "playlist_id": str(playlist_id),
            "assigned_at": str(assignment.assigned_at)
        }
