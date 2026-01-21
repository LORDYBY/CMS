# import uuid
# from uuid import uuid4
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func

# from app.infrastructure.db.models.playlist import Playlist
# from app.infrastructure.db.models.playlist_item import PlaylistItem
# from app.infrastructure.db.models.playlist_version import PlaylistVersion
# from app.infrastructure.db.models.media import MediaAsset, ContentVersion

# class PlaylistRepository:

#     def __init__(self, session: AsyncSession):
#         self.session = session

#     # ---------------------------------------------------------
#     # PLAYLIST
#     # ---------------------------------------------------------

#     async def create_playlist(self, tenant_id: uuid.UUID, name: str):
#         playlist = Playlist(
#             id=uuid.uuid4(),
#             tenant_id=tenant_id,
#             name=name,
#         )
#         self.session.add(playlist)
#         await self.session.flush()
#         return playlist

#     async def get_playlist(self, playlist_id: uuid.UUID, tenant_id: uuid.UUID):
#         stmt = (
#             select(Playlist)
#             .where(
#                 Playlist.id == playlist_id,
#                 Playlist.tenant_id == tenant_id,
#             )
#         )
#         result = await self.session.execute(stmt)
#         return result.scalar_one_or_none()

#     # ---------------------------------------------------------
#     # PLAYLIST VERSIONS
#     # ---------------------------------------------------------

#     async def get_latest_version_number(self, playlist_id: uuid.UUID):
#         stmt = (
#             select(func.max(PlaylistVersion.version_number))
#             .where(PlaylistVersion.playlist_id == playlist_id)
#         )
#         result = await self.session.execute(stmt)
#         latest = result.scalar()
#         return latest or 0

#     async def create_playlist_version(self, tenant_id: uuid.UUID, playlist_id: uuid.UUID, version_number: int):
#         version = PlaylistVersion(
#             id=uuid.uuid4(),
#             tenant_id=tenant_id,
#             playlist_id=playlist_id,
#             version_number=version_number,
#         )
#         self.session.add(version)
#         await self.session.flush()
#         return version

#     # ---------------------------------------------------------
#     # PLAYLIST ITEMS
#     # ---------------------------------------------------------

#     async def get_last_position(self, playlist_id: uuid.UUID):
#         stmt = (
#             select(func.max(PlaylistItem.position))
#             .where(PlaylistItem.playlist_id == playlist_id)
#         )
#         result = await self.session.execute(stmt)
#         pos = result.scalar()
#         return pos or 0

#     async def add_item(
#         self,
#         tenant_id: uuid.UUID,
#         playlist_id: uuid.UUID,
#         content_version_id: uuid.UUID,
#         position: int,
#         duration_seconds: int | None,
#     ):
#         item = PlaylistItem(
#             id=uuid.uuid4(),
#             tenant_id=tenant_id,
#             playlist_id=playlist_id,
#             content_version_id=content_version_id,
#             position=position,
#             duration_seconds=duration_seconds,
#         )

#         self.session.add(item)
#         await self.session.flush()
#         return item

#     # ---------------------------------------------------------
#     # LIST ITEMS
#     # ---------------------------------------------------------

#     async def list_items(self, playlist_id: uuid.UUID):
#         stmt = (
#             select(PlaylistItem)
#             .where(PlaylistItem.playlist_id == playlist_id)
#             .order_by(PlaylistItem.position.asc())
#         )
#         result = await self.session.execute(stmt)
#         return result.scalars().all()

#     # ---------------------------------------------------------
#     # LIST Media
#     # ---------------------------------------------------------
#     async def list_items_with_media(self, playlist_id: uuid.UUID):
#         stmt = (
#             select(
#                 PlaylistItem,
#                 ContentVersion,
#                 MediaAsset,
#             )
#             .join(ContentVersion, PlaylistItem.content_version_id == ContentVersion.id)
#             .join(MediaAsset, ContentVersion.media_asset_id == MediaAsset.id)
#             .where(PlaylistItem.playlist_id == playlist_id)
#             .order_by(PlaylistItem.position.asc())
#         )

#         result = await self.session.execute(stmt)
#         rows = result.all()
#         return rows


import uuid
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.infrastructure.db.models.playlist import Playlist
from app.infrastructure.db.models.playlist_item import PlaylistItem
from app.infrastructure.db.models.playlist_version import PlaylistVersion
from app.infrastructure.db.models.media import MediaAsset, ContentVersion


class PlaylistRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------------------------------------------------
    # PLAYLIST
    # ---------------------------------------------------------

    async def create_playlist(self, tenant_id: uuid.UUID, name: str):
        playlist = Playlist(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
        )
        self.session.add(playlist)
        await self.session.flush()
        return playlist

    async def get_playlist(self, playlist_id: uuid.UUID, tenant_id: uuid.UUID):
        stmt = (
            select(Playlist)
            .where(
                Playlist.id == playlist_id,
                Playlist.tenant_id == tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ---------------------------------------------------------
    # PLAYLIST VERSIONS
    # ---------------------------------------------------------

    async def get_latest_version_number(self, playlist_id: uuid.UUID):
        stmt = (
            select(func.max(PlaylistVersion.version_number))
            .where(PlaylistVersion.playlist_id == playlist_id)
        )
        result = await self.session.execute(stmt)
        latest = result.scalar()
        return latest or 0

    async def create_playlist_version(self, tenant_id: uuid.UUID, playlist_id: uuid.UUID, version_number: int):
        version = PlaylistVersion(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            playlist_id=playlist_id,
            version_number=version_number,
        )
        self.session.add(version)
        await self.session.flush()
        return version

    async def get_published_playlist(self, playlist_id: uuid.UUID):
        """Returns the latest published playlist version."""
        stmt = (
            select(PlaylistVersion)
            .where(PlaylistVersion.playlist_id == playlist_id)
            .order_by(PlaylistVersion.version_number.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    # ---------------------------------------------------------
    # PLAYLIST ITEMS
    # ---------------------------------------------------------

    async def get_last_position(self, playlist_id: uuid.UUID):
        stmt = (
            select(func.max(PlaylistItem.position))
            .where(PlaylistItem.playlist_id == playlist_id)
        )
        result = await self.session.execute(stmt)
        pos = result.scalar()
        return pos or 0

    async def add_item(
        self,
        tenant_id: uuid.UUID,
        playlist_id: uuid.UUID,
        content_version_id: uuid.UUID,
        position: int,
        duration_seconds: int | None,
    ):
        item = PlaylistItem(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            playlist_id=playlist_id,
            content_version_id=content_version_id,
            position=position,
            duration_seconds=duration_seconds,
        )

        self.session.add(item)
        await self.session.flush()
        return item

    async def list_items(self, playlist_id: uuid.UUID):
        stmt = (
            select(PlaylistItem)
            .where(PlaylistItem.playlist_id == playlist_id)
            .order_by(PlaylistItem.position.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ---------------------------------------------------------
    # LIST ITEMS + MEDIA JOIN
    # ---------------------------------------------------------

    async def list_items_with_media(self, playlist_id: uuid.UUID):
        stmt = (
            select(
                PlaylistItem,
                ContentVersion,
                MediaAsset,
            )
            .join(ContentVersion, PlaylistItem.content_version_id == ContentVersion.id)
            .join(MediaAsset, ContentVersion.media_asset_id == MediaAsset.id)
            .where(PlaylistItem.playlist_id == playlist_id)
            .order_by(PlaylistItem.position.asc())
        )

        result = await self.session.execute(stmt)
        return result.all()