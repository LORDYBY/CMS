import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.playlist_repository import PlaylistRepository
from app.infrastructure.db.repositories.media_repository import MediaRepository
from app.infrastructure.db.models.enums import ContentState


class AddPlaylistItemUseCase:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.playlists = PlaylistRepository(session)
        self.media = MediaRepository(session)

    async def execute(self, tenant_id, playlist_id, content_version_id, duration_seconds):
        # 1) Validate playlist
        playlist = await self.playlists.get_playlist(playlist_id, tenant_id)
        if not playlist:
            raise ValueError("Playlist not found")

        # 2) Validate version
        version = await self.media.get_content_version(content_version_id)
        if not version:
            raise ValueError("Content version not found")

        if version.state != ContentState.APPROVED:
            raise ValueError("Content version must be APPROVED")

        # 3) Determine next position
        last_position = await self.playlists.get_last_position(playlist_id)
        position = (last_position or 0) + 1

        # 4) Insert
        item = await self.playlists.add_item(
            tenant_id=tenant_id,
            playlist_id=playlist_id,
            content_version_id=content_version_id,
            position=position,
            duration_seconds=duration_seconds
        )

        await self.session.commit()

        return {
            "playlist_id": str(playlist_id),
            "item_id": str(item.id),
            "content_version_id": str(content_version_id),
            "position": position,
            "duration_seconds": duration_seconds
        }
