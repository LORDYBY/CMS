# import uuid
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.infrastructure.db.repositories.playlist_repository import PlaylistRepository


# class CreatePlaylistUseCase:

#     def __init__(self, session: AsyncSession):

#         self.session = session
#         self.repo = PlaylistRepository()

#     async def execute(self, tenant_id: uuid.UUID, name: str, created_by: uuid.UUID):

#         # 1. Create playlist
#         playlist = await self.repo.create_playlist(
#             session=self.session,
#             tenant_id=tenant_id,
#             name=name,
#         )

#         # 2. Create initial playlist version (version 1)
#         playlist_version = await self.repo.create_playlist_version(
#             session=self.session,
#             tenant_id=tenant_id,
#             playlist_id=playlist.id,
#         )

#         # 3. Commit
#         await self.session.commit()

#         return {
#             "playlist_id": str(playlist.id),
#             "name": playlist.name,
#             "version": playlist_version.version_number,
#             "created_at": playlist.created_at,
#         }
###########################################

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.playlist_repository import PlaylistRepository


class CreatePlaylistUseCase:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PlaylistRepository(session)

    async def execute(self, tenant_id: uuid.UUID, name: str, created_by: uuid.UUID):

        # 1. Create playlist
        playlist = await self.repo.create_playlist(
            tenant_id=tenant_id,
            name=name,
        )

        # 2. Determine next version (initial = 1)
        version_number = 1

        playlist_version = await self.repo.create_playlist_version(
            tenant_id=tenant_id,
            playlist_id=playlist.id,
            version_number=version_number,
        )

        # 3. Commit
        await self.session.commit()

        return {
            "playlist_id": str(playlist.id),
            "name": playlist.name,
            "version": playlist_version.version_number,
            "created_at": playlist.created_at,
        }
