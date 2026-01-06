from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.filesystem.media_storage import MediaStorage
from app.infrastructure.db.models.media import MediaAssetModel


class UploadMediaUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, temp_path: Path, filename: str, mime_type: str):
        result = MediaStorage.save_upload(temp_path, filename)

        media = MediaAssetModel(
            id=result["id"],
            filename=result["filename"],
            mime_type=mime_type,
            checksum=result["checksum"],
            size_bytes=result["size_bytes"],
        )

        self.session.add(media)
        await self.session.commit()

        return {
            "id": str(media.id),
            "filename": media.filename,
            "url": f"http://localhost:8080/uploads/{media.filename}",
            "checksum": media.checksum,
            "size_bytes": media.size_bytes,
        }
