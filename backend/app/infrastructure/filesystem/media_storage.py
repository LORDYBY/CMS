import shutil
from pathlib import Path
from uuid import uuid4

from .paths import UPLOADS_DIR
from .checksum import sha256_file


class MediaStorage:
    @staticmethod
    def save_upload(temp_path: Path, original_filename: str) -> dict:
        extension = Path(original_filename).suffix.lower()
        media_id = uuid4()
        final_name = f"{media_id}{extension}"
        final_path = UPLOADS_DIR / final_name

        if final_path.exists():
            raise RuntimeError("Media file already exists")

        shutil.move(str(temp_path), final_path)

        checksum = sha256_file(final_path)
        size_bytes = final_path.stat().st_size

        return {
            "id": media_id,
            "filename": final_name,
            "path": str(final_path),
            "checksum": checksum,
            "size_bytes": size_bytes,
        }