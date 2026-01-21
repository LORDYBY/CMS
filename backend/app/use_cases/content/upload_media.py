# from pathlib import Path

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.infrastructure.filesystem.media_storage import MediaStorage
# from app.infrastructure.db.models.media import MediaAsset


# class UploadMediaUseCase:
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def execute(self, temp_path: Path, filename: str, mime_type: str):
#         result = MediaStorage.save_upload(temp_path, filename)

#         media = MediaAsset(
#             id=result["id"],
#             filename=result["filename"],
#             mime_type=mime_type,
#             checksum=result["checksum"],
#             size_bytes=result["size_bytes"],
#         )

#         self.session.add(media)
#         await self.session.commit()

#         return {
#             "id": str(media.id),
#             "filename": media.filename,
#             "url": f"http://localhost:8080/uploads/{media.filename}",
#             "checksum": media.checksum,
#             "size_bytes": media.size_bytes,
#         }

#############################################################################


# from app.domain.media.service import MediaDomainService
# from app.infrastructure.db.repositories.media_repository import MediaRepository
# from app.infrastructure.filesystem.media_storage import FileStorage


# class UploadMediaUseCase:

#     def __init__(self, repository: MediaRepository, file_storage: FileStorage):
#         self.repository = repository
#         self.file_storage = file_storage

#     async def execute(self, session, tenant_id, created_by, file):
#         # 1. Extract domain info
#         data, filename, mime, size_bytes, checksum, ext = \
#             await MediaDomainService.extract_file_info(file)

#         # 2. Create media asset (DB)
#         asset = await self.repository.create_media_asset(
#             session=session,
#             tenant_id=tenant_id,
#             filename=filename,
#             mime_type=mime,
#             size_bytes=size_bytes,
#             checksum=checksum,
#         )

#         # 3. Save physical file (Filesystem)
#         self.file_storage.save_version(
#             tenant_id=tenant_id,
#             media_id=asset.id,
#             version_number=1,
#             filename=filename,
#             data=data,
#         )

#         # 4. Create ContentVersion v1
#         version = await self.repository.create_content_version(
#             session=session,
#             tenant_id=tenant_id,
#             media_asset_id=asset.id,
#             version_number=1,
#             created_by=created_by,
#         )

#         # 5. Commit once
#         await self.repository.commit(session)

#         return {
#             "media_id": str(asset.id),
#             "filename": filename,
#             "mime_type": mime,
#             "size_bytes": size_bytes,
#             "checksum": checksum,
#             "version": version.version_number,
#             "path": f"/media/tenants/{tenant_id}/media/{asset.id}/v1/{filename}"
#         }


from app.domain.media.service import MediaDomainService
from app.infrastructure.db.repositories.media_repository import MediaRepository
from app.infrastructure.filesystem.media_storage import FileStorage


class UploadMediaUseCase:

    def __init__(self, repository: MediaRepository, file_storage: FileStorage):
        self.repository = repository
        self.file_storage = file_storage

    async def execute(self, tenant_id, created_by, file):
        # 1. Extract domain info
        data, filename, mime, size_bytes, checksum, ext = \
            await MediaDomainService.extract_file_info(file)

        # 2. Create media asset (DB)
        asset = await self.repository.create_media_asset(
            tenant_id=tenant_id,
            filename=filename,
            mime_type=mime,
            size_bytes=size_bytes,
            checksum=checksum,
        )

        # 3. Save physical file (Filesystem)
        self.file_storage.save_version(
            tenant_id=tenant_id,
            media_id=asset.id,
            version_number=1,
            filename=filename,
            data=data,
        )

        # 4. Create ContentVersion v1
        version = await self.repository.create_content_version(
            tenant_id=tenant_id,
            media_asset_id=asset.id,
            version_number=1,
            created_by=created_by,
        )

        # 5. Commit once
        await self.repository.commit()

        return {
            "media_id": str(asset.id),
            "filename": filename,
            "mime_type": mime,
            "size_bytes": size_bytes,
            "checksum": checksum,
            "version": version.version_number,
            "path": f"/media/tenants/{tenant_id}/media/{asset.id}/v1/{filename}"
        }
