# import uuid
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.infrastructure.db.repositories.media_repository import MediaRepository

# class ApproveVersionUseCase:

#     def __init__(self, session: AsyncSession):
#         self.session = session
#         self.repo = MediaRepository()

#     async def execute(self, media_id: uuid.UUID, version_number: int, approver_id: uuid.UUID):

#         version = await self.repo.approve_version(
#             session=self.session,
#             media_id=media_id,
#             version_number=version_number,
#             approver_id=approver_id
#         )

#         if not version:
#             raise ValueError("Version not found")

#         await self.session.commit()

#         return {
#             "media_id": str(media_id),
#             "version": version_number,
#             "state": "APPROVED",
#         }

import uuid
from app.infrastructure.db.repositories.media_repository import MediaRepository


class ApproveVersionUseCase:

    def __init__(self, session):
        self.session = session
        self.repo = MediaRepository(session)

    async def execute(self, media_id: uuid.UUID, version_number: int, approver_id: uuid.UUID):
        version = await self.repo.approve_version(
            media_id=media_id,
            version_number=version_number,
            approver_id=approver_id
        )

        if version is None:
            return {"error": "Version not found"}

        await self.repo.commit()

        return {
            "media_id": str(media_id),
            "approved_version": version_number,
            "state": version.state.value,
        }
