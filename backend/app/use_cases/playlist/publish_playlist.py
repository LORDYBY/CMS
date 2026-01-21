from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.playlist_repository import PlaylistRepository

class PublishPlaylistUseCase:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PlaylistRepository(session)

    async def execute(self, playlist_id: UUID, tenant_id: UUID):
        playlist = await self.repo.get_playlist(playlist_id, tenant_id)
        if not playlist:
            raise ValueError("Playlist not found")

        # get items
        items = await self.repo.list_items(playlist_id)
        if not items:
            raise ValueError("Cannot publish empty playlist")

        # compute next version number
        latest = await self.repo.get_latest_version_number(playlist_id)
        new_version = latest + 1

        # create version
        version = await self.repo.create_playlist_version(
            tenant_id=tenant_id,
            playlist_id=playlist_id,
            version_number=new_version,
        )

        await self.session.commit()

        return {
            "playlist_id": str(playlist.id),
            "published_version": new_version,
            "items": len(items)
        }