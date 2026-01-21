# import uuid
# from sqlalchemy import select, func
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.infrastructure.db.models.media import MediaAsset, ContentVersion
# from uuid import uuid4
# from app.infrastructure.db.models.enums import ContentState


# class MediaRepository:

#     async def get_media_by_id(self, session: AsyncSession, media_id):
#         stmt = select(MediaAsset).where(MediaAsset.id == media_id)
#         result = await session.execute(stmt)
#         return result.scalar_one_or_none()

#     async def create_media_asset(self, session: AsyncSession, tenant_id, filename, mime_type, size_bytes, checksum):
#         asset = MediaAsset(
#             id=uuid4(),
#             tenant_id=tenant_id,
#             filename=filename,
#             mime_type=mime_type,
#             size_bytes=size_bytes,
#             checksum=checksum,
#         )
#         session.add(asset)
#         await session.flush()
#         return asset

#     async def create_content_version(self, session: AsyncSession, tenant_id, media_asset_id, version_number, created_by):
#         version = ContentVersion(
#             id=uuid4(),
#             tenant_id=tenant_id,
#             media_asset_id=media_asset_id,
#             version_number=version_number,
#             created_by=created_by,
#         )
#         session.add(version)
#         await session.flush()
#         return version

#     async def get_latest_version(self, session: AsyncSession, media_id):
#         print(">>> Looking for versions of:", media_id)

#         stmt = select(func.max(ContentVersion.version_number)).where(
#             ContentVersion.media_asset_id == media_id
#         )

#         result = await session.execute(stmt)
#         latest = result.scalar()

#         print(">>> FOUND LATEST VERSION:", latest)

#         return latest or 0
    

#     async def approve_version(self, session: AsyncSession, media_id, version_number, approver_id):
#         # Unapprove all existing versions
#         stmt_unapprove = (
#             select(ContentVersion)
#             .where(ContentVersion.media_asset_id == media_id)
#         )
#         result = await session.execute(stmt_unapprove)
#         all_versions = result.scalars().all()

#         for v in all_versions:
#             v.state = ContentState.DRAFT

#         # Approve selected version
#         stmt = (
#             select(ContentVersion)
#             .where(
#                 ContentVersion.media_asset_id == media_id,
#                 ContentVersion.version_number == version_number
#             )
#         )
#         result2 = await session.execute(stmt)
#         version = result2.scalar_one_or_none()

#         if not version:
#             return None

#         version.state = ContentState.APPROVED
#         version.approved_at = func.now()
#         version.created_by = approver_id

#         await session.flush()
#         return version


#     async def commit(self, session: AsyncSession):
#         await session.commit()


import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.media import MediaAsset, ContentVersion
from app.infrastructure.db.models.enums import ContentState


class MediaRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------------------------------------------------
    # MEDIA ASSET
    # ---------------------------------------------------------

    async def get_media_by_id(self, media_id: uuid.UUID):
        stmt = select(MediaAsset).where(MediaAsset.id == media_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_media_asset(self, tenant_id, filename, mime_type, size_bytes, checksum):
        asset = MediaAsset(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            filename=filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum=checksum,
        )
        self.session.add(asset)
        await self.session.flush()
        return asset

    # ---------------------------------------------------------
    # CONTENT VERSIONS
    # ---------------------------------------------------------

    async def get_content_version(self, version_id: uuid.UUID):
        stmt = select(ContentVersion).where(ContentVersion.id == version_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_version(self, media_id: uuid.UUID):
        stmt = (
            select(func.max(ContentVersion.version_number))
            .where(ContentVersion.media_asset_id == media_id)
        )
        result = await self.session.execute(stmt)
        latest = result.scalar()
        return latest or 0

    async def create_content_version(self, tenant_id, media_asset_id, version_number, created_by):
        version = ContentVersion(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            media_asset_id=media_asset_id,
            version_number=version_number,
            created_by=created_by,
        )
        self.session.add(version)
        await self.session.flush()
        return version

    # ---------------------------------------------------------
    # APPROVAL WORKFLOW
    # ---------------------------------------------------------

    async def approve_version(self, media_id, version_number, approver_id):
        # reset all versions
        stmt_unapprove = (
            select(ContentVersion)
            .where(ContentVersion.media_asset_id == media_id)
        )
        result = await self.session.execute(stmt_unapprove)
        all_versions = result.scalars().all()

        for v in all_versions:
            v.state = ContentState.DRAFT

        # approve the selected one
        stmt = (
            select(ContentVersion)
            .where(
                ContentVersion.media_asset_id == media_id,
                ContentVersion.version_number == version_number,
            )
        )
        result2 = await self.session.execute(stmt)
        version = result2.scalar_one_or_none()

        if not version:
            return None

        version.state = ContentState.APPROVED
        version.approved_at = func.now()
        version.created_by = approver_id

        await self.session.flush()
        return version

    # ---------------------------------------------------------
    # COMMIT
    # ---------------------------------------------------------

    async def commit(self):
        await self.session.commit()
