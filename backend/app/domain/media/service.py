from pathlib import Path
from app.infrastructure.filesystem.checksum import compute_checksum


class MediaDomainService:
    """
    Pure domain logic: no DB, no filesystem.
    """

    @staticmethod
    async def extract_file_info(upload_file):
        data = await upload_file.read()
        filename = upload_file.filename
        ext = Path(filename).suffix
        mime = upload_file.content_type
        size_bytes = len(data)
        checksum = compute_checksum(data)
        return data, filename, mime, size_bytes, checksum, ext
