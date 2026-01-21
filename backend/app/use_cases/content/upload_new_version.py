# import uuid
# from pathlib import Path
# from fastapi import UploadFile
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.infrastructure.db.repositories.media_repository import MediaRepository
# from app.infrastructure.filesystem.media_storage import FileStorage
# from app.infrastructure.filesystem.checksum import compute_checksum


# class UploadNewVersionUseCase:

#     def __init__(self, session: AsyncSession):
#         self.session = session
#         #self.repo = MediaRepository()
#         self.repo = MediaRepository(session)
#         self.storage = FileStorage()

#     async def execute(self, media_id: uuid.UUID, file: UploadFile, user_id: uuid.UUID):
#         # 1. Load asset
#         asset = await self.repo.get_media_by_id(self.session, media_id)
#         if not asset:
#             raise ValueError("Media not found")

#         # 2. Read file
#         data = await file.read()
#         checksum = compute_checksum(data)
#         size_bytes = len(data)
#         ext = Path(file.filename).suffix

#         # 3. Get next version number
#         latest = await self.repo.get_latest_version(self.session, media_id)
#         new_version = latest + 1

#         # 4. Save file physically
#         saved_file = self.storage.save_version(
#             tenant_id=asset.tenant_id,
#             media_id=asset.id,
#             version_number=new_version,
#             filename=file.filename,
#             data=data,
#         )

#         # 5. Insert version row
#         version = await self.repo.create_content_version(
#             self.session,
#             tenant_id=asset.tenant_id,
#             media_asset_id=asset.id,
#             version_number=new_version,
#             created_by=user_id,
#         )

#         # 6. Update asset metadata
#         asset.size_bytes = size_bytes
#         asset.checksum = checksum
#         asset.filename = file.filename

#         # 7. Commit
#         await self.session.commit()

#         return {
#             "media_id": str(asset.id),
#             "new_version": new_version,
#             "filename": file.filename,
#             "path": str(saved_file),
#         }
#         ## must resturns :: http://localhost:8080/media/tenants/<tenant>/media/<id>/v2/file.mp4

##############################

import uuid
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.media_repository import MediaRepository
from app.infrastructure.filesystem.media_storage import FileStorage
from app.infrastructure.filesystem.checksum import compute_checksum
from app.settings import settings


class UploadNewVersionUseCase:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MediaRepository(session)   # ✅ FIXED
        self.storage = FileStorage()

    async def execute(self, media_id: uuid.UUID, file: UploadFile, user_id: uuid.UUID):
        # 1) Load asset
        asset = await self.repo.get_media_by_id(media_id)
        if not asset:
            raise ValueError("Media not found")

        # 2) Read uploaded file
        data = await file.read()
        checksum = compute_checksum(data)
        size_bytes = len(data)
        ext = Path(file.filename).suffix

        # 3) Next version number
        latest = await self.repo.get_latest_version(media_id)
        new_version = latest + 1

        # 4) Save file physically
        saved_file = self.storage.save_version(
            tenant_id=asset.tenant_id,
            media_id=asset.id,
            version_number=new_version,
            filename=file.filename,
            data=data,
        )

        # 5) Insert version row in DB
        version = await self.repo.create_content_version(
            tenant_id=asset.tenant_id,
            media_asset_id=asset.id,
            version_number=new_version,
            created_by=user_id,
        )

        # 6) Update asset (metadata of the last uploaded file)
        asset.size_bytes = size_bytes
        asset.checksum = checksum
        asset.filename = file.filename

        # 7) Commit once
        await self.session.commit()

        # 8) Generate PUBLIC URL
        public_url = (
            f"{settings.MEDIA_PUBLIC_BASE_URL}/media/tenants/"
            f"{asset.tenant_id}/media/{asset.id}/v{new_version}/{file.filename}"
        )

        return {
            "media_id": str(asset.id),
            "new_version": new_version,
            "filename": file.filename,
            "path": public_url,
        }
